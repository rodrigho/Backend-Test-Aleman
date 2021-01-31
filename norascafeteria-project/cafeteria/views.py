import logging

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import now, localtime

from .forms import DishForm, MenuForm, OrderForm
from .models import Dish, User, Menu, Order
from .slackapi import send_async_notification


# This retrieves a Python logging instance (or creates it)
logger = logging.getLogger(__name__)


def home(request):
    date = localtime(now()).date()
    menu = None
    try:
        menu = Menu.objects.get(date=date)
        logger.info(f'Menu uuid: {menu.uuid}')
    except Exception as e:
        logger.error(f"Error: {e}")

    is_authenticated = False
    is_admin = False

    if request.user.is_authenticated:
        logger.info('User authenticated')
        is_authenticated = True

        role = request.user.role.lower()
        if role == 'admin':
            is_admin = True

    return render(request, 'cafeteria/home.html', {
        'menu': menu,
        'is_authenticated': is_authenticated,
        'is_admin': is_admin
    })


@login_required
def dish_form(request):
    role = request.user.role.lower()
    if role != 'admin':
        return home(request)

    form = DishForm()
    all_dishes = Dish.objects.all()
    if request.method == 'POST':
        filled_form = DishForm(request.POST)
        if filled_form.is_valid():
            created_dish = filled_form.save()
            created_dish_pk = created_dish.id
            note = 'Dish %s was added!' % filled_form.cleaned_data['name']
            filled_form = DishForm()
        else:
            created_dish_pk = None
            note = 'Dish was not inserted, please try again'
        return render(request, 'cafeteria/dish_form.html', {
            'created_dish_pk': created_dish_pk,
            'dish_form': filled_form,
            'note': note,
            'all_dishes': all_dishes
        })
    return render(request, 'cafeteria/dish_form.html', {'dish_form': form, 'all_dishes': all_dishes})


# Admin
# This is managed by Nora
@login_required
def edit_dish(request, pk):
    role = request.user.role.lower()
    if role != 'admin':
        return render(request, 'cafeteria/home.html')

    #dish = Dish.objects.get(pk=pk)
    dish = get_object_or_404(Dish, pk=pk)
    form = DishForm(instance=dish)
    if request.method == 'POST':
        filled_form = DishForm(request.POST, instance=dish)
        if filled_form.is_valid():
            filled_form.save()
            form = filled_form
            note = 'Dish was edited successfully!'
        else:
            note = 'Dish was not updated, please try again'
        return render(request, 'cafeteria/edit_dish.html', {'dish_form': form, 'dish': dish, 'note': note})
    return render(request, 'cafeteria/edit_dish.html', {'dish_form': form, 'dish': dish})


@login_required
def menu_form(request):
    role = request.user.role.lower()
    if role != 'admin':
        return home(request)

    form = MenuForm()
    date = localtime(now()).date()
    menu = None
    note = None
    have_errors = False

    try:
        menu = Menu.objects.get(date=date)
        note = "Today's menu is ready"
        if menu.notification_sent:
            note = "Employees has been notified with today's menu"

        # Send async slack notification
        if request.method == 'GET' and request.GET.get('slack'):
            send_async_notification(f"{menu.detail}:\nhttp://localhost:8000/menu/{menu.uuid}")
            menu.notification_sent = True
            menu.save()
            return redirect(menu_form)

    except ObjectDoesNotExist as e:
        pass
    except MultipleObjectsReturned as e:
        note = 'There are more than one menu, please contact support team'
        have_errors = True
        pass

    if request.method == 'POST':
        form = MenuForm(request.POST)
        # Create a new menu
        if form.is_valid():
            menu = form.save()
            date = menu.date
            note = f'Menu has been created for {date}!'
        else:
            note = f'Menu could not be added, please try again!'
            have_errors = True
        # Clean fields
        form = MenuForm()
    return render(request, 'cafeteria/menu_form.html', {
        'menu_form': form,
        'date': date,
        'note': note,
        'menu': menu,
        'have_errors': have_errors
    })


@login_required
def edit_menu(request, pk):
    role = request.user.role.lower()
    if role != 'admin':
        return render(request, 'cafeteria/home.html')

    #menu = Menu.objects.get(pk=pk)
    menu = get_object_or_404(Menu, pk=pk)
    form = MenuForm(instance=menu)
    if request.method == 'POST':
        menu.notification_sent = False
        filled_form = MenuForm(request.POST, instance=menu)
        if filled_form.is_valid():
            filled_form.save()
            form = filled_form
            note = 'Menu was edited successfully!'
        else:
            note = 'Menu was not updated, please try again'
        return render(request, 'cafeteria/edit_menu.html', {'menu_form': form, 'menu': menu, 'note': note})
    return render(request, 'cafeteria/edit_menu.html', {'menu_form': form, 'menu': menu})



