# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('navsy', '0010_added_regex_fields_to_route'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='route',
            unique_together=set([('page', 'regex')]),
        ),
        migrations.RemoveField(
            model_name='route',
            name='pattern',
        ),
        migrations.DeleteModel(
            name='Pattern',
        ),
    ]
