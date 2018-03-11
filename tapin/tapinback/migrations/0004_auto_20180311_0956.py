# Generated by Django 2.0.3 on 2018-03-11 09:56

from django.db import migrations, models
import tapinback.models


class Migration(migrations.Migration):

    dependencies = [
        ('tapinback', '0003_auto_20180311_0953'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tapuser',
            name='keys',
            field=models.CharField(default=tapinback.models.gen_keys, max_length=196),
        ),
        migrations.AlterField(
            model_name='tapuser',
            name='token',
            field=models.CharField(default=tapinback.models.gen_token, max_length=1024),
        ),
    ]
