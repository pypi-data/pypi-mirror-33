# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-05-15 05:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bee_django_course', '0028_course_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='course/face', verbose_name='\u914d\u56fe'),
        ),
    ]
