from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import *

# Register your models here.
@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    empty_value_display = 'vide'
    ordering = ('product', 'quantity', 'color',)
    search_fields = ['product__id', 'product__name']
    list_display = ['product_name', 'product_image', 'quantity', 'displayed_color']

    def product_name(self, obj):
        return obj.product.name

    def product_image(self, obj):
        return mark_safe('<img src="{}" alt="{}" style=" width: 8%; height: auto; " />'.format(obj.product.images.first().file.url, obj.product.name))

    def displayed_color(self, obj):
        return mark_safe('<button type="button" style=" padding: 16%; border-radius: 100%; background-color: {};"></button>'.format(obj.color))

    def view_color(self, obj):
        return mark_safe('<img src="..." alt="..." class="rounded-circle" />')\

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    empty_value_display = 'vide'
    ordering = ('price_from', 'product')
    search_fields = ['price_from', 'external_url']
    list_display = ['title', 'banner_description', 'product', 'banner_image']


    def banner_description(self, obj):
        return mark_safe(obj.description)

    def banner_image(self, obj):
        return mark_safe('<img src="{}" alt="{}" style="width: 20em;height: auto;" />'.format(obj.get_banner_image(), obj.get_banner_image()))

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    empty_value_display = 'vide'
    ordering = ('email', 'subject')
    search_fields = ['email', 'first_name', 'last_name', 'subject']
    list_display = ['email', 'nom', 'prenom', 'sujet', 'message']


    def nom(self, obj):
        return mark_safe(obj.first_name)
    def prenom(self, obj):
        return mark_safe(obj.last_name)
    def sujet(self, obj):
        return mark_safe(obj.subject)

admin.site.register(Image)
admin.site.register(Category)
admin.site.register(Brand)
admin.site.register(Product)
admin.site.register(Description)
admin.site.register(Color)
admin.site.register(Profile)
admin.site.register(Sale)
admin.site.register(Compare)
admin.site.register(NewsLetter)
admin.site.register(WishList)
admin.site.register(Order)
admin.site.register(OrderLine)
admin.site.register(Cart)
admin.site.register(Specification)
