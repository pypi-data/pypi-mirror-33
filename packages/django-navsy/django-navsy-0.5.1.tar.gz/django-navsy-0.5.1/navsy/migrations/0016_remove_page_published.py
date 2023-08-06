# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('navsy', '0015_fixed_route_default_ordering'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='page',
            name='published',
        ),
    ]
