# Generated by Django 4.2.5 on 2023-11-03 11:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Website', '0006_remove_cashiertransaction_transactionid'),
    ]

    operations = [
        migrations.AddField(
            model_name='cashiertransaction',
            name='CashIn',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='cashiertransaction',
            name='CashierSN',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='cashiertransaction',
            name='CommuterSN',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='cashiertransaction',
            name='DateIn',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='cashiertransaction',
            name='TransactionID',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='cashiertransaction',
            name='change',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='cashiertransaction',
            name='paidAmount',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
    ]