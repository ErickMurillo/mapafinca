# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import smart_selects.db_fields


class Migration(migrations.Migration):

    dependencies = [
        ('encuestas', '0011_auto_20160414_1655'),
    ]

    operations = [
        migrations.AddField(
            model_name='cultivosfrutasfinca',
            name='iniciativas',
            field=models.IntegerField(blank=True, null=True, choices=[(1, b'Si'), (2, b'No')]),
        ),
        migrations.AddField(
            model_name='cultivoshuertosfamiliares',
            name='iniciativas',
            field=models.IntegerField(blank=True, null=True, choices=[(1, b'Si'), (2, b'No')]),
        ),
        migrations.AddField(
            model_name='cultivostradicionales',
            name='iniciativas',
            field=models.IntegerField(blank=True, null=True, choices=[(1, b'Si'), (2, b'No')]),
        ),
        migrations.AddField(
            model_name='ganaderia',
            name='iniciativas',
            field=models.IntegerField(blank=True, null=True, choices=[(1, b'Si'), (2, b'No')]),
        ),
        migrations.AddField(
            model_name='procesamiento',
            name='iniciativas',
            field=models.IntegerField(blank=True, null=True, choices=[(1, b'Si'), (2, b'No')]),
        ),
        migrations.AlterField(
            model_name='organizacionresp',
            name='departamento',
            field=smart_selects.db_fields.ChainedForeignKey(auto_choose=True, to='lugar.Departamento', chained_model_field=b'pais', chained_field=b'pais', null=True),
        ),
        migrations.AlterField(
            model_name='organizacionresp',
            name='municipio',
            field=smart_selects.db_fields.ChainedForeignKey(auto_choose=True, to='lugar.Municipio', chained_model_field=b'departamento', chained_field=b'departamento', null=True),
        ),
    ]
