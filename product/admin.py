from django.contrib import admin
from . import models

class VariationInline(admin.TabularInline):
    model = models.Variation
    extra = 0

class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'short_description', 'get_preco_formatado', 'get_preco_promocional_formatado']
    inlines = [
        VariationInline
    ]

# Register your models here.
admin.site.register(models.Product, ProductAdmin)
admin.site.register(models.Variation)