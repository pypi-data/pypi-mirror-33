# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('navsy', '0014_page_status'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='route',
            options={'ordering': ['page', '-priority', 'regex'], 'verbose_name': 'Route', 'verbose_name_plural': 'Routes'},
        ),
    ]
