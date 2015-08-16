from django.contrib import admin

from getresults.admin import admin_site

from .models import Panel, PanelItem, Utestid, Order, UtestidMapping, Sender


class PanelItemInline(admin.TabularInline):
    model = PanelItem
    extra = 0


class PanelItemAdmin(admin.ModelAdmin):
    list_display = ('panel', 'utestid')
    search_fields = ('panel__name', 'utestid__name')
admin_site.register(PanelItem, PanelItemAdmin)


class PanelAdmin(admin.ModelAdmin):
    inlines = [PanelItemInline]
admin_site.register(Panel, PanelAdmin)


class UtestidAdmin(admin.ModelAdmin):
    pass
admin_site.register(Utestid, UtestidAdmin)


class OrderAdmin(admin.ModelAdmin):
    date_hierarchy = 'order_datetime'
    list_display = ('order_identifier', 'order_datetime', 'panel', 'aliquot')
    search_fields = ('order_identifier', 'aliquot__aliquot_identifier', 'panel__name')

    # inlines = [ResultInline, ]
admin_site.register(Order, OrderAdmin)


class SenderAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description')
admin_site.register(Sender, SenderAdmin)


class UtestidMappingAdmin(admin.ModelAdmin):
    list_display = ('sender', 'sender_utestid_name', 'utestid')
    search_fields = ('sender__name', 'sender_utestid_name', 'utestid__name')
admin_site.register(UtestidMapping, UtestidMappingAdmin)
