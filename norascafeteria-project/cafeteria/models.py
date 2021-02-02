import uuid as uuid

from django.contrib.auth.models import UserManager, AbstractUser, PermissionsMixin
from django.db import models
from django.utils.timezone import now, localtime


ROLES = (
    ('admin', "Admin"),
    ('employee', "Employee"),
)


class User(AbstractUser):
    last_name = models.CharField(max_length=100, blank=True, null=True)
    password = models.CharField(max_length=100)
    role = models.CharField(max_length=8, choices=ROLES, default='employee')

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['password', 'role']


class Dish(models.Model):
    name = models.CharField(max_length=256, unique=True)

    def __str__(self):
        return self.name


class Menu(models.Model):
    date = models.DateField(unique=True)
    detail = models.TextField()
    dishes = models.ManyToManyField(Dish)
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    notification_sent = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.date} {self.detail}'


class Order(models.Model):
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    employee = models.ForeignKey(User, on_delete=models.CASCADE)
    customizations = models.CharField(max_length=256, default='', blank=True, null=True)
    created_at = models.DateField(default=localtime(now()).date().strftime("%Y-%m-%d"))

    class Meta:
        unique_together = ('employee', 'created_at',)

    def __str__(self):
        return f'{self.created_at}  {self.employee.username} {self.dish.name}'
