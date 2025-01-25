from django_q.tasks import async_task
from django.conf import settings

from scraper_core.incremental_movie_scraper import IncrementalMovieScraper
from scraper_core.genre_keywords_scraper import GenreKeywordScraper

from movie_scraper_app.models import Movies, Tag


def scrape_movies(movies_count: int, genre: str = None, keyword: str = None):
    """
    Scrape first batch of movie data and return first cut data to a user and rest of all data
    fetch and update in background asynchronously.
    """
    movie_page_size = settings.MOVIES_PAGE_SIZE
    first_load_movie_size = settings.FIRST_LOAD_MOVIE_SIZE
    inc_scraper = IncrementalMovieScraper(movies_count, genre, keyword, movie_page_size)
    initial_movies_data = inc_scraper.scrape_first_batch_data(first_load_movie_size)
    # Insert first batch of movies into the database
    Movies.create_or_update(initial_movies_data)

    # Compute clicks and parse count required for rest of the movies
    first_load_left_movies = min(movie_page_size, movies_count) - first_load_movie_size
    clicks_and_parse_count = inc_scraper.compute_clicks_and_parse_count_required(
        first_load_left_movies, settings.MAX_CLICKS_PER_REQUEST)
    print(f"Clicks and Parse Count: {clicks_and_parse_count}")

    # Submit each iteration as a task to Django Q for parallel execution
    task_ids = []
    for num_of_clicks, parse_movies_data_count in clicks_and_parse_count:
        task_id = async_task('movie_scraper_app.movie_scraper_adapter.scrape_batch_task',
                             movies_count, genre, keyword, movie_page_size, num_of_clicks,
                             parse_movies_data_count)
        print(f"Submitted the movies for scraping asynchronously. "
              f"{task_id}, Clicks:{num_of_clicks}, Parse Movies Count: {parse_movies_data_count}")
        task_ids.append(task_id)


def scrape_batch_task(movies_count: int, genre: str, keyword: str, movie_page_size: int,
                      num_of_clicks: int, parse_movies_data_count: int):
    """ Scrape batch task is an asynchronous task for scraping movies"""
    inc_scraper = IncrementalMovieScraper(movies_count, genre, keyword, movie_page_size)
    movies_data = inc_scraper.batch_scrape(num_of_clicks, parse_movies_data_count, movie_page_size)
    # Insert all batch of movies into the database
    Movies.create_or_update(movies_data)
    print(f"Asynchronous batch scrape data completed.  Movies Data Count: {len(movies_data)}")
    return movies_data


def scrape_genre_and_keywords():
    """ Scrapes genre and keyword data with core scraper and updates the database."""
    gk_scraper = GenreKeywordScraper(settings.MOVIES_PAGE_SIZE)
    scraped_data = gk_scraper.scrape()
    # Update or create genres
    for genre in scraped_data.get("genres", []):
        Tag.create_or_update_tag(name=genre["name"], count=genre["count"], is_genre=True)
    # Update or create keywords
    for keyword in scraped_data.get("keywords", []):
        Tag.create_or_update_tag(name=keyword["name"], count=keyword["count"], is_genre=False)
