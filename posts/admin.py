from django.contrib import admin
from .models import Post, SubPost


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "created_at", "updated_at")
    list_filter = ("created_at", "author")
    search_fields = ("title", "body")
    date_hierarchy = "created_at"


@admin.register(SubPost)
class SubPostAdmin(admin.ModelAdmin):
    list_display = ("title", "post", "created_at", "updated_at")
    list_filter = ("created_at", "post")
    search_fields = ("title", "body")
    date_hierarchy = "created_at"
