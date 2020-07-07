from django.urls import path
from . import views

urlpatterns = [
    path('products/', views.products, name='products'),
    path('products/art-for-sale/', views.art_for_sale, name='art_for_sale'),
    path('products/art-pages/', views.art_pages, name='art_pages'),
    path('new-subscriber/', views.new, name='new'),
    path('confirm/', views.confirm, name='confirm'),
    path('delete/', views.delete, name='delete'),
    path('contact/', views.contact, name='contact'),
]