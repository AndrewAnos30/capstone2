# Generated by Django 4.2.5 on 2023-11-03 11:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Website', '0005_remove_cashiertransaction_datein'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cashiertransaction',
            name='TransactionID',
        ),
    ]
