from django.contrib import admin
from .models import Post, Comment

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_date', 'published_date')
    search_fields = ['title', 'text']
    fields = ('title', 'author', 'text', 'created_date', 'published_date')
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
