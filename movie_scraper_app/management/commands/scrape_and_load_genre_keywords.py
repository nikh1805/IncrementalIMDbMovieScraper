""" Django Management command for scraping and loading data into models. """

from django.core.management.base import BaseCommand

from movie_scraper_app.movie_scraper_adapter import scrape_genre_and_keywords


class Command(BaseCommand):
    """
    Django management command to scrape Genre and Keywords from IMDb
    and load them into the database.
    """
    help = 'Scrapes the Genre and Keywords from IMDb and loads them into the database.'

    def handle(self, *args, **kwargs):
        # ANSI Escape Codes for color codes.
        self.stdout.write("\033[1;34mRunning: Scraping Genre & Keywords...\033[0m")

        # Perform the scraping and updating
        scrape_genre_and_keywords()

        self.stdout.write("\033[1;32mSuccessfully scraped and loaded Genres & Keywords.\033[0m")
