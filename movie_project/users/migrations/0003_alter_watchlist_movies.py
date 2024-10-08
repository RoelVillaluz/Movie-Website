# Generated by Django 5.0.4 on 2024-08-15 09:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0028_alter_award_category_alter_movie_overview'),
        ('users', '0002_watchlist_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='watchlist',
            name='movies',
            field=models.ManyToManyField(blank=True, null=True, related_name='watchlists', to='movies.movie'),
        ),
    ]
