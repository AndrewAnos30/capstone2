# Generated by Django 4.2.5 on 2023-10-03 08:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Website', '0008_datacrawl'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datacrawl',
            name='CrawlPHP',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='datacrawl',
            name='CrawlUSD',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
