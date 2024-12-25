# Generated by Django 5.1.2 on 2024-10-25 11:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0008_alter_question_created_at_alter_question_updated_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='question',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='reply',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='reply',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]