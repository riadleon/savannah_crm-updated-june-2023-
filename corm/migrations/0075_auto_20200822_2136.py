# Generated by Django 3.0.4 on 2020-08-22 21:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('corm', '0074_auto_20200730_1417'),
    ]

    operations = [
        migrations.AlterField(
            model_name='member',
            name='role',
            field=models.CharField(choices=[('staff', 'Staff'), ('bot', 'Bot')], default='community', max_length=32),
        ),
        migrations.AlterField(
            model_name='source',
            name='connector',
            field=models.CharField(choices=[('corm.plugins.null', 'Manual Entry'), ('corm.plugins.reddit', 'Reddit'), ('corm.plugins.twitter', 'Twitter'), ('corm.plugins.discourse', 'Discourse'), ('corm.plugins.slack', 'Slack'), ('corm.plugins.discord', 'Discord'), ('corm.plugins.github', 'Github'), ('corm.plugins.gitlab', 'Gitlab'), ('corm.plugins.rss', 'RSS')], max_length=256),
        ),
        migrations.AlterField(
            model_name='userauthcredentials',
            name='connector',
            field=models.CharField(choices=[('corm.plugins.null', 'Manual Entry'), ('corm.plugins.reddit', 'Reddit'), ('corm.plugins.twitter', 'Twitter'), ('corm.plugins.discourse', 'Discourse'), ('corm.plugins.slack', 'Slack'), ('corm.plugins.discord', 'Discord'), ('corm.plugins.github', 'Github'), ('corm.plugins.gitlab', 'Gitlab'), ('corm.plugins.rss', 'RSS')], max_length=256),
        ),
        migrations.CreateModel(
            name='MemberWatch',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start', models.DateTimeField(auto_now_add=True)),
                ('end', models.DateTimeField(blank=True, null=True)),
                ('level', models.SmallIntegerField(choices=[(10, 'debug'), (20, 'info'), (25, 'success'), (30, 'warning'), (40, 'error')], default=30)),
                ('manager', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='corm.Member')),
            ],
        ),
    ]
