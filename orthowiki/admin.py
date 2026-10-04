from django.contrib import admin
from .models import Article


class ArticleAdmin(admin.ModelAdmin):
    list_display = ["title", "pub_date", "mod_date"]
    list_filter = ["pub_date", "mod_date"]
    search_fields = ["content", "title"]


admin.site.register(Article, ArticleAdmin)
