# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('navsy', '0008_removed_autoslugfield'),
    ]

    operations = [
        migrations.AlterField(
            model_name='page',
            name='tn_level',
            field=models.PositiveSmallIntegerField(default=1, editable=False, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(10)], verbose_name='Level'),
        ),
    ]
