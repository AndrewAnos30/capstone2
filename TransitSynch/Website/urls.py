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
    path('save_data/', views.save_data, name='save_data'),
    path("generate", views.generate, name="generate"),
    path('update_prices/', views.update_prices, name='update_prices'),
    path('update_current_price/', views.update_current_price, name='update_current_price'),
    path('computing_update/', views.computing_update, name='computing_update'),
    path('account_management/', views.account_management, name='account_management'),
    path('validation/', views.validation, name='validation'),
    path('update_validation/<int:user_id>/', views.update_validation, name='update_validation'),






]