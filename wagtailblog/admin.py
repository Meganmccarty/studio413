from wagtail.contrib.modeladmin.options import (
    ModelAdmin,
    modeladmin_register,
)
from django.contrib import admin
from .models import BlogPage, Subscriber

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