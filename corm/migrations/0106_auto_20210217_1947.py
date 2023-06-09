# Generated by Django 3.0.4 on 2021-02-17 19:47

from django.db import migrations, models
import django.db.models.deletion

def noop(apps, schema_editor):
    pass

def backward(apps, schema_editor):
    Conversation = apps.get_model('corm', 'Conversation')
    Contribution = apps.get_model('corm', 'Contribution')
    for convo in Conversation.objects.filter(contribution__isnull=False):
        convo.contribution.conversation = convo
        convo.contribution.save()

def forward(apps, schema_editor):
    Conversation = apps.get_model('corm', 'Conversation')
    Contribution = apps.get_model('corm', 'Contribution')
    print("Setting Conversation.contribution based on Contribution.conversation")
    for contrib in Contribution.objects.filter(conversation__isnull=False):
        contrib.conversation.contribution = contrib
        contrib.conversation.save()

    print("Attempting to match Contributions without a conversation")
    for contrib in Contribution.objects.filter(conversation__isnull=True):
        try:
            convo = Conversation.objects.get(channel=contrib.channel, speaker=contrib.author, timestamp=contrib.timestamp)
            convo.contribution = contrib
            convo.save()
            contrib.conversation = convo
            contrib.save()
        except:
            pass

class Migration(migrations.Migration):

    dependencies = [
        ('corm', '0105_auto_20210211_2135'),
    ]

    operations = [
        migrations.AddField(
            model_name='conversation',
            name='contribution',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='new_contribution', to='corm.Contribution'),
        ),
        migrations.AlterField(
            model_name='contribution',
            name='conversation',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='old_contributions', to='corm.Conversation'),
        ),
        migrations.AlterField(
            model_name='source',
            name='connector',
            field=models.CharField(choices=[('corm.plugins.null', 'Manual Entry'), ('corm.plugins.api', 'API'), ('corm.plugins.discourse', 'Discourse'), ('corm.plugins.slack', 'Slack'), ('corm.plugins.discord', 'Discord'), ('corm.plugins.github', 'Github'), ('corm.plugins.gitlab', 'Gitlab'), ('corm.plugins.stackexchange', 'Stack Exchange'), ('corm.plugins.reddit', 'Reddit'), ('corm.plugins.rss', 'RSS')], max_length=256),
        ),
        migrations.AlterField(
            model_name='userauthcredentials',
            name='connector',
            field=models.CharField(choices=[('corm.plugins.null', 'Manual Entry'), ('corm.plugins.api', 'API'), ('corm.plugins.discourse', 'Discourse'), ('corm.plugins.slack', 'Slack'), ('corm.plugins.discord', 'Discord'), ('corm.plugins.github', 'Github'), ('corm.plugins.gitlab', 'Gitlab'), ('corm.plugins.stackexchange', 'Stack Exchange'), ('corm.plugins.reddit', 'Reddit'), ('corm.plugins.rss', 'RSS')], max_length=256),
        ),
        migrations.RunPython(forward, backward)
    ]
