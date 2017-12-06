# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='NetaxeptPayment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('transaction_id', models.CharField(max_length=32)),
                ('amount', models.IntegerField(null=True, blank=True)),
                ('currencycode', models.CharField(max_length=3)),
                ('description', models.CharField(max_length=255)),
                ('ordernumber', models.CharField(max_length=32)),
                ('flagged', models.BooleanField(default=False)),
                ('responsecode', models.CharField(max_length=3, null=True, blank=True)),
                ('responsesource', models.CharField(max_length=20, null=True, blank=True)),
                ('responsetext', models.CharField(max_length=255, null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='NetaxeptTransaction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('transaction_id', models.CharField(max_length=32)),
                ('operation', models.CharField(max_length=7, choices=[(b'AUTH', b'AUTH'), (b'SALE', b'SALE'), (b'CAPTURE', b'CAPTURE'), (b'CREDIT', b'CREDIT'), (b'ANNUL', b'ANNUL')])),
                ('amount', models.PositiveIntegerField(null=True, blank=True)),
                ('flagged', models.BooleanField(default=False)),
                ('responsecode', models.CharField(max_length=3, null=True, blank=True)),
                ('responsesource', models.CharField(max_length=20, null=True, blank=True)),
                ('responsetext', models.CharField(max_length=255, null=True, blank=True)),
                ('payment', models.ForeignKey(to='djnetaxept.NetaxeptPayment')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
