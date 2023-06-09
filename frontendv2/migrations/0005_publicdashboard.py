# Generated by Django 3.1.2 on 2021-07-25 15:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('corm', '0127_auto_20210709_1610'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('frontendv2', '0004_auto_20210317_1608'),
    ]

    operations = [
        migrations.CreateModel(
            name='PublicDashboard',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('page', models.CharField(choices=[('overview', 'Overview'), ('members', 'Members'), ('conversation', 'Conversations'), ('contributions', 'Contributions')], max_length=32)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('view_count', models.PositiveBigIntegerField(default=0)),
                ('show_companies', models.BooleanField(default=False, help_text='Show company names.')),
                ('show_members', models.BooleanField(default=False, help_text='Show member names and affiliation (but not contact info).')),
                ('pin_time', models.BooleanField(default=False, help_text='Show data from the time the dashboard was created, not the time it was viewed.')),
                ('filters', models.JSONField()),
                ('community', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='corm.community')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
