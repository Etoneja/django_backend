# Generated by Django 3.1 on 2021-02-07 21:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0004_auto_20210207_2359'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userbookrelation',
            name='rate',
            field=models.PositiveIntegerField(choices=[(1, 'ok'), (2, 'fine'), (3, 'good'), (4, 'amazing'), (5, 'incredible')], null=True),
        ),
    ]
