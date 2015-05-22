# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jobs.models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0002_auto_20150522_1009'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exportformat',
            name='slug',
            field=jobs.models.LowerCaseCharField(default='', unique=True, max_length=7),
        ),
    ]
