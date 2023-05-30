# Generated by Django 3.0.4 on 2020-08-26 12:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('corm', '0075_auto_20200822_2136'),
    ]

    operations = [
        migrations.AddField(
            model_name='source',
            name='enabled',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='member',
            name='role',
            field=models.CharField(choices=[('community', 'Community'), ('staff', 'Staff'), ('bot', 'Bot')], default='community', max_length=32),
        ),
    ]
