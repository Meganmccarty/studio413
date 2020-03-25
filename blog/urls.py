from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('blog/', views.post_list, name='post_list'),
    path('products/', views.products, name='products'),
    path('new-subscriber/', views.new, name='new'),
    path('confirm/', views.confirm, name='confirm'),
    path('delete/', views.delete, name='delete'),
    path('post/new/', views.post_new, name='post_new'),
    path('post/<slug>/', views.post_detail, name='post_detail'),
    path('post/<slug>/edit/', views.post_edit, name='post_edit'),
    path('drafts/', views.post_draft_list, name='post_draft_list'),
    path('post/<slug>/publish/', views.post_publish, name='post_publish'),
    path('post/<slug>/remove/', views.post_remove, name='post_remove'),
]