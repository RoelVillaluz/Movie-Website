# Generated by Django 5.0.4 on 2024-08-07 10:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0018_movieimage'),
    ]

    operations = [
        migrations.AddField(
            model_name='actor',
            name='bio',
            field=models.TextField(default='No bio yet'),
        ),
    ]