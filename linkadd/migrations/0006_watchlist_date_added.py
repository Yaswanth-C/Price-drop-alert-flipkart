# Generated by Django 3.1.1 on 2020-12-29 15:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('linkadd', '0005_mailinglist'),
    ]

    operations = [
        migrations.AddField(
            model_name='watchlist',
            name='date_added',
            field=models.DateTimeField(auto_now_add=True, default='none'),
            preserve_default=False,
        ),
    ]
