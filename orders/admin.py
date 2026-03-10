from django.contrib import admin
from .models import Payment, Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ('dish', 'quantity', 'price')
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'full_name', 'phone', 'email', 'total', 'payment_method', 'status', 'is_ordered', 'created_at']
    list_filter = ['status', 'is_ordered']
    search_fields = ['order_number', 'first_name', 'last_name', 'phone', 'email']
    list_per_page = 20
    inlines = [OrderItemInline]

    def full_name(self, obj):
        return f'{obj.first_name} {obj.last_name}'

admin.site.register(Payment)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
