from __future__ import unicode_literals

import aboutconfig.utils
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Config',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(help_text='Period separated strings. All keys are case-insensitive.', max_length=512, unique=True, validators=[django.core.validators.RegexValidator('^(\\w+\\.)*\\w+$')], verbose_name='Key')),
                ('key_namespace', models.CharField(db_index=True, max_length=512, verbose_name='Key namespace')),
                ('value', models.CharField(blank=True, max_length=1024, null=True, verbose_name='Value')),
                ('default_value', models.CharField(editable=False, help_text='Default value set by setting provider. Used by 3rd-party apps.', max_length=1024, verbose_name='Default value')),
                ('allow_template_use', models.BooleanField(default=True, help_text='Prevent settings from being accessible via the template filter. Can be useful for API-keys, for example', verbose_name='Allow template use')),
            ],
            options={
                'ordering': ('key', 'value', 'default_value'),
                'verbose_name': 'Config',
            },
        ),
        migrations.CreateModel(
            name='DataType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32, verbose_name='Name')),
                ('serializer_class', models.CharField(help_text='Must be a class that implements serialize, unserialize and validate methods.', max_length=256, validators=[aboutconfig.utils.serializer_validator], verbose_name='Serializer class')),
                ('widget_class', models.CharField(blank=True, help_text='Widget class used to edit values of this data type. TextInput by default.', max_length=256, verbose_name='Widget class')),
                ('widget_args_raw', models.CharField(default='{}', help_text='Additional data for the value field widget (JSON).', max_length=1024, verbose_name='Raw widget arguments')),
            ],
            options={
                'verbose_name': 'Data-type',
            },
        ),
        migrations.AddField(
            model_name='config',
            name='data_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='aboutconfig.DataType', verbose_name='Data-type'),
        ),
    ]
