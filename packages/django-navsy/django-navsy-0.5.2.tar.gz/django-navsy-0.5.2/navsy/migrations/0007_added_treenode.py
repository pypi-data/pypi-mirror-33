# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('navsy', '0006_removed_slug_uniqueness'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='page',
            options={'ordering': ['tn_order'], 'verbose_name': 'Page', 'verbose_name_plural': 'Pages'},
        ),
        migrations.RenameField(
            model_name='page',
            old_name='children_count',
            new_name='tn_children_count'
        ),
        migrations.RenameField(
            model_name='page',
            old_name='children_pks',
            new_name='tn_children_pks'
        ),
        migrations.RenameField(
            model_name='page',
            old_name='parent',
            new_name='tn_parent'
        ),
        migrations.RenameField(
            model_name='page',
            old_name='parents_count',
            new_name='tn_ancestors_count'
        ),
        migrations.RenameField(
            model_name='page',
            old_name='parents_pks',
            new_name='tn_ancestors_pks'
        ),
        migrations.RemoveField(
            model_name='page',
            name='priorities',
        ),
        migrations.RenameField(
            model_name='page',
            old_name='priority',
            new_name='tn_priority'
        ),
        migrations.RenameField(
            model_name='page',
            old_name='siblings_count',
            new_name='tn_siblings_count'
        ),
        migrations.RenameField(
            model_name='page',
            old_name='siblings_pks',
            new_name='tn_siblings_pks'
        ),
        migrations.AddField(
            model_name='page',
            name='tn_depth',
            field=models.PositiveSmallIntegerField(default=0, editable=False, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(10)], verbose_name='Depth'),
        ),
        migrations.AddField(
            model_name='page',
            name='tn_descendants_count',
            field=models.PositiveSmallIntegerField(default=0, editable=False, verbose_name='Descendants count'),
        ),
        migrations.AddField(
            model_name='page',
            name='tn_descendants_pks',
            field=models.CharField(blank=True, default='', editable=False, max_length=500, verbose_name='Descendants pks'),
        ),
        migrations.AddField(
            model_name='page',
            name='tn_index',
            field=models.PositiveSmallIntegerField(default=0, editable=False, verbose_name='Index'),
        ),
        migrations.AddField(
            model_name='page',
            name='tn_level',
            field=models.PositiveSmallIntegerField(default=0, editable=False, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(10)], verbose_name='Level'),
        ),
        migrations.AddField(
            model_name='page',
            name='tn_order',
            field=models.PositiveSmallIntegerField(default=0, editable=False, verbose_name='Order'),
        ),
        migrations.AlterField(
            model_name='page',
            name='tn_ancestors_count',
            field=models.PositiveSmallIntegerField(default=0, editable=False, verbose_name='Ancestors count'),
        ),
        migrations.AlterField(
            model_name='page',
            name='tn_ancestors_pks',
            field=models.CharField(blank=True, default='', editable=False, max_length=500, verbose_name='Ancestors pks'),
        ),
        migrations.AlterField(
            model_name='page',
            name='tn_children_count',
            field=models.PositiveSmallIntegerField(default=0, editable=False, verbose_name='Children count'),
        ),
        migrations.AlterField(
            model_name='page',
            name='tn_children_pks',
            field=models.CharField(blank=True, default='', editable=False, max_length=500, verbose_name='Children pks'),
        ),
        migrations.AlterField(
            model_name='page',
            name='tn_parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tn_children', to='navsy.Page', verbose_name='Parent'),
        ),
        migrations.AlterField(
            model_name='page',
            name='tn_priority',
            field=models.PositiveSmallIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(9999)], verbose_name='Priority'),
        ),
        migrations.AlterField(
            model_name='page',
            name='tn_siblings_count',
            field=models.PositiveSmallIntegerField(default=0, editable=False, verbose_name='Siblings count'),
        ),
        migrations.AlterField(
            model_name='page',
            name='tn_siblings_pks',
            field=models.CharField(blank=True, default='', editable=False, max_length=500, verbose_name='Siblings pks'),
        ),
    ]
