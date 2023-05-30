# Generated by Django 3.0.4 on 2020-04-28 17:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('corm', '0043_channel_last_import'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='avatar_url',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='member',
            name='email_address',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='member',
            name='mailing_address',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='member',
            name='phone_number',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
    ]