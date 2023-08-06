# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('navsy', '0012_removed_regex_extra_fields'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='route',
            name='redirect_to_first_child_page',
        ),
    ]
