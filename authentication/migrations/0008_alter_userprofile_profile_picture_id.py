# Generated by Django 5.1.2 on 2024-10-27 09:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0007_userprofile_profile_picture_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='profile_picture_id',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
    ]
