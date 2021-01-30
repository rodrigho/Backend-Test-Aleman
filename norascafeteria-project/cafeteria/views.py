from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.shortcuts import render, redirect
from django.utils.timezone import now, localtime

from .forms import DishForm, MenuForm, OrderForm
from .models import Dish, User, Menu, Order


def home(request):
    date = localtime(now()).date()
    menu = None
    try:
        menu = Menu.objects.get(date=date)
        print(f'Menu uuid: {menu.uuid}')
    except Exception as ex:
        print(f'Error: {ex}')

    is_authenticated = False
    is_admin = False

    if request.user.is_authenticated:
        print('User authenticated')
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

    dish = Dish.objects.get(pk=pk)
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
    if request.method == 'POST':
        filled_form = MenuForm(request.POST)
        if filled_form.is_valid():
            created_menu = filled_form.save()
            date = created_menu.date
            note = f'Menu has been created for {date}!'
            filled_form = MenuForm()
        else:
            date = None
            note = f'This menu could not be added, please try again!'
            created_menu = None
        return render(request, 'cafeteria/menu_form.html', {
            'menu_form': filled_form,
            'date': date,
            'note': note,
            'created_menu': created_menu
        })
    return render(request, 'cafeteria/menu_form.html', {'menu_form': form})


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
            for order in orders:
                print(f'{order.dish.name}')
        except Exception as ex:
            print(f'Error orders: {ex}')
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
        menu = Menu.objects.get(uuid=pk)
    except ObjectDoesNotExist as e:
        pass
    except MultipleObjectsReturned as e:
        pass
    return order(request, user, menu, pk)


def order(request, user, menu, pk):
    form = OrderForm()
    date = localtime(now()).date()
    note = None
    have_errors = False
    created_order = None

    if not menu:
        note = 'The menu has not been created yet!'

    enable_form = allow_order(15)

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
            note = 'Too late to order :('
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
            except Exception as e:
                note = 'Error updating your dish, please try again'
                have_errors = True

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
        else:
            note = f'Please choose a dish!'
            have_errors = True
    return render(request, 'employee/order.html', {
        'order_form': form,
        'date': date,
        'note': note,
        'user': user,
        'menu': menu,
        'created_order': created_order,
        'have_errors': have_errors,
        'enable_form': enable_form,
        'pk': pk
    })
