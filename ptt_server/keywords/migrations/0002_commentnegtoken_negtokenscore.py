# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-25 21:52
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('keywords', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommentNegToken',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.CharField(max_length=50, null=True, verbose_name='Date')),
            ],
        ),
        migrations.CreateModel(
            name='NegTokenScore',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.FloatField(null=True, verbose_name='Score')),
                ('token', models.CharField(max_length=50, null=True, verbose_name='Token')),
                ('CommentNegToken', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='keywords.CommentNegToken')),
            ],
        ),
    ]