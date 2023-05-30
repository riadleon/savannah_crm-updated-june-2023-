# Generated by Django 3.0.4 on 2021-02-01 15:51

from django.db import migrations, models

def noop(apps, schema_editor):
    pass

def set_oldest_import(apps, schema_editor):
    Channel = apps.get_model('corm', 'Channel')
    for channel in Channel.objects.filter(oldest_import__isnull=True):
        channel.oldest_import = channel.first_import
        channel.save()

class Migration(migrations.Migration):

    dependencies = [
        ('corm', '0103_auto_20210129_1750'),
    ]

    operations = [
        migrations.AddField(
            model_name='channel',
            name='oldest_import',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.RunPython(set_oldest_import, noop),
    ]
