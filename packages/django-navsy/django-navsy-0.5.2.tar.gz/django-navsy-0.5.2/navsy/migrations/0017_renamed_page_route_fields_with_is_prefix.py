# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('navsy', '0016_remove_page_published'),
    ]

    operations = [
        migrations.RenameField(
            model_name='route',
            old_name='published',
            new_name='is_enabled',
        ),
        migrations.RenameField(
            model_name='page',
            old_name='home',
            new_name='is_home',
        ),
        migrations.RenameField(
            model_name='page',
            old_name='menu',
            new_name='in_menu',
        ),
    ]
