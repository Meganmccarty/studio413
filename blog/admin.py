from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
from .models import Post, Comment, Subscriber, Newsletter

@admin.register(Post)
class PostAdmin(SummernoteModelAdmin):
    list_display = ('title', 'author', 'created_date', 'published_date')
    search_fields = ['title', 'text']
    fields = ('title', 'author', 'text', 'created_date', 'published_date')
    summernote_fields = ('text')
    #prepopulated_fields = {'slug': ('title',)}

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'name', 'email', 'created_date', 'approved_comment')
    list_filter = ('approved_comment', 'created_date')
    search_fields = ('name', 'email', 'text')
    fields = ('post', 'name', 'email', 'text', 'created_date', 'approved_comment')
    actions = ['approve_comments']

    def approve_comments(self, request, queryset):
        queryset.update(approve_comment=True)

@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'confirmed')
    fields = ('email', 'first_name', 'last_name', 'conf_num', 'confirmed')

@admin.register(Newsletter)
class PostAdmin(SummernoteModelAdmin):
    list_display = ('subject', 'created_at', 'updated_at')
    search_fields = ['subject', 'contents']
    fields = ('subject', 'contents', 'created_at', 'updated_at')
    summernote_fields = ('contents')
