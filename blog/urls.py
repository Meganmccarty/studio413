from django.urls import path
from . import views

urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('post/new/', views.post_new, name='post_new'),
    path('post/<slug>/', views.post_detail, name='post_detail'),
    path('post/<slug>/edit/', views.post_edit, name='post_edit'),
    path('drafts/', views.post_draft_list, name='post_draft_list'),
    path('post/<slug>/publish/', views.post_publish, name='post_publish'),
    path('post/<slug>/remove/', views.post_remove, name='post_remove'),
    #path('post/<slug>/comment/', views.add_comment_to_post, name='add_comment_to_post'),
    #path('comment/<slug>/remove/', views.comment_remove, name='comment_remove'),
    #path('comment/<slug>/approve/', views.comment_approve, name='comment_approve'),
]