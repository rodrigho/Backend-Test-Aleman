from django import forms
from .models import Dish, Menu


'''class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password']
        labels = {'username': 'User name', 'password': 'Password'}'''


class DishForm(forms.ModelForm):
    class Meta:
        model = Dish
        fields = ['name']
        labels = {'name': 'Dish name'}


class MenuForm(forms.ModelForm):
    date = forms.DateField(
        label='Pick a date to create a menu',
        input_formats=['%Y-%m-%d'],
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control datetimepicker-input',
            'data-target': '#datetimepicker1'
        }))

    dishes = forms.ModelMultipleChoiceField(
        label='Options',
        queryset=Dish.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    class Meta:
        model = Menu
        fields = ['date', 'detail', 'dishes']
        labels = {'date': 'Pick a date to create a menu', 'detail': 'Message to employees', 'dishes': 'Options'}

