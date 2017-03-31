# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('encuestas', '0013_auto_20161005_1731'),
    ]

    operations = [
        migrations.AddField(
            model_name='encuesta',
            name='estacion',
            field=models.IntegerField(default=b'1', choices=[(1, b'Verano'), (2, b'Invierno')]),
        ),
    ]
