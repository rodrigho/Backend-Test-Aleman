from http import HTTPStatus

from django.core import serializers
from django.test import TestCase
from uuid import UUID
from django.utils.timezone import now, localtime
from django.db import IntegrityError
from django.test import Client

from .models import Dish, User, Menu, Order
from .forms import DishForm, MenuForm, OrderForm


# All Model tests
class UserTest(TestCase):

    def create_user(self, username="test", password="1234", first_name="Test", role="admin/employee"):
        return User.objects.create(username=username, password=password, first_name=first_name, role=role)

    def test_admin_user(self):
        role = "admin"
        user = self.create_user(role=role)
        self.assertTrue(isinstance(user, User))
        self.assertEqual(user.role, role)

    def test_employee_user(self):
        role = "employee"
        user = self.create_user(role=role)
        self.assertTrue(isinstance(user, User))
        self.assertEqual(user.role, role)


class DishTest(TestCase):

    def create_dish(self, name):
        return Dish.objects.create(name=name)

    def test_dish_creation(self):
        name = "Premium chicken Salad and Dessert"
        dish = self.create_dish(name=name)
        self.assertTrue(isinstance(dish, Dish))
        self.assertEqual(dish.name, name)
        with self.assertRaises(IntegrityError) as raise_context:
            self.create_dish(name)
            self.assertTrue('UNIQUE constraint failed' in raise_context.exception.message)


class MenuTest(TestCase):

    def create_menu(self):
        menu = Menu()
        menu.detail = "Today's menu"
        menu.dishes.set(Dish.objects.all())
        menu.date = localtime(now()).date()
        menu.save()
        return menu

    def test_menu_creation(self):
        menu = self.create_menu()
        self.assertTrue(isinstance(menu, Menu))
        val_uuid = UUID(str(menu.uuid), version=4)
        self.assertEqual(val_uuid.hex, str(menu.uuid).replace('-', ''))
        self.assertFalse(menu.notification_sent)
        with self.assertRaises(IntegrityError) as raise_context:
            self.create_menu()
            self.assertTrue('UNIQUE constraint failed' in raise_context.exception.message)


class OrderTest(TestCase):

    def create_order(self):
        order = Order()
        order.customizations = "No tomatoes in the salad"
        order.employee = User.objects.create(username='test', password='1234', role='employee')
        order.dish = Dish.objects.create(name="Premium chicken Salad and Dessert")
        order.save()
        return order

    def test_order_creation(self):
        order = self.create_order()
        self.assertTrue(isinstance(order, Order))
        self.assertEqual(order.dish.name, "Premium chicken Salad and Dessert")
        with self.assertRaises(IntegrityError) as raise_context:
            self.create_order()
            self.assertTrue('UNIQUE constraint failed' in raise_context.exception.message)


# All Form tests
class DishFormTest(TestCase):

    def test_valid_dish_form(self):
        data = {'name': 'Other dish'}
        form = DishForm(data=data)
        self.assertTrue(form.is_valid())

    def test_error_dish_form(self):
        dish = Dish.objects.create(name='Premium chicken Salad and Dessert')
        data = {'name': dish.name}
        form = DishForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["name"], ["Dish with this Name already exists."])


class MenuFormTest(TestCase):

    def test_valid_menu_form(self):
        dish = Dish.objects.create(name='foo')
        data = {'date': localtime(now()).date(), 'detail': 'None', 'dishes': [dish]}
        form = MenuForm(data=data)
        self.assertTrue(form.is_valid())

    def test_error_menu_form(self):
        data = {'date': localtime(now()).date(), 'detail': 'None', 'dishes': None}
        form = MenuForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["dishes"], ["This field is required."])
        data = {'date': localtime(now()).date(), 'detail': '', 'dishes': [{"name": "foo"}]}
        form = MenuForm(data=data)
        self.assertEqual(form.errors["dishes"], ["Enter a list of values."])
        self.assertEqual(form.errors["detail"], ["This field is required."])

        menu = Menu()
        menu.detail = "Today's menu"
        menu.dishes.set(Dish.objects.all())
        menu.date = localtime(now()).date()
        menu.save()

        dish = Dish.objects.create(name='foo')
        data = {'date': localtime(now()).date(), 'detail': 'None', 'dishes': [dish]}
        form = MenuForm(data=data)
        self.assertEqual(form.errors["date"], ["Menu with this Date already exists."])


class OrderFormTest(TestCase):

    def test_valid_order_form(self):
        dish = Dish.objects.create(name='foo')
        data = {'dish': dish, 'customizations': ''}
        form = OrderForm(data=data)
        self.assertTrue(form.is_valid())

    def test_error_order_form(self):
        data = {'dish': 'foo', 'customizations': ''}
        form = OrderForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["dish"], ["Select a valid choice. That choice is not one of the available choices."])
        data = {'dish': None, 'employee': 'test', 'customizations': ''}
        form = OrderForm(data=data)
        self.assertEqual(form.errors["dish"], ["This field is required."])


