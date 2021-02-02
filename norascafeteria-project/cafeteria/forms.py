from django import forms
from django.utils.timezone import now, localtime

from .models import Dish, Menu, Order


class DishForm(forms.ModelForm):
    class Meta:
        model = Dish
        fields = ['name']
        labels = {'name': 'Dish name'}


class MenuForm(forms.ModelForm):
    date = forms.DateField(
        initial=localtime(now()).date(),
        label='Pick a date to create a menu',
        input_formats=['%Y-%m-%d'],
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
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


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['dish', 'customizations']
        labels = {'dish': 'Lunch options', 'customizations': 'Add customizations'}
