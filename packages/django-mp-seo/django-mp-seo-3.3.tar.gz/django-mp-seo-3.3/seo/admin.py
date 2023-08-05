
from importlib import import_module

from django.apps import apps
from django.contrib import admin

from seo.models import PageMeta


def _get_page_meta_admin_base_class():

    if apps.is_installed('modeltranslation'):
        return import_module('modeltranslation.admin').TranslationAdmin

    return admin.ModelAdmin


class PageMetaAdmin(_get_page_meta_admin_base_class()):

    list_display = ['url', 'title', 'robots']
    list_editable = ['robots']
    list_filter = ['robots']
    search_fields = ['url', 'title']


admin.site.register(PageMeta, PageMetaAdmin)
