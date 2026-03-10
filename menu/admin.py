from django.contrib import admin
from .models import Category, Dish

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name', 'slug')

class DishAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name', 'category', 'price', 'is_available', 'updated_at')
    search_fields = ('name', 'category__name')
    list_filter = ('category', 'is_available')

admin.site.register(Category, CategoryAdmin)
admin.site.register(Dish, DishAdmin)