# All View tests
class HomeViewTest(TestCase):

    def setUp(self):
        user = User.objects.create(username='testuser', password="1234", role="admin", first_name="User Name")
        user.set_password('1234')
        user.save()
        self.response = self.client.login(username='testuser', password='1234')

    def test_get_home_view(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, "Nora's Cafeteria", html=True)
        self.assertContains(response, "Welcome, User Name", html=True)

        self.client.logout()
        response = self.client.get("/")
        self.assertContains(response, "Log in", html=True)


class DishViewTest(TestCase):

    def setUp(self):
        user = User.objects.create(username='testuser', password="1234", role="admin")
        user.set_password('1234')
        user.save()
        self.response = self.client.login(username='testuser', password='1234')

    def test_get_dish_view(self):
        response = self.client.get("/dish_form")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, "Add a new dish", html=True)

    def test_post_dish_view(self):
        response = self.client.post("/dish_form", data={"name": "foo"})
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, "Add a new dish", html=True)

    def test_not_permission_dish_view(self):
        self.client.logout()
        response = self.client.get("/dish_form")
        self.assertEqual(response.status_code, HTTPStatus.FOUND)


class MenuViewTest(TestCase):

    def setUp(self):
        user = User.objects.create(username='testuser', password="1234", role="admin", first_name="Name")
        user.set_password('1234')
        user.save()

        Dish.objects.create(name="Corn pie, Salad and Dessert")
        Dish.objects.create(name="Premium chicken Salad and Dessert")
        self.menu = Menu()
        self.menu.detail = "Today's menu"
        self.menu.date = localtime(now()).date()
        self.menu.save()
        self.menu.dishes.set(Dish.objects.all())
        self.menu.save()

        self.response = self.client.login(username='testuser', password='1234')

    def test_get_menu_view(self):
        response = self.client.get("/menu_form")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, "Hello Name", html=True)

    def test_error_menu_view(self):
        self.client.logout()
        response = self.client.get("/menu_form")
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_post_menu_view(self):
        data = {'date': self.menu.date, 'detail': self.menu.detail, 'dishes': self.menu.dishes}
        response = self.client.post("/menu_form", data=data)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, "Today's Menu", html=True)
        self.assertContains(response, self.menu.dishes.first(), html=True)
        self.assertContains(response, self.menu.dishes.last(), html=True)

    def test_error_post_menu_view(self):
        data = {'date': self.menu.date, 'detail': self.menu.detail, 'dishes': self.menu.dishes}
        self.client.post("/menu_form", data=data)
        response = self.client.post("/menu_form", data=data)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, "Menu could not be added, please try again!", html=True)

    def test_get_menu_edit_view(self):
        response = self.client.get(f"/menu_form/{self.menu.uuid}")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, "Hello Name, let's edit the menu", html=True)

    def test_error_post_menu_edit_view(self):
        data = {'date': self.menu.date, 'detail': 'No details', 'dishes': self.menu.dishes}
        response = self.client.post(f"/menu_form/{self.menu.uuid}", data=data)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, "Menu was not updated, please try again", html=True)


class SeeOrdersViewTest(TestCase):

    def setUp(self):
        user = User.objects.create(username='testuser', password="1234", role="admin")
        user.set_password('1234')
        user.save()
        self.response = self.client.login(username='testuser', password='1234')

    def test_get_dish_view(self):
        response = self.client.get("/see_orders")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, "Employees' orders for today", html=True)
        self.client.logout()
        response = self.client.get("/see_orders")
        self.assertEqual(response.status_code, HTTPStatus.FOUND)


class OrderViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='testuser', password="1234", role="employee", first_name="Employee")
        self.user.set_password('1234')
        self.user.save()

        self.dish1 = Dish.objects.create(name="Corn pie, Salad and Dessert")
        self.dish2 = Dish.objects.create(name="Premium chicken Salad and Dessert")
        self.menu = Menu()
        self.menu.detail = "Today's menu"
        self.menu.date = localtime(now()).date()
        self.menu.save()
        self.menu.dishes.set(Dish.objects.all())
        self.menu.save()

        self.response = self.client.login(username=self.user.username, password='1234')

    def test_get_order_view(self):
        response = self.client.get(f"/menu/{self.menu.uuid}")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, "Hello Employee", html=True)

    def test_get_order_requested_view(self):
        order = Order()
        order.customizations = ''
        order.employee = self.user
        order.dish = self.dish1
        order.save()

        response = self.client.get(f"/menu/{self.menu.uuid}")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, "You have ordered Corn pie, Salad and Dessert", html=True)

    def test_post_request_order_view(self):
        data = {'dish': self.dish2, 'employee': self.user, 'customizations': 'No tomatoes'}
        response = self.client.post(f"/menu/{self.menu.uuid}", data=data)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, "Please choose a dish!", html=True)

    def test_error_get_order_view(self):
        response = self.client.get(f"/menu/0371577c-e15a-4466-88a2-f54fcace18a6")
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.client.logout()
        response = self.client.get(f"/menu/{self.menu.uuid}")
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_error_post_order_view(self):
        data = {'dish': self.dish1, 'employee': self.user, 'customizations': 'No tomatoes'}
        response = self.client.post(f"/menu/0371577c-e15a-4466-88a2-f54fcace18a6", data=data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.client.logout()
        response = self.client.post(f"/menu/{self.menu.uuid}", data=data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
