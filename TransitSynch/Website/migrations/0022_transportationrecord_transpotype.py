# Generated by Django 4.2.5 on 2023-11-08 17:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Website', '0021_alter_transportationrecord_commuterstatus'),
    ]

    operations = [
        migrations.AddField(
            model_name='transportationrecord',
            name='TranspoType',
            field=models.CharField(blank=True, max_length=25, null=True),
        ),
    ]
