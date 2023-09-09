from .import views
from django.urls import path
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("register", views.registerCommuter, name="register"),
    path('login', views.custom_login, name='login'),
    path('logout', views.custom_logout, name='logout'),
]