from django.contrib import admin
from django.contrib.admin import ModelAdmin

from .models import Book, UserBookRelation

# Register your models here.


@admin.register(Book)
class BookAdmin(ModelAdmin):
    pass


@admin.register(UserBookRelation)
class BookAdmin(ModelAdmin):
    pass
