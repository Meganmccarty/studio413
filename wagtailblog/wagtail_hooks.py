import wagtail.admin.rich_text.editors.draftail.features as draftail_features
from wagtail.admin.rich_text.converters.html_to_contentstate import InlineStyleElementHandler
from wagtail.admin.action_menu import ActionMenuItem
from wagtail.core import hooks

from .models import Subscriber, BlogPage
from django.conf import settings
from django.core.mail import send_mail
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (Mail, Attachment, FileContent, FileName, FileType, Disposition)

class NotificationMenuItem(ActionMenuItem):
    name = 'email-notification'
    label = "Notify Subscribers of New Post"

    def get_url(self, request, context):
        return 'http://www.zenstudio413.com/admin/wagtailblog/blogpage/'
        #BlogPage.send('', request)

@hooks.register('register_page_action_menu_item')
def register_notification_menu_item():
    return NotificationMenuItem(order=100)


@hooks.register("register_rich_text_features")
def register_centertext_feature(features):
    """Creates centered text in our richtext editor and page."""

    # Step 1
    feature_name = "center"
    type_ = "CENTERTEXT"
    tag = "div"

    # Step 2
    control = {
        "type": type_,
        "label": "Center",
        "description": "Center Text",
        "style": {
            "display": "block",
            "text-align": "center",
        },
    }

    # Step 3
    features.register_editor_plugin(
        "draftail", feature_name, draftail_features.InlineStyleFeature(control)
    )

    # Step 4
    db_conversion = {
        "from_database_format": {tag: InlineStyleElementHandler(type_)},
        "to_database_format": {
            "style_map": {
                type_: {
                    "element": tag,
                    "props": {
                        "class": "d-block text-center"
                    }
                }
            }
        }
    }

    # Step 5
    features.register_converter_rule("contentstate", feature_name, db_conversion)

    # Step 6, This is optional.
    features.default_features.append(feature_name)