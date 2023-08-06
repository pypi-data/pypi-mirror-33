# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings
import cmsplugin_diff.models


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0016_auto_20160608_1535'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='EditHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('plugin_id', models.IntegerField(db_index=True)),
                ('comment', models.CharField(max_length=255, null=True, verbose_name='User Comment')),
                ('content', models.TextField(verbose_name='Current Plugin Content')),
                ('language', models.CharField(max_length=8, null=True, verbose_name='Plugin Language', choices=[(b'ar', b'Arabic'), (b'en', b'English'), (b'de', b'German'), (b'da', b'Danish'), (b'fr', b'French'), (b'nl', b'Dutch'), (b'it', b'Italian'), (b'es', b'Spanish'), (b'pt', b'Portuguese'), (b'pt-br', b'Brazilian Portuguese'), (b'cs', b'Czech'), (b'ru', b'Russian'), (b'sk', b'Slovak'), (b'ja', b'Japanese'), (b'zh', b'Simplified Chinese'), (b'zh-hant', b'Traditional Chinese'), (b'ko', b'Korean')])),
                ('page', models.ForeignKey(related_name='edit_history', on_delete=django.db.models.deletion.SET_NULL, to='cms.Page', null=True)),
            ],
            options={
                'ordering': ('-date',),
                'get_latest_by': 'date',
            },
        ),
        migrations.CreateModel(
            name='PublishHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('language', models.CharField(max_length=8, null=True, verbose_name='Page Language', choices=[(b'ar', b'Arabic'), (b'en', b'English'), (b'de', b'German'), (b'da', b'Danish'), (b'fr', b'French'), (b'nl', b'Dutch'), (b'it', b'Italian'), (b'es', b'Spanish'), (b'pt', b'Portuguese'), (b'pt-br', b'Brazilian Portuguese'), (b'cs', b'Czech'), (b'ru', b'Russian'), (b'sk', b'Slovak'), (b'ja', b'Japanese'), (b'zh', b'Simplified Chinese'), (b'zh-hant', b'Traditional Chinese'), (b'ko', b'Korean')])),
                ('page', models.ForeignKey(related_name='publish_history', on_delete=django.db.models.deletion.SET_NULL, to='cms.Page', null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.SET(cmsplugin_diff.models.get_deleted_user))),
            ],
            options={
                'ordering': ('-date',),
                'get_latest_by': 'date',
            },
        ),
        migrations.AddField(
            model_name='edithistory',
            name='published_in',
            field=models.ForeignKey(related_name='editings', blank=True, to='cmsplugin_diff.PublishHistory', null=True),
        ),
        migrations.AddField(
            model_name='edithistory',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.SET(cmsplugin_diff.models.get_deleted_user)),
        ),
    ]
