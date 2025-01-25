""" Scraps movies with handling multiple pagination. """
import math

from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from .base import BaseScraper, SeleniumBase
from .constants import BASE_URL, MOVIE_URL, HEADLESS_MODE


class MovieScraper(BaseScraper):
    """ Scraper for extracting movies from IMDb for given Genre or keyword. """

    def __init__(self, genre: str = None, keyword: str = None):
        """
        Initialize the scraper to get the genres, keywords and total movie counts.
        Args:
            genre (str) (Optional): Movies to be scraped for Genre
            keyword (str) (Optional): Movies to be scraped for keyword
        """
        super().__init__(BASE_URL)

        self.genre = genre
        self.keyword = keyword

        self._selenium = SeleniumBase(BASE_URL, HEADLESS_MODE)

    def _prepare_endpoint(self, movie_page_size: int):
        """
        Prepares scrape URL for fetching the movies for given genre or keyword
        """
        if self.genre:
            return f"{MOVIE_URL}&count={movie_page_size}&genres={self.genre}"
        elif self.keyword:
            return f"{MOVIE_URL}&count={movie_page_size}&keywords={self.keyword}"
        else:
            raise ValueError("Either Genre or Keyword is required to fetch the movies")

    def _click_see_more(self, num_of_clicks: int):
        """
        Click the "See more" button num_of_pages times to load additional movies.
        Args:
            num_of_clicks (int): Number of times to click the "See more" button.
        """
        for i in range(num_of_clicks):
            try:
                self._selenium.click_element(By.XPATH, "//span[contains(@class, 'single-page-see-more-button')]/button")
            except NoSuchElementException:
                raise ValueError(f"Incremental movie scraper, 'See more' button not found after {i} clicks.")
            except TimeoutException:
                raise ValueError(f"Incremental movie scraper, Timeout occurred while clicking the 'See more' button.")

    def batch_scrape(self, num_of_clicks: int, parse_movies_data_count: int, movie_page_size: int):
        """
        Scrape movies for the given batch size.
        Args:
            num_of_clicks (int): Number of batches to fetch. Each batch corresponds to clicking the "See more" button.
            parse_movies_data_count(int): Number of movies to be parsed for this request
            movie_page_size(int): Number of movies per page
        """
        try:
            endpoint = self._prepare_endpoint(movie_page_size)
            self._selenium.load_page(endpoint)
            # Click the "See more" button num_of_pages times
            self._click_see_more(num_of_clicks)
            page_source = self._selenium.get_page_source()
        except Exception as e:
            raise ValueError(f"Batch Scrape issue. {e}")
        finally:
            self._selenium.close()  # Close the Selenium driver
        # Parse the movies
        return self._parse_movies(page_source, parse_movies_data_count)

    def _parse_movies(self, page_source: str, parse_movies_data_count: int):
        """
        Parse movies with the BeautifulSoup.
        Args:
            page_source (HTML): HTML content of the page.
            parse_movies_data_count(int): number of movies to be parsed from end
        Returns:
            list: List of parsed movie data.
        """
        try:
            soup = self.get_soup(page_source)
            movies = []
            movie_items = soup.find_all("li", class_="ipc-metadata-list-summary-item")[-parse_movies_data_count:]
            print(f"Scraped movies list successfully. Total: {len(movie_items)}")
            print("Scraping movie details ...")
            for movie_item in movie_items:
                title_tag = movie_item.find("h3", class_="ipc-title__text")
                year_tag = movie_item.find("span", class_="sc-300a8231-7")
                rating_tag = movie_item.find("span", class_="ipc-rating-star--rating")
                summary_tag = movie_item.find("div", class_="ipc-html-content-inner-div")
                movie_info_tag = movie_item.find("a", class_="ipc-lockup-overlay ipc-focusable")
                title = title_tag.text.split('.')[1] if title_tag else "N/A"
                year = year_tag.text if year_tag and year_tag.text.isdigit() else 0
                rating = rating_tag.text.strip() if rating_tag else 0
                plot_summary = summary_tag.text if summary_tag else "N/A"
                movie_info_data = self._parse_movie_detail_info(
                    movie_info_tag.attrs.get("href")) if movie_info_tag else {}
                movies.append({
                    **{"title": title, "year": year, "rating": rating, "plot_summary": plot_summary},
                    **movie_info_data
                })
        except Exception as e:
            raise ValueError(f"Movie data parsing Issue. {e}")
        print(f"Scraped movie details successfully")
        return movies

    def _parse_movie_detail_info(self, movie_info_url: str):
        """
        Parses movie details including directors, casts, genres, and keywords from the given movie page URL.
        Args:
            movie_info_url (str): The URL of the movie details page.
        Returns:
            dict: A dictionary containing directors, casts, genres, and keywords.
        """
        soup = self.fetch_page(movie_info_url)
        # Extract directors
        director_span = soup.find("span", text="Director")
        directors = [
            director.get_text(strip=True)
            for director in director_span.find_parent("li").find_all("a")
        ] if director_span and director_span.find_parent("li") else []

        # Extract casts
        cast_a = soup.find("a", text="Stars")
        casts = [
            cast.get_text(strip=True)
            for cast in cast_a.find_parent("li").find("div").find_all("a")
        ] if cast_a and cast_a.find_parent("li") and cast_a.find_parent("li").find("div") else []

        # Extract genre
        genre_section = soup.find("div", {"data-testid": "interests"})
        genres = [genre.get_text(strip=True) for genre in genre_section.find_all("a")] if genre_section else []

        # Extract Keywords
        soup = self.fetch_page(f"{movie_info_url.split('?')[0]}keywords/")
        keys = soup.find_all("li", {"data-testid": "list-summary-item"})
        keywords = [key.get_text(strip=True) for k in keys for key in k.find_all("a")]
        return {"directors": directors, "casts": casts, "genres": genres, "keywords": keywords}


