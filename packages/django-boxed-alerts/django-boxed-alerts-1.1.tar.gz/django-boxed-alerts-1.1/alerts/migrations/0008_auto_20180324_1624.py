# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alerts', '0007_useralertsetting_filter_value'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alerttype',
            name='slug',
            field=models.CharField(unique=True, max_length=128, verbose_name='URL Slug'),
        ),
        migrations.AlterField(
            model_name='useralertobject',
            name='name',
            field=models.CharField(max_length=128),
        ),
        migrations.AlterField(
            model_name='useralertvalue',
            name='name',
            field=models.CharField(max_length=128),
        ),
    ]
