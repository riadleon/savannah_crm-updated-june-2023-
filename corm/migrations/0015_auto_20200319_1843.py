# Generated by Django 3.0.4 on 2020-03-19 18:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('corm', '0014_auto_20200319_1838'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activity',
            name='location',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='activitytype',
            name='feed',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='source',
            name='connector',
            field=models.CharField(choices=[('corm.plugins.email', 'Email'), ('corm.plugins.slack', 'Slack'), ('corm.plugins.discourse', 'Discourse'), ('corm.plugins.rss', 'RSS')], max_length=256),
        ),
    ]