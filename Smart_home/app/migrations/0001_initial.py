# Generated by Django 4.2.2 on 2023-06-10 16:22

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Devices',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('mac', models.CharField(max_length=17)),
                ('localization', models.CharField(max_length=30)),
                ('type', models.CharField(max_length=8)),
                ('value', models.CharField(max_length=20)),
            ],
        ),
    ]
