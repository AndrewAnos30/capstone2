# Generated by Django 4.2.5 on 2023-09-21 07:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Website', '0004_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Routes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Rname', models.CharField(max_length=50)),
            ],
        ),
    ]
