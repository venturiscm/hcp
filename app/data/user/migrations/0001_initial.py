# Generated by Django 2.1.7 on 2019-04-02 04:24

import data.user.models
from django.db import migrations, models
import systems.models.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('group', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('created', models.DateTimeField(editable=False, null=True)),
                ('updated', models.DateTimeField(editable=False, null=True)),
                ('id', models.CharField(editable=False, max_length=64, primary_key=True, serialize=False)),
                ('name', models.CharField(editable=False, max_length=256)),
                ('config', systems.models.fields.EncryptedDataField(default={}, editable=False)),
                ('provider_type', models.CharField(editable=False, max_length=128, null=True)),
                ('variables', systems.models.fields.EncryptedDataField(default={}, editable=False)),
                ('state_config', systems.models.fields.EncryptedDataField(default={}, editable=False)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('email', models.EmailField(max_length=254, null=True)),
                ('first_name', models.CharField(max_length=30, null=True)),
                ('last_name', models.CharField(max_length=150, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('groups', models.ManyToManyField(related_name='user_relation', to='group.Group')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'db_table': 'core_user',
                'ordering': ['name'],
                'abstract': False,
            },
            managers=[
                ('objects', data.user.models.UserManager()),
            ],
        ),
    ]
