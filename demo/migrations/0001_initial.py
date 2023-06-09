# Generated by Django 3.0.14 on 2021-07-09 16:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('corm', '0127_auto_20210709_1610'),
    ]

    operations = [
        migrations.CreateModel(
            name='Demonstration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.SmallIntegerField(choices=[(0, 'Seed'), (1, 'Ready'), (2, 'In Use')], default=0)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('community', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='corm.Community')),
            ],
        ),
    ]
