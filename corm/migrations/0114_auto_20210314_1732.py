# Generated by Django 3.0.4 on 2021-03-14 17:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('corm', '0113_suggesttag'),
    ]

    operations = [
        migrations.AddField(
            model_name='memberlevel',
            name='contribution_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='memberlevel',
            name='conversation_count',
            field=models.IntegerField(default=0),
        ),
    ]