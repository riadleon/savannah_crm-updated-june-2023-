# Generated by Django 3.0.4 on 2020-03-19 19:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('corm', '0016_auto_20200319_1935'),
    ]

    operations = [
        migrations.AddField(
            model_name='conversation',
            name='location',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='source',
            name='connector',
            field=models.CharField(choices=[('corm.plugins.null', 'None'), ('corm.plugins.email', 'Email'), ('corm.plugins.slack', 'Slack'), ('corm.plugins.discourse', 'Discourse'), ('corm.plugins.rss', 'RSS'), ('corm.plugins.reddit', 'Reddit')], max_length=256),
        ),
    ]
