# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lugar', '0003_pais_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='pais',
            name='latitud',
            field=models.DecimalField(null=True, verbose_name=b'Latitud', max_digits=8, decimal_places=5, blank=True),
        ),
        migrations.AddField(
            model_name='pais',
            name='longitud',
            field=models.DecimalField(null=True, verbose_name=b'Longitud', max_digits=8, decimal_places=5, blank=True),
        ),
    ]
