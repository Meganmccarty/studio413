from wagtail.contrib.modeladmin.options import (
    ModelAdmin,
    modeladmin_register,
)
from django.contrib import admin
from .models import BlogPage, Subscriber

from django_comments_xtd.models import XtdComment

def send_notification(modeladmin, request, queryset):
    for post in queryset:
        post.send(request)

send_notification.short_description = "Send selected Post(s) to all subscribers"


class BlogPageAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'body')
    search_fields = ['title', 'body']
    actions = [send_notification]
admin.site.register(BlogPage, BlogPageAdmin)

class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'confirmed')
admin.site.register(Subscriber, SubscriberAdmin)

class SubscriberAdmin(ModelAdmin):
    """Subscriber admin."""

    model = Subscriber
    menu_label = "Subscribers"
    menu_icon = "mail"
    menu_order = 290
    add_to_settings_menu = False
    exclude_from_explorer = False
    list_display = ("first_name", "last_name", "email", "confirmed")
    search_fields = ("first_name", "last_name", "email")

modeladmin_register(SubscriberAdmin)

class CommentsAdmin(ModelAdmin):
    model = XtdComment
    menu_label = "Comments"
    menu_icon = "icon icon-fa-comments-o"
    menu_order = 280
    add_to_settings_menu = True
    exclude_from_explorer = False
    list_display = ("comment", "user_name", "submit_date", "is_public", "is_removed")
    fields_display = ["comment", "user", "user_name", "user_email", "submit_date", "is_public", "is_removed"]
    search_fields = ("comment", "user_name", "submit_date")

modeladmin_register(CommentsAdmin)