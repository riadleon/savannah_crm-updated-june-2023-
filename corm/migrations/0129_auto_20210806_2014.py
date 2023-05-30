# Generated by Django 3.1.2 on 2021-08-06 20:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('corm', '0128_auto_20210806_1825'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='channels',
            field=models.ManyToManyField(blank=True, help_text="Any activity in these channels will be included in this project's activity", to='corm.Channel'),
        ),
        migrations.AlterField(
            model_name='project',
            name='tag',
            field=models.ForeignKey(blank=True, help_text="Any content with this tag will be included in this project's activity", null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='projects_by_content', to='corm.tag'),
        ),
    ]