@login_required
def see_orders(request):
    role = request.user.role.lower()
    if role != 'admin':
        return home(request)

    date = localtime(now()).date()
    orders = None
    if request.method == 'GET':
        try:
            orders = Order.objects.filter(created_at=date.strftime("%Y-%m-%d"))
        except Exception as e:
            logger.error(f"Error: {e}")
    return render(request, 'cafeteria/orders.html', {'orders': orders})


# Employee content
# Here are all the views that are allowed to the employee
def allow_order(allow_hour):
    datetime = localtime(now())
    return datetime.hour < allow_hour


@login_required
def redirect_uuid(request):
    date = localtime(now()).date()
    pk = 'null'
    try:
        menu = Menu.objects.get(date=date)
        pk = menu.uuid
    except ObjectDoesNotExist as e:
        pass
    except MultipleObjectsReturned as e:
        pass
    return redirect(order_uuid, pk)


@login_required
def order_uuid(request, pk):
    username = request.user.username
    user = User.objects.get(username=username)

    menu = None
    try:
        #menu = Menu.objects.get(uuid=pk)
        menu = get_object_or_404(Menu, pk=pk)
    except ObjectDoesNotExist as e:
        pass
    except MultipleObjectsReturned as e:
        pass
    return order(request, user, menu, pk)


def order(request, user, menu, pk):
    form = OrderForm()
    _time = localtime(now())
    date = _time.date()
    note = None
    have_errors = False
    created_order = None

    if not menu:
        note = 'The menu has not been created yet!'

    enable_form = allow_order(settings.ALLOWED_HOUR_TO_ORDER)

    if request.method == 'GET':
        try:
            created_order = Order.objects.get(employee=user, created_at=date.strftime("%Y-%m-%d"))
            form = OrderForm(instance=created_order)
            note = f'You have ordered {created_order.dish.name}'
            if created_order.customizations and created_order.customizations.strip() != '':
                note = f'{note} | {created_order.customizations.strip()}'
        except ObjectDoesNotExist as e:
            pass
        except MultipleObjectsReturned as e:
            note = 'There are more than 1 order, please contact Nora'
            have_errors = True

        if not enable_form and not created_order:
            note = f'{_time.time().strftime("%H:%M:%S")} - Too late to order :('
            have_errors = True

    elif request.method == 'POST':
        form = OrderForm(request.POST)
        if request.POST.get('options'):
            dish_id = request.POST.get('options')
            dish = Dish.objects.get(pk=dish_id)

            form.employee = user
            form.dish = dish

            # Edit dish
            try:
                created_order = Order.objects.get(employee=user, created_at=date.strftime("%Y-%m-%d"))
                created_order.dish = dish
                created_order.customizations = request.POST.get('customizations')
                created_order.save()
                note = f'You order has been updated to: {dish.name}'
                if created_order.customizations and created_order.customizations.strip() != '':
                    note = f'{note} | {created_order.customizations.strip()}'
            except ObjectDoesNotExist as e:
                pass
            except MultipleObjectsReturned as e:
                note = 'There are more than 1 order, please contact Nora'
                have_errors = True
                logger.error(f"Error: {e}")
            except Exception as e:
                note = 'Error updating your dish, please try again'
                have_errors = True
                logger.error(f"Error: {e}")

            if not created_order:
                try:
                    created_order = Order.objects.create(
                        dish=dish,
                        employee=user,
                        customizations=form.cleaned_data['customizations']
                    )
                    note = f'You have ordered {dish.name}!'
                    if created_order.customizations and created_order.customizations.strip() != '':
                        note = f'{note} | {created_order.customizations.strip()}'
                except Exception as e:
                    note = 'Error ordering your dish, please try again'
                    have_errors = True
                    logger.error(f"Error: {e}")
        else:
            note = f'Please choose a dish!'
            have_errors = True
    return render(request, 'employee/order.html', {
        'order_form': form,
        'note': note,
        'user': user,
        'menu': menu,
        'created_order': created_order,
        'have_errors': have_errors,
        'enable_form': enable_form,
        'pk': pk
    })
