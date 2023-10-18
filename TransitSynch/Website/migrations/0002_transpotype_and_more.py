# Generated by Django 4.2.5 on 2023-10-16 21:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Website', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TranspoType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.RenameField(
            model_name='currentprice',
            old_name='CurrentFare',
            new_name='CurrentFarePUJ',
        ),
        migrations.RenameField(
            model_name='currentprice',
            old_name='CurrentSucceeding',
            new_name='CurrentSucceedingPUJ',
        ),
    ]
