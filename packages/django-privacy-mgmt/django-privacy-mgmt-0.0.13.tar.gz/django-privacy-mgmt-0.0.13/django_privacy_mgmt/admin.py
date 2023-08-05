from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from parler.admin import TranslatableAdmin
from .models import TrackingItem


class TrackingItemAdmin(TranslatableAdmin):
    list_display = ('__unicode__', 'category', )
    search_fields = ('name', )
    list_filter = ('category', )

    filter_vertical = ('site', )


admin.site.register(TrackingItem, TrackingItemAdmin)
