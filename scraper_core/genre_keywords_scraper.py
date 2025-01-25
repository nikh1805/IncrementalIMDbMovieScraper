""" Scraps Genres, Keywords and total movie counts """

from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from .base import BaseScraper, SeleniumBase
from .constants import BASE_URL, MOVIE_URL, HEADLESS_MODE
from .utils import convert_to_integer


class GenreKeywordScraper(BaseScraper):
    """
    Scraper for extracting genres and keywords from IMDb.
    """

    def __init__(self, movie_page_size: int = 250):
        """
        Initialize the scraper to get the genres, keywords and total movie counts.
        Args:
            movie_page_size(int): maximum movies per page
        """
        super().__init__(BASE_URL)

        self.movie_page_size = movie_page_size
        self.endpoint = f"{MOVIE_URL}&count={self.movie_page_size}"
        self.selenium = SeleniumBase(BASE_URL, HEADLESS_MODE)

    def scrape(self) -> dict:
        """
        Scrapes genres and keywords from the IMDb page.
        Returns:
            dict: A dictionary containing genres and keywords
        """
        soup = self.fetch_page(self.endpoint)
        genres = self._extract_genres(soup)
        keywords = self._extract_keywords()
        return {"genres": genres, "keywords": keywords}

    def _extract_genres(self, soup) -> list:
        """
        Extracts genres from the IMDb page.
        Args:
            soup (BeautifulSoup): Parsed HTML content.
        Returns:
            list: A list of dictionaries with genre names and movie counts.
        """
        genres = []
        try:
            genre_section = soup.find("div", id="accordion-item-genreAccordion")
            if genre_section:
                buttons = genre_section.find_all("button")
                for button in buttons:
                    # Extract genre name
                    name_span = button.find("span", class_="ipc-chip__text")
                    genre_name = name_span.contents[0].strip() if name_span else None
                    # Extract and convert movie count
                    count_span = button.find("span", class_="ipc-chip__count")
                    m_count = convert_to_integer(count_span.text) if count_span else 0
                    # Add to genres if the count is greater than zero
                    if genre_name and m_count > 0:
                        genres.append({"name": genre_name, "count": m_count})
        except Exception as e:
            raise ValueError(f"Error extracting genres from scraped gener data: {e}")
        return genres

    def _extract_keywords(self) -> list:
        """
        Extracts keywords from the IMDb page.
        Returns:
            list: A list of dictionaries with keyword names and movies count.
        """
        keywords = []
        try:
            page_source = self._get_keywords_extended_page()
            soup = self.get_soup(page_source)
            keyword_section = soup.find("div", id="accordion-item-keywordsAccordion")
            if keyword_section:
                buttons = keyword_section.find_all("button")
                for button in buttons:
                    name_span = button.find("span", class_="ipc-chip__text")
                    keyword_name = name_span.contents[0].strip() if name_span else None
                    count_span = button.find("span", class_="ipc-chip__count")
                    k_count = convert_to_integer(count_span.text) if count_span else 0
                    if keyword_name and k_count > 0:
                        keywords.append({"name": keyword_name, "count": k_count})
        except NoSuchElementException as e:
            raise ValueError(f"Element not found in extract_keywords. {e}")
        except TimeoutException as e:
            raise ValueError(f"Command Timeout in extract_keywords. {e}")
        except Exception as e:
            raise ValueError(f"Error extracting keywords from scraped gener data: {e}")
        finally:
            self.selenium.close()  # Close the driver
        return keywords

    def _get_keywords_extended_page(self):
        """ Loads all keywords """
        self.selenium.load_page(self.endpoint)
        # Click expand all button to expand the filters accordian
        self.selenium.click_element(By.XPATH, '//*[@id="keywordsAccordion"]/div[1]/label/span[2]')
        # Click "See more keywords" button to load all possible keywords present
        self.selenium.click_element(By.XPATH, '/html/body/div[2]/main/div[2]/div[3]/section/section/div/section/'
                                              'section/div[2]/div/section/div[2]/div[1]/section/div/div[14]/div[2]/'
                                              'div/div/button')
        self.selenium.scroll_down_once()
        return self.selenium.get_page_source()
