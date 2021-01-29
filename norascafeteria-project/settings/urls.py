from django.contrib import admin
from django.urls import path, include
from django.urls import path
from cafeteria import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', views.home, name='home'),
    path('dish_form', views.dish_form, name='dish_form'),
    path('menu_form', views.menu_form, name='menu_form'),
    path('dish_form/<int:pk>', views.edit_dish, name='edit_dish'),
]