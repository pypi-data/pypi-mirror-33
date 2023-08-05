from django import template
from django.conf import settings
from ..models import TrackingItem, TRACKING_ITEM_CHOICES, TRACKING_ITEM_CHOICE_ESSENTIALS, TRACKING_ITEM_CHOICE_MARKETING, TRACKING_ITEM_CHOICE_STATISTICS
from django.db.models import Q

register = template.Library()


@register.inclusion_tag('django_privacy_mgmt/popup.html', takes_context=True)
def render_privacy_settings_modal(context):
    sezikai_ctx_var = getattr(settings, 'SEKIZAI_VARNAME', 'SEKIZAI_CONTENT_HOLDER')
    tracking_items = TrackingItem.objects.filter(Q(site=settings.SITE_ID) | Q(site__isnull=True))

    return {
        'essentials': tracking_items.filter(category=TRACKING_ITEM_CHOICE_ESSENTIALS),
        'statistics': tracking_items.filter(category=TRACKING_ITEM_CHOICE_STATISTICS),
        'marketing': tracking_items.filter(category=TRACKING_ITEM_CHOICE_MARKETING),
        'tracking_items': tracking_items,
        sezikai_ctx_var: context[sezikai_ctx_var]
    }


@register.inclusion_tag('django_privacy_mgmt/api.html')
def render_privacy_api():
    pass


@register.inclusion_tag('django_privacy_mgmt/link.html')
def render_privacy_settings_modal_link():
    pass


@register.inclusion_tag('django_privacy_mgmt/banner.html', takes_context=True)
def render_privacy_banner(context):
    sezikai_ctx_var = getattr(settings, 'SEKIZAI_VARNAME', 'SEKIZAI_CONTENT_HOLDER')
    tracking_items = TrackingItem.objects.filter(Q(site=settings.SITE_ID) | Q(site__isnull=True))

    return {
        'essentials': tracking_items.filter(category=TRACKING_ITEM_CHOICE_ESSENTIALS),
        'statistics': tracking_items.filter(category=TRACKING_ITEM_CHOICE_STATISTICS),
        'marketing': tracking_items.filter(category=TRACKING_ITEM_CHOICE_MARKETING),
        'tracking_items': tracking_items,
        sezikai_ctx_var: context[sezikai_ctx_var]
    }
