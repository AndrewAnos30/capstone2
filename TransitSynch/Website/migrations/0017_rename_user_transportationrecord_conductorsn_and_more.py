# Generated by Django 4.2.5 on 2023-11-08 16:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Website', '0016_delete_location_delete_route'),
    ]

    operations = [
        migrations.RenameField(
            model_name='transportationrecord',
            old_name='user',
            new_name='conductorSN',
        ),
        migrations.AddField(
            model_name='transportationrecord',
            name='commuterSN',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
