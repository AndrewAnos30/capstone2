# Generated by Django 4.2.5 on 2023-11-05 13:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Website', '0009_rename_latitude_transportationrecord_latitudein_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='TransportationRecordOUT',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('longitudeOUT', models.FloatField(blank=True, null=True)),
                ('latitudeOUT', models.FloatField(blank=True, null=True)),
                ('extracted_data', models.TextField(blank=True, null=True)),
                ('scan_type', models.CharField(blank=True, max_length=20, null=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='transportationrecord',
            name='latitudeOUT',
        ),
        migrations.RemoveField(
            model_name='transportationrecord',
            name='longitudeOUT',
        ),
    ]
