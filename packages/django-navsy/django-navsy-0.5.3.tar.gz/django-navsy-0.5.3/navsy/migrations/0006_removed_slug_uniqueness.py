# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import autoslug.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('navsy', '0005_page_slug_unique_with_parent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='page',
            name='slug',
            field=autoslug.fields.AutoSlugField(blank=True, editable=False, null=True, populate_from='name'),
        ),
    ]
