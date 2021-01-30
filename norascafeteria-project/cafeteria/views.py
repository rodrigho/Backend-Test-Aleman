from django.contrib.auth.decorators import login_required
from django.shortcuts import render
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
def allow_order():
    datetime = localtime(now())
    return datetime.hour < 11

@login_required
def order(request):
    form = OrderForm()

    username = request.user.username
    user = User.objects.get(username=username)

    date = localtime(now()).date()

    try:
        menu = Menu.objects.get(date=date)
    except Exception as ex:
        return render(request, 'employee/order.html', {
            'order_form': None,
            'user': user,
            'menu': None,
            'note': 'The has not been created yet!'
        })

    enable_form = allow_order()

    if request.method == 'GET':
        try:
            order2 = Order.objects.get(employee=user, created_at=date.strftime("%Y-%m-%d"))
            if order2:
                return render(request, 'employee/order.html', {
                    'order_form': form,
                    'date': date,
                    'note': 'You have already choose your dish',
                    'user': user,
                    'menu': menu,
                    'created_order': order2,
                    'enable_form': enable_form
                })
        except Exception as ex:
            print(f'Error {ex}')
            pass

        if not enable_form:
            return render(request, 'employee/order.html', {
                'order_form': None,
                'date': date,
                'note': 'Good luck next time :(',
                'user': user,
                'menu': None,
                'created_order': None,
                'enable_form': enable_form
            })

    if request.method == 'POST':
        filled_form = OrderForm(request.POST)
        if filled_form.is_valid():

            dish_id = request.POST.get('options')
            dish = Dish.objects.get(pk=dish_id)

            filled_form.employee = user
            filled_form.dish = dish
            created_order = Order.objects.create(
                dish=dish,
                employee=user,
                customizations=filled_form.cleaned_data['customizations']
            )

            note = f'You have ordered {dish.name}!'
            filled_form = OrderForm()
        else:
            date = None
            note = f'Error, please try again!'
            created_order = None
        return render(request, 'employee/order.html', {
            'order_form': filled_form,
            'date': date,
            'note': note,
            'user': user,
            'menu': menu,
            'created_order': created_order
        })

    return render(request, 'employee/order.html', {
        'order_form': form,
        'user': user,
        'menu': menu
    })


@login_required
def order_uuid(request, pk):
    form = OrderForm()
    print(pk)
    username = request.user.username
    user = User.objects.get(username=username)

    date = localtime(now()).date()
    menu = None
    try:
        menu = Menu.objects.get(uuid=pk)
    except Exception as ex:
        print(ex)
    return render(request, 'employee/order.html', {
        'order_form': form,
        'user': user,
        'menu': menu,
        'note': None
    })