class IncrementalMovieScraper(MovieScraper):
    """ Incremental Movie scraper extending movie scraper. """

    def __init__(self, movies_count: int, genre: str = None, keyword: str = None, movie_page_size: int = 250):
        super().__init__(genre, keyword)

        self.movies_count = movies_count
        self.movie_page_size = movie_page_size

    def compute_clicks_and_parse_count_required(self, first_load_left_movies: int, max_clicks_per_request: int):
        """
        Computes the number of clicks required to fetch all the remaining movies based on the maximum number of clicks
        allowed per request and the number of movies already fetched during the first load.

        This function calculates the number of click requests necessary to fetch the remaining movies in chunks,
        ensuring that no more than `max_clicks_per_request` are made at once. It returns a list of tuples where each
        tuple contains the total number of clicks and the number of movies fetched in each request.

        Args:
            first_load_left_movies (int): The number of movies left to fetch from the initial load.
            max_clicks_per_request (int): The maximum number of clicks allowed per request.

        Returns:
            list: A list of tuples where each tuple contains:
                  - The total number of clicks made (int).
                  - The number of movies fetched in the current request (int).
        """
        requests = []
        last_clicks = 0
        remaining_movies = max(0, self.movies_count - self.movie_page_size)
        while remaining_movies > 0:
            clicks = min(math.ceil(remaining_movies / self.movie_page_size), max_clicks_per_request)
            total_clicks = clicks + last_clicks
            movies_fetched = min(clicks * self.movie_page_size, remaining_movies + first_load_left_movies)
            requests.append((total_clicks, movies_fetched))
            remaining_movies -= movies_fetched
            first_load_left_movies = 0
            last_clicks = total_clicks
        else:
            if first_load_left_movies > 0:
                requests.append((0, first_load_left_movies))
        return requests

    def scrape_first_batch_data(self, first_load_movies: int):
        """
        Scrapes the first batch of movie data without performing any clicks. This batch fetches either
        the first `first_load_movies` movies or the total available movies, whichever is smaller.
        Args:
            first_load_movies (int): The number of movies to be fetched in the first batch scrape.
        Returns:
            list: A list containing the movie data for the first batch, fetched without any clicks.
        """
        parse_movies_data_count = min(self.movies_count, first_load_movies)
        movie_data = self.batch_scrape(0, parse_movies_data_count, parse_movies_data_count)
        return movie_data
