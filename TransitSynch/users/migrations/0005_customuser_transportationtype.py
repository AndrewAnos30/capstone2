# Generated by Django 4.2.5 on 2023-11-08 16:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_alter_customuser_balance'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='TransportationType',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
