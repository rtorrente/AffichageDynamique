from django.contrib import admin
from .models import *
# Register your models here.
@admin.register(Content, FeedGroup, Feed, Subscription, Image)
class Admin(admin.ModelAdmin):
    pass

@admin.register(Screen)
class ScreenAdmin(admin.ModelAdmin):
  list_display = ('name', 'place', 'token')