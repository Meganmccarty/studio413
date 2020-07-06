from wagtail.contrib.modeladmin.options import (
    ModelAdmin,
    modeladmin_register,
)
from .models import Subscriber

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