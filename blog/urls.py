from django.urls import path
from . import views

urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('about/', views.about, name='about'),
    path('products/', views.products, name='products'),
    path('post/new/', views.post_new, name='post_new'),
    path('post/<slug>/', views.post_detail, name='post_detail'),
    path('post/<slug>/edit/', views.post_edit, name='post_edit'),
    path('drafts/', views.post_draft_list, name='post_draft_list'),
    path('post/<slug>/publish/', views.post_publish, name='post_publish'),
    path('post/<slug>/remove/', views.post_remove, name='post_remove'),
]