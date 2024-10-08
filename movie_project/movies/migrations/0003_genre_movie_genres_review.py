# Generated by Django 5.0.4 on 2024-08-01 10:07

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0002_alter_movie_backdrop_path_alter_movie_poster_path'),
    ]

    operations = [
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('Action', 'Action'), ('Comedy', 'Comedy'), ('Drama', 'Drama'), ('Horror', 'Horror'), ('Romance', 'Romance'), ('Sci-Fi', 'Sci-Fi'), ('Thriller', 'Thriller'), ('Animation', 'Animation'), ('Marvel', 'Marvel'), ('DC', 'DC'), ('Fantasy', 'Fantasy'), ('Mystery', 'Mystery'), ('Crime', 'Crime'), ('Adventure', 'Adventure'), ('Documentary', 'Documentary'), ('Family', 'Family'), ('Musical', 'Musical'), ('Western', 'Western'), ('War', 'War'), ('History', 'History'), ('Biography', 'Biography'), ('Sport', 'Sport'), ('Music', 'Music'), ('Short', 'Short'), ('Indie', 'Indie'), ('Noir', 'Noir'), ('Superhero', 'Superhero')], max_length=24)),
            ],
        ),
        migrations.AddField(
            model_name='movie',
            name='genres',
            field=models.ManyToManyField(blank=True, to='movies.genre'),
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.IntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10)])),
                ('movie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='movies.movie')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
