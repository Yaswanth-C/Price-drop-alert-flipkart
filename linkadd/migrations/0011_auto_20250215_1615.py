# Generated by Django 3.1.14 on 2025-02-15 10:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('linkadd', '0010_auto_20250213_2218'),
    ]

    operations = [
        migrations.AlterField(
            model_name='watchlist',
            name='product_name',
            field=models.TextField(),
        ),
    ]
