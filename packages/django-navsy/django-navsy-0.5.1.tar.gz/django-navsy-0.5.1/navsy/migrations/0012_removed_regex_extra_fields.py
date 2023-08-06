# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('navsy', '0011_removed_pattern_model'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='route',
            name='regex_display',
        ),
        migrations.RemoveField(
            model_name='route',
            name='regex_format',
        ),
    ]
