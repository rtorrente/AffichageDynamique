from django.contrib import admin
from .models import *
# Register your models here.
@admin.register(Content, FeedGroup, Feed, Screen, Subscription)
class Admin(admin.ModelAdmin):
    pass