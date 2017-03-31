# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('encuestas', '0012_auto_20160626_2340'),
    ]

    operations = [
        migrations.AlterField(
            model_name='genero',
            name='porcentaje',
            field=models.IntegerField(choices=[(1, b'10%'), (2, b'20%'), (3, b'30%'), (4, b'40%'), (5, b'50%'), (6, b'60%'), (7, b'70%'), (8, b'80%'), (9, b'90%'), (10, b'100%')]),
        ),
    ]
