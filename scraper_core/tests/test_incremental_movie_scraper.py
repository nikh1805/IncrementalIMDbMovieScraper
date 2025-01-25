from unittest import TestCase

from scraper_core.incremental_movie_scraper import IncrementalMovieScraper


class TestIncrementalMovieScraper(TestCase):

    def test_compute_clicks_and_parse_count_required_400_movies(self):
        # Test for 400 movies
        inc_movie_scraper = IncrementalMovieScraper(genre="action", movies_count=400)
        expected = [(1, 150)]  # 400 - 250 = 150; 1 click required
        res = inc_movie_scraper.compute_clicks_and_parse_count_required(0, 4)
        self.assertEqual(res, expected)

    def test_compute_clicks_and_parse_count_required_400_movies_50left_from_initial(self):
        # Test for 400 movies
        inc_movie_scraper = IncrementalMovieScraper(genre="action", movies_count=400)
        expected = [(1, 200)]  # 400 - 250 = 150+50; 1 click required
        res = inc_movie_scraper.compute_clicks_and_parse_count_required(50, 4)
        self.assertEqual(res, expected)

    def test_compute_clicks_and_parse_count_required_2000_movies(self):
        # Test for 2000 movies
        inc_movie_scraper = IncrementalMovieScraper(genre="action", movies_count=2000)
        expected = [(4, 1000), (7, 750)]  # Two sets of requests to cover 2000 movies
        res = inc_movie_scraper.compute_clicks_and_parse_count_required(0, 4)
        self.assertEqual(res, expected)

    def test_compute_clicks_and_parse_count_required_1252_movies(self):
        # Test for 1252 movies
        inc_movie_scraper = IncrementalMovieScraper(genre="action", movies_count=1252)
        expected = [(4, 1000), (5, 2)]  # Two sets: 1000 movies + 2 remaining
        res = inc_movie_scraper.compute_clicks_and_parse_count_required(0, 4)
        self.assertEqual(res, expected)

    def test_compute_clicks_and_parse_count_required_2611_movies(self):
        # Test for 2611 movies
        inc_movie_scraper = IncrementalMovieScraper(genre="action", movies_count=2611)
        expected = [(4, 1000), (8, 1000), (10, 361)]  # Three sets of requests
        res = inc_movie_scraper.compute_clicks_and_parse_count_required(0, 4)
        self.assertEqual(res, expected)

    def test_compute_clicks_and_parse_count_required_zero_movies(self):
        # Edge case: 0 movies
        inc_movie_scraper = IncrementalMovieScraper(genre="action", movies_count=0)
        expected = []  # No requests needed
        res = inc_movie_scraper.compute_clicks_and_parse_count_required(0, 4)
        self.assertEqual(res, expected)

    def test_compute_clicks_and_parse_count_required_movies_less_than_page_size(self):
        # Edge case: movies < movies_per_click (250)
        inc_movie_scraper = IncrementalMovieScraper(genre="action", movies_count=200)
        expected = []  # Already fetched on the first page
        res = inc_movie_scraper.compute_clicks_and_parse_count_required(0, 4)
        self.assertEqual(res, expected)

    def test_compute_clicks_and_parse_count_required_movies_equal_to_page_size(self):
        # Edge case: movies == movies_per_click (250)
        inc_movie_scraper = IncrementalMovieScraper(genre="action", movies_count=250)
        expected = []  # No additional requests required
        res = inc_movie_scraper.compute_clicks_and_parse_count_required(0, 4)
        self.assertEqual(res, expected)

    def test_compute_clicks_and_parse_count_required_movies_just_above_page_size(self):
        # Edge case: movies just above the page size (250)
        inc_movie_scraper = IncrementalMovieScraper(genre="action", movies_count=251)
        expected = [(1, 1)]  # One extra click required for 1 movie
        res = inc_movie_scraper.compute_clicks_and_parse_count_required(0, 4)
        self.assertEqual(res, expected)

    def test_compute_clicks_and_parse_count_required_large_movies_count(self):
        # Large number of movies
        inc_movie_scraper = IncrementalMovieScraper(genre="action", movies_count=5000)
        expected = [(4, 1000), (8, 1000), (12, 1000), (16, 1000), (19, 750)]  # 5 sets
        res = inc_movie_scraper.compute_clicks_and_parse_count_required(0, 4)
        self.assertEqual(res, expected)

    def test_compute_clicks_and_parse_count_required_custom_max_clicks(self):
        # Custom max_clicks_per_request smaller than default
        inc_movie_scraper = IncrementalMovieScraper(genre="action", movies_count=1252)
        expected = [(2, 500), (4, 500), (5, 2)]  # smaller click limit
        res = inc_movie_scraper.compute_clicks_and_parse_count_required(0, 2)
        self.assertEqual(res, expected)

    def test_compute_clicks_and_parse_count_required_custom_movies_per_click(self):
        # Custom movies_per_click larger than default
        inc_movie_scraper = IncrementalMovieScraper(genre="action", movies_count=50000)
        expected = [(50, 12500), (100, 12500), (150, 12500), (199, 12250)]  # larger movies_per_click
        res = inc_movie_scraper.compute_clicks_and_parse_count_required(0, 50)
        self.assertEqual(res, expected)
