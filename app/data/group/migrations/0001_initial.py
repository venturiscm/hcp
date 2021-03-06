# Generated by Django 3.2.5 on 2021-07-13 07:03

from django.db import migrations, models
import django.db.models.deletion
import systems.models.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('created', models.DateTimeField(editable=False, null=True)),
                ('updated', models.DateTimeField(editable=False, null=True)),
                ('id', models.CharField(editable=False, max_length=64, primary_key=True, serialize=False)),
                ('name', models.CharField(editable=False, max_length=256)),
                ('config', systems.models.fields.EncryptedDataField(default={}, editable=False)),
                ('provider_type', models.CharField(editable=False, max_length=128, null=True)),
                ('variables', systems.models.fields.EncryptedDataField(default={}, editable=False)),
                ('state_config', systems.models.fields.EncryptedDataField(default={}, editable=False)),
                ('parent', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='group_relation', to='group.group')),
            ],
            options={
                'verbose_name': 'group',
                'verbose_name_plural': 'groups',
                'db_table': 'core_group',
                'ordering': ['name'],
                'abstract': False,
            },
        ),
    ]
