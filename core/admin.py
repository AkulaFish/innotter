from django.contrib import admin
from .models import *


@admin.register(Page, Post, Tag)
class CoreAdmin(admin.ModelAdmin):
    pass
