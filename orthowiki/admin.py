from django.contrib import admin
from .models import Article, ContactSubmission


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ["title", "pub_date", "mod_date"]
    list_filter = ["pub_date", "mod_date"]
    search_fields = ["content", "title"]
    ordering = ['-pub_date']


@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display = ['submitted_at', 'name', 'email', 'subject', 'is_read']
    list_filter = ['submitted_at', 'is_read']
    search_fields = ['name', 'email', 'subject', 'message']
    ordering = ['-submitted_at']
