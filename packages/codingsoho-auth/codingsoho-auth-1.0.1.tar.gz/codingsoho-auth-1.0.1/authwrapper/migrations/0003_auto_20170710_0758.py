# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authwrapper', '0002_wechatuserprofile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='myuser',
            name='account_type',
            field=models.CharField(default='username', max_length=50, null=True, blank=True, choices=[('username', 'Username'), ('mail', 'Mail'), ('phone', 'Phone')]),
        ),
    ]
