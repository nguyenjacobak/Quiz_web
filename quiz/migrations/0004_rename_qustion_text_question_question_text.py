# Generated by Django 5.1.1 on 2024-10-09 03:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0003_rename_quiz_question_quiz_id_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='question',
            old_name='qustion_text',
            new_name='question_text',
        ),
    ]