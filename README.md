# Incremental Movie Scraper

## Overview

#### This project is an **incremental movie scraping** tool, designed to scrape movie details from https://www.imdb.com/ website based on genre or keyword. The scraper works asynchronously using Django Q to handle tasks parallely. The scraper is designed to be scalable, supporting different scraping strategies based on movie count, multiple page clicks, and request batches.

## Features

- **Flexible Search**: Allows users to specify the genre or keyword for the movie search.
- **Incremental Scraping:** The scraper fetches movie data in incremental batches to handle IMDB movies pagination and extract specific details about movies from multiple pages.
- **Immediate Response**: For an immediate response of search API, the scraper fetches and returns the data either from database if exists or scrape the first 10 movies (configurable) synchronously. The rest of the movies are scraped asynchronously.
- **Django Q Integration:** Asynchronous task handling for long-running scraping jobs and admin control to monitor the Tasks (Queued, Failed, Successful etc.).
- **Parallel Processing**: Scraping is done in parallel by submitting incremental batches using **Django Q**, improving overall scraping performance.
- **Exception Handling**: The scraper handles unexpected issues gracefully, including API exceptions and errors from movie Scraper. Detailed error messages can be tracked through django admin Failed task model.
- **Pagination**: Supports pagination (limit and offset) for efficient handling of large datasets.
- **Customizable Settings:** Configurable scraping settings such as the number of movies to scrape, the maximum clicks per request, and more.
- **Custom Management Command:** Customized django management command to scrape all the available Genres and Keywords from IMDB.

## Scraping Logic

The scraper works in batches and makes requests to fetch movie data in chunks. The scraper calculates the number of clicks required based on the number of remaining movies and fetches movie data incrementally. The scraper ensures that only the necessary number of requests are made.

1. First Batch Scraping
   The first batch of movie data is fetched synchronously without requiring additional clicks. This includes the first batch of movies based on the defined first_load_movies(10).

2. Incremental Scraping
   After the first batch, the scraper continues fetching data in subsequent batches by calculating the number of clicks required to fetch the remaining movies. This is handled asynchronously using Django Q tasks.

## Tech Stack

- **Python**: Programming Language used. 
- **Django**: Web framework used to build the application.
- **Django REST Framework (DRF)**: To build REST APIs.
- **Django Q**: For handling asynchronous background tasks.
- **BeautifulSoup**: For web scraping.
- **Selenium (with ChromeDriver)**: To interact with dynamic content on websites such as load more movies.

## Setup and Installation

### Prerequisites

- Python 3.x
- Django 3.x or higher

### Clone the repository

```bash
git clone https://github.com/nikh1805/IncrementalIMDbMovieScraper
cd IncrementalIMDbMovieScraper
```

### Create Environment and Install Dependencies

**Windows**

```shell
python -m venv env
env\Scripts\activate
pip install -r requirements.txt
```

**Linux/Mac**

```shell
python3 -m venv env
source env/bin/activate
pip3 install -r requirements.txt
```

### Environment Variables

Create environment file as .env inside root folder (where manage.py file resides) and keep the below environment
variables.

```shell
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=your-database-url # defaults to SQLITE3
CHROME_DRIVER_PATH=chrome-driver-path # Defaults: Linux: /usr/bin/chromedriver MAC: /Applications/ChromeDriver/chromedriver. If not provided system tries to find automatically. 
```

## Database Setup

```shell
python manage.py migrate
python manage.py createsuperuser
python manage.py scrape_and_load_genre_keywords # Fetches the Genres and Keywords from IMDB and loads into database
python manage.py runserver
```

## Django Q Setup and Task Monitoring

```shell
python manage.py qcluster # (Required. Run in Separate Terminal) Starts the Django Q cluster, which is responsible for processing queued tasks.
python manage.py qmonitor # (optional) Starts a command-line monitor for your queues, displaying real-time information about the task status, including pending, running, and completed tasks.
```

#### Admin Interface: Visit http://localhost:8000/admin

## API Endpoints

1. Search Movies API (Lists movies and triggers the Scraping)
    - Endpoints:
        - All Movie List: GET http://localhost:8000/api/movies
        - Movies List with Pagination: GET http://localhost:8000/api/movies?limit=10&offset=0
        - Movies filtered by Genre/Keyword: GET http://localhost:8000/api/movies?limit=10&offset=0&tag=Game-Show
2. Movie Detail API (Gets movie detail information for given movie id)
    - Endpoint: GET http://localhost:8000/api/movie/<movie_id>


