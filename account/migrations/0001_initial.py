# Generated by Django 5.1.1 on 2024-10-05 16:41

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bio', models.TextField(blank=True, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True, unique=True)),
                ('profile_img', models.ImageField(blank=True, default='/static/images/user.jpg', null=True, upload_to='profile_images', verbose_name='Profile Pic')),
                ('studen_id', models.CharField(blank=True, max_length=15, null=True)),
                ('gender', models.CharField(blank=True, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], max_length=6, null=True)),
                ('user', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='User Object')),
            ],
        ),
    ]