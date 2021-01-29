from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .forms import DishForm, MenuForm
from .models import Dish


def home(request):
    return render(request, 'cafeteria/home.html')


@login_required
def dish_form(request):
    role = request.user.role.lower()
    if role != 'admin':
        return render(request, 'cafeteria/home.html')

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
        return render(request, 'cafeteria/home.html')

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
