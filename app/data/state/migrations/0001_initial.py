# Generated by Django 2.1.7 on 2019-04-02 04:24

from django.db import migrations, models
import django.db.models.deletion
import systems.models.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('environment', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='State',
            fields=[
                ('created', models.DateTimeField(editable=False, null=True)),
                ('updated', models.DateTimeField(editable=False, null=True)),
                ('id', models.CharField(editable=False, max_length=64, primary_key=True, serialize=False)),
                ('name', models.CharField(editable=False, max_length=256)),
                ('value', systems.models.fields.EncryptedDataField(null=True)),
                ('environment', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='state_relation', to='environment.Environment')),
            ],
            options={
                'verbose_name': 'state',
                'verbose_name_plural': 'states',
                'db_table': 'core_state',
                'ordering': ['name'],
                'abstract': False,
            },
        ),
        migrations.AlterUniqueTogether(
            name='state',
            unique_together={('environment', 'name')},
        ),
    ]
