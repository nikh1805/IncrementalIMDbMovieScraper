""" Base scraper module, single point of interaction with IMDB website through BS4 and selenium."""
import os

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service


class BaseScraper:
    """
    Base class for scraping IMDB website that extracts movie information from IMDb..
    Provides common functionality for fetching the HTML content.
    """

    def __init__(self, base_url: str):
        """
        Initialize the scraper with a base URL.
        Args:
            base_url (str): The base URL to be used for scraping.
        """
        self.base_url = base_url
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
            )
        }

    @classmethod
    def get_soup(cls, page_source):
        """ Gets Beautiful soup object for given page source"""
        return BeautifulSoup(page_source, "html.parser")

    def fetch_page(self, endpoint: str = "") -> BeautifulSoup:
        """
        Fetches the HTML content of a page and returns a BeautifulSoup object.
        Args:
            endpoint (str): The URL endpoint to fetch (optional).
        Returns:
            BeautifulSoup: Parsed HTML content.
        """
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()  # Raise an exception for HTTP errors
            return self.get_soup(response.content)
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Error fetching page: {url}. Details: {e}")
        except Exception as e:
            raise ValueError(f"Internal Server Error while fetching the page, {str(e)}")


class SeleniumBase:
    """
    Base class for handling Selenium WebDriver interactions.
    """

    def __init__(self, base_url: str, headless: bool = True):
        """
        Initialize the Selenium WebDriver.
        Args:
            base_url (str): The base URL to be used to load page.
            headless (bool): Run in headless mode (no GUI).
        """
        self.base_url = base_url
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--window-size=1920x1080")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")

        chrome_driver_path = os.environ.get("CHROME_DRIVER_PATH")
        if chrome_driver_path is None:
            # Try to identify the default driver path automatically
            self.driver = webdriver.Chrome(options=chrome_options)
        else:
            service = Service(chrome_driver_path)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)

        self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            'userAgent': (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
            )
        })
        # Maximize the Chrome window for better page visibility
        self.driver.maximize_window()

    def load_page(self, endpoint: str):
        """
        Load a webpage in the browser.
        Args:
            endpoint (str): endpoint of the page to load.
        """
        self.driver.get(f"{self.base_url}{endpoint}")

    def click_element(self, by: By, value: str):
        """
        Click an element on the webpage.
        Args:
            by (By): Locator strategy (e.g., By.ID, By.XPATH).
            value (str): Locator value.
        """
        try:
            # Wait until the element is visible and clickable
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((by, value))
            )
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((by, value))
            )
            # Find the element
            element = self.driver.find_element(by, value)
            # Scroll into element view
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center', inline: 'center'});",
                element
            )
            # Set border red style. Helps in debug visible in non headless mode
            self.driver.execute_script("arguments[0].style.border='3px solid red'", element)
            # Click See more element
            self.driver.execute_script("arguments[0].click();", element)
        except Exception as e:
            print(f"Error clicking element: {str(e)}")

    def get_page_source(self) -> str:
        """
        Get the page source after interactions.
        Returns:
            str: HTML content of the page.
        """
        return self.driver.page_source

    def scroll_down_once(self):
        """
        Scroll the page down by one viewport height.
        """
        self.driver.execute_script("window.scrollBy(0, window.innerHeight);")

    def close(self):
        """Close the Selenium WebDriver."""
        self.driver.quit()
