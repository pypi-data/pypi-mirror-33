# -*- coding: utf-8 -*-

from django.apps import apps
from django.core.management import call_command
from django.db.models.signals import (
    post_delete, post_migrate, post_save,
)
from django.dispatch import receiver

from navsy import cache
from navsy.models import Page, Route
from navsy.utils import i18n_utils


app_config = apps.get_app_config('navsy')


@receiver(post_migrate, sender=app_config, dispatch_uid='post_migrate_app')
def post_migrate_app(sender, **kwargs):
    cache.delete_routes()
    Page.create_default_page()

    if i18n_utils.use_modeltranslation():
        call_command('update_translation_fields')


@receiver(post_save, sender=Page, dispatch_uid='post_save_page')
def post_save_page(sender, instance, **kwargs):
    instance.create_default_route()
    instance.update_unique_home()


@receiver(post_save, sender=Route, dispatch_uid='post_save_route')
def post_save_route(sender, instance, **kwargs):
    cache.delete_routes()


@receiver(post_delete, sender=Route, dispatch_uid='post_delete_route')
def post_delete_route(sender, instance, **kwargs):
    cache.delete_routes()
