from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
from .models import Post, Comment, Subscriber, Newsletter

def send_notification(modeladmin, request, queryset):
    for post in queryset:
        post.send(request)

send_notification.short_description = "Send selected Post(s) to all subscribers"

@admin.register(Post)
class PostAdmin(SummernoteModelAdmin):
    list_display = ('title', 'author', 'created_date', 'published_date')
    search_fields = ['title', 'text']
    fields = ('title', 'author', 'youtube_video', 'text', 'created_date', 'published_date')
    summernote_fields = ('text')
    #prepopulated_fields = {'slug': ('title',)}
    actions = [send_notification]

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'name', 'email', 'created_date', 'approved_comment')
    list_filter = ('approved_comment', 'created_date')
    search_fields = ('name', 'email', 'text')
    fields = ('post', 'name', 'email', 'text', 'created_date', 'approved_comment')
    actions = ['approved_comments']

    def approved_comments(self, request, queryset):
        queryset.update(approved_comment=True)

@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'confirmed')
    fields = ('email', 'first_name', 'last_name', 'conf_num', 'confirmed')

def send_newsletter(modeladmin, request, queryset):
    for newsletter in queryset:
        newsletter.send(request)

send_newsletter.short_description = "Send selected Newsletters to all subscribers"

@admin.register(Newsletter)
class NewsletterAdmin(SummernoteModelAdmin):
    list_display = ('subject', 'created_at', 'updated_at')
    search_fields = ['subject', 'contents']
    fields = ('subject', 'contents', 'attachment', 'created_at', 'updated_at')
    #summernote_fields = ('contents')
    actions = [send_newsletter]

