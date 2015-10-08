from django.contrib import admin

from getresults.admin import admin_site

from .models import (
    OrderPanel, OrderPanelItem, Utestid, Order, Sender, SenderPanel,
    SenderPanelItem, SenderModel)


class OrderPanelItemInline(admin.TabularInline):
    model = OrderPanelItem
    extra = 0


class OrderPanelItemAdmin(admin.ModelAdmin):
    list_display = ('order_panel', 'utestid')
    search_fields = ('order_panel__name', 'utestid__name')
admin_site.register(OrderPanelItem, OrderPanelItemAdmin)


class OrderPanelAdmin(admin.ModelAdmin):
    list_display = ('name', )
    search_fields = ('name', )
    inlines = [OrderPanelItemInline]
admin_site.register(OrderPanel, OrderPanelAdmin)


class UtestidAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'units', 'description', 'value_type', 'value_datatype',
        'lower_limit', 'upper_limit', 'formula')
    search_fields = ('name', )
    list_filter = ('value_type', 'value_datatype', )
admin_site.register(Utestid, UtestidAdmin)


class OrderAdmin(admin.ModelAdmin):
    date_hierarchy = 'order_datetime'
    list_display = ('order_identifier', 'order_datetime', 'order_panel', 'aliquot')
    search_fields = ('order_identifier', 'aliquot__aliquot_identifier', 'order_panel__name')
admin_site.register(Order, OrderAdmin)


class SenderAdmin(admin.ModelAdmin):
    list_display = ('sender_model', 'serial_number')
    search_fields = (
        'sender_model__name', 'serial_number', 'sender_model__make',
        'sender_model__description')
admin_site.register(Sender, SenderAdmin)


class SenderInline(admin.TabularInline):
    model = Sender
    extra = 0


class SenderModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'make', 'description')
    search_fields = ('name', )
    inlines = [SenderInline, ]
admin_site.register(SenderModel, SenderModelAdmin)


class SenderPanelItemAdmin(admin.ModelAdmin):
    list_display = ('sender_panel', 'utestid')
    search_fields = ('utestid', 'sender_panel__name')
admin_site.register(SenderPanelItem, SenderPanelItemAdmin)


class SenderPanelItemInline(admin.TabularInline):
    model = SenderPanelItem
    extra = 0


class SenderPanelAdmin(admin.ModelAdmin):
    list_display = ('name', 'sender_model')
    search_fields = ('name', 'sender_model__name')
    inlines = [SenderPanelItemInline]
admin_site.register(SenderPanel, SenderPanelAdmin)
