from django.contrib import admin
from .models import Product, Category, Review, Discount

class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'sku',
        'name',
        'category',
        'price',
        'rating',
        'image',
    )
    ordering = ('price',)
    search_fields = ('name', 'sku')
    list_filter = ('category',)

class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'friendly_name',
        'name',
    )
    search_fields = ('friendly_name', 'name')

admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)  # This is the correct registration

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'status', 'created_at')
    actions = ['approve_reviews', 'reject_reviews']

    def approve_reviews(self, request, queryset):
        queryset.update(status='approved')
        self.message_user(request, "Selected reviews have been approved.")

    def reject_reviews(self, request, queryset):
        queryset.update(status='rejected')
        self.message_user(request, "Selected reviews have been rejected.")

@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ('category', 'discount_percentage', 'start_date', 'end_date')
