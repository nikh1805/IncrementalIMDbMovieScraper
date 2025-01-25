from django.db import models


class Tag(models.Model):
    """ Represents a tag that can be either a genre or a keyword associated with movies. """
    name = models.CharField(max_length=255, unique=True, db_index=True, help_text="Name of the tag (genre or keyword).")
    movies_count = models.IntegerField(default=0, help_text="Number of movies associated with this tag.")
    is_genre = models.BooleanField(default=True, help_text="True if the tag represents a genre, False for a keyword.")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp when the tag was created.")
    updated_at = models.DateTimeField(auto_now=True, help_text="Timestamp when the tag was last updated.")

    def __str__(self):
        """ String representation. """
        return f"{self.name} | {self.movies_count} | Tag:{'Genre' if self.is_genre else 'Keyword'}"

    @classmethod
    def create_or_update_tag(cls, name, count, is_genre):
        """
        Updates or creates a genre with the provided name and count.
        Args:
            name (str): Name of the genre.
            count (int): Count associated with the genre or keyword.
            is_genre(bool): True if genre, false if keyword
        Returns:
            Genre: The updated or newly created tag instance.
        """
        tag, created = cls.objects.update_or_create(name=name, defaults={"movies_count": count, "is_genre": is_genre})
        return tag


class Movies(models.Model):
    """ Represents a movie and its related information, including genres, keywords, and details. """
    title = models.CharField(max_length=255, unique=True, db_index=True, help_text="The title of the movie.")
    director = models.JSONField(help_text="JSON field storing director details.")
    cast = models.JSONField(help_text="JSON field storing cast details.")
    rating = models.FloatField(help_text="The movie's rating.")
    year = models.IntegerField(help_text="The year the movie was released.")
    summary = models.TextField(help_text="Plot summary or description of the movie.")
    tags = models.ManyToManyField(Tag, related_name='movies',
                                  help_text="Genres and keywords associated with the movie.")

    def __str__(self):
        return self.title

    @classmethod
    def create_or_update(cls, movies_data):
        """
        create or update movies.
        Args:
            movies_data (list of dict): A list of dictionaries containing movie details.
        Returns:
            list: A list of movie objects created or updated.
        """
        # Extract titles to check for existing movies
        titles = [movie_data["title"] for movie_data in movies_data]
        # Get the existing movies to perform updates on
        existing_movies = cls.objects.filter(title__in=titles)
        existing_movies_dict = {movie.title: movie for movie in existing_movies}

        movies_to_update = []
        for movie_data in movies_data:
            # Check if the movie already exists
            existing_movie = existing_movies_dict.get(movie_data["title"])
            if existing_movie:
                # Update existing movie
                existing_movie.director = movie_data["directors"]
                existing_movie.cast = movie_data["casts"]
                existing_movie.rating = movie_data["rating"]
                existing_movie.year = movie_data["year"]
                existing_movie.summary = movie_data["plot_summary"]
                movies_to_update.append(existing_movie)
            else:
                # Create new movie
                movie = cls(
                    title=movie_data["title"],
                    director=movie_data["directors"],
                    cast=movie_data["casts"],
                    rating=movie_data["rating"],
                    year=movie_data["year"],
                    summary=movie_data["plot_summary"])
                movie.save()
                tags = Tag.objects.filter(
                    name__in=[tag_name for tag_name in movie_data["genres"] + movie_data["keywords"]])
                movie.tags.set(list(tags.values_list('id', flat=True)))

        print("Movies create and update is completed")
