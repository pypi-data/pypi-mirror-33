# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('navsy', '0013_remove_route_redirect_to_first_child_page'),
    ]

    operations = [
        migrations.AddField(
            model_name='page',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Draft'), (2, 'Published'), (0, 'Unpublished')], default=1),
        ),
    ]
