from . import views
from django.urls import path

urlpatterns = [
    path("home", views.homepage, name="home"),
    path("", views.welcome, name="welcome"),
    path("admin", views.admin, name="admin"),
    path("conductor/", views.conductor, name="conductor"),
    path("cashier/", views.cashier, name="cashier"),
    path("commuter/", views.commuter, name="commuter"),
    path('create_conductor/', views.create_conductor, name='create_conductor'),
    path('create_cashier/', views.create_cashier, name='create_cashier'),
    path('track_prices/', views.track_prices, name='track_prices'),
    path("", views.homepage, name="home"),
    path("generate", views.generate, name="generate"),
    path("conductorHome", views.conductorHome, name="conductorHome"),





]