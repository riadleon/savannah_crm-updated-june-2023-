# Generated by Django 3.0.4 on 2020-03-25 15:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('corm', '0026_auto_20200325_1547'),
    ]

    operations = [
        migrations.AddField(
            model_name='activity',
            name='origin_id',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='channel',
            name='origin_id',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='contact',
            name='origin_id',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='conversation',
            name='origin_id',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
    ]
