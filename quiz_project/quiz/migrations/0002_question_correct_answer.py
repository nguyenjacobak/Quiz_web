# Generated by Django 5.1.1 on 2024-10-08 18:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='correct_answer',
            field=models.TextField(blank=True, null=True),
        ),
    ]
