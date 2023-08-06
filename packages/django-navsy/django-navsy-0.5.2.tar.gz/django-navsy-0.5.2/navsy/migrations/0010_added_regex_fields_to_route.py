# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('navsy', '0009_updated_treenode_level_default'),
    ]

    operations = [
        migrations.AddField(
            model_name='route',
            name='regex',
            field=models.CharField(blank=True, choices=[[b'', b'<blank>'], [b'(?P<date_day>((0|1|2)?([1-9])|[1-3]0|31))', b'<date_day>'], [b'(?P<date_month>(0?([1-9])|10|11|12))', b'<date_month>'], [b'(?P<date_year>[\\d]{4})', b'<date_year>'], [b'(?P<date_year>[\\d]{4})(?P<date_month>(0?([1-9])|10|11|12))', b'<date_year><date_month>'], [b'(?P<date_year>[\\d]{4})(?P<date_month>(0?([1-9])|10|11|12))(?P<date_day>((0|1|2)?([1-9])|[1-3]0|31))', b'<date_year><date_month><date_day>'], [b'(?P<date_year>[\\d]{4})-(?P<date_month>(0?([1-9])|10|11|12))-(?P<date_day>((0|1|2)?([1-9])|[1-3]0|31))', b'<date_year>-<date_month>-<date_day>'], [b'(?P<date_year>[\\d]{4})/(?P<date_month>(0?([1-9])|10|11|12))', b'<date_year>/<date_month>'], [b'(?P<date_year>[\\d]{4})/(?P<date_month>(0?([1-9])|10|11|12))/(?P<date_day>((0|1|2)?([1-9])|[1-3]0|31))', b'<date_year>/<date_month>/<date_day>'], [b'(?P<email>(([a-z\\d]+([\\.\\_]{1}[a-z\\d]+)?){6})\\@([a-z\\d]+([\\.\\_\\-]{1}[a-z\\d]+){1,}[a-z]+))', b'<email>'], [b'(?P<email_username>([a-z\\d]+([\\.\\_]{1}[a-z\\d]+)?){6})\\@(?P<email_domain>[a-z\\d]+([\\.\\_\\-]{1}[a-z\\d]+){1,}[a-z]+)', b'<email_username>@<email_domain>'], [b'(?P<file_name>[\\w-]+).(?P<file_ext>[\\w]+)', b'<file_name>.<file_ext>'], [b'(?P<id>[\\d]+)', b'<id>'], [b'(?P<id>[\\d]+)/(?P<slug>[\\w-]+)', b'<id>/<slug>'], [b'(?P<page>[\\d]+)', b'<page>'], [b'(?P<slug>[\\w-]+)', b'<slug>'], [b'(?P<slug_parent>[\\w-]+)/(?P<slug>[\\w-]+)', b'<slug_parent>/<slug>'], [b'(?P<username>[\\w.@-]+)', b'<username>'], [b'(?P<uuid>[a-fA-F0-9]{8}-?[a-fA-F0-9]{4}-?[1345][a-fA-F0-9]{3}-?[a-fA-F0-9]{4}-?[a-fA-F0-9]{12})', b'<uuid>'], [b'(?P<version>[\\d]+(\\.[\\d]+)+)', b'<version>'], [b'(?P<version_major>[\\d]+)\\.(?P<version_minor>[\\d]+)', b'<version_major>.<version_minor>'], [b'(?P<version_major>[\\d]+)\\.(?P<version_minor>[\\d]+)\\.(?P<version_build>[\\d]+)', b'<version_major>.<version_minor>.<version_build>'], [b'by-(?P<slug>[\\w-]+)', b'by-<slug>'], [b'login', b'login'], [b'logout', b'logout']], default='', max_length=255),
        ),
        migrations.AddField(
            model_name='route',
            name='regex_display',
            field=models.CharField(blank=True, default='', editable=False, max_length=255),
        ),
        migrations.AddField(
            model_name='route',
            name='regex_format',
            field=models.CharField(blank=True, default='', editable=False, max_length=255),
        ),
    ]
