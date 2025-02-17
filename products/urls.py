from django.contrib import admin
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path(
        'products/', views.all_products, name='products'
    ),
    path(
        'product/<int:product_id>/',
        views.product_detail, name='product_detail'
    ),
    path('add/', views.add_product, name='add_product'),
    path('edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path(
        'delete/<int:product_id>/', views.delete_product, name='delete_product'
    ),
    path('wishlist/', views.view_wishlist, name='view_wishlist'),
    path(
        'wishlist/add/<int:product_id>/',
        views.add_to_wishlist, name='add_to_wishlist'
    ),
    path(
        'wishlist/remove/<int:product_id>/',
        views.remove_from_wishlist, name='remove_from_wishlist'
    ),
    path('add_to_bag/<int:product_id>/', views.add_to_bag, name='add_to_bag'),
    path(
        'product/<int:product_id>/submit_review/',
        views.submit_review, name='submit_review'
    ),
    path('login/', auth_views.LoginView.as_view(), name='login'),
]
