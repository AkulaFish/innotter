from django.contrib import admin
from .models import Page, Post, Tag


@admin.register(Page, Post, Tag)
class CoreAdmin(admin.ModelAdmin):
    pass
