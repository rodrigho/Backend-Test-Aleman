from django.test import TestCase
from uuid import UUID
from django.utils.timezone import now, localtime
from django.db import IntegrityError

from .models import Dish, User, Menu, Order


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
