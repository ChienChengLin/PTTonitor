# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-05 15:32
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('id_query', '0011_graph_link_node'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserWordFreq',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.CharField(max_length=50, null=True, verbose_name='User')),
            ],
        ),
        migrations.CreateModel(
            name='WordFreq',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('word', models.TextField(null=True, verbose_name='Word')),
                ('freq', models.IntegerField(null=True, verbose_name='Freq')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='id_query.UserWordFreq')),
            ],
        ),
    ]
