# Generated by Django 5.1 on 2024-10-16 03:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0011_studentanswer_quiz_id_alter_quiz_total_questions'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentanswer',
            name='is_mark',
            field=models.BooleanField(default=False),
        ),
    ]