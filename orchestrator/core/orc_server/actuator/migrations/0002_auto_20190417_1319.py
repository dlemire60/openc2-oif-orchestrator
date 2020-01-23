# Generated by Django 2.2 on 2019-04-17 13:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('actuator', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='actuator',
            name='schema_format',
            field=models.CharField(choices=[('jadn', 'JADN'), ('json', 'JSON')], default='jadn', help_text='Format of the schema (JADN|JSON), set from the schema', max_length=4),
        ),
        migrations.AlterField(
            model_name='actuator',
            name='profile',
            field=models.CharField(default='N/A', help_text='Profile of the actuator, set from the schema', max_length=60),
        ),
    ]
