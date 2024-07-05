import os
import requests
import time
import datetime

from linkedin_api import Linkedin

from src.utils.constants import SEARCH_URL
from urllib.request import urlopen
from bs4 import BeautifulSoup
from selenium import webdriver


def move_down(url:str, scroll_count: int) -> BeautifulSoup:

    """
    Scrolls down a webpage a specified number of times and returns the page source as a BeautifulSoup object.

    Args:
        url (str): The URL of the webpage to scroll.
        scroll_count (int): The number of times to scroll down the page.

    Returns:
        BeautifulSoup: A BeautifulSoup object containing the HTML of the scrolled page.
    """

    driver = webdriver.Remote(os.getenv("WEBDRIVER_URL"), webdriver.DesiredCapabilities.CHROME)

    driver.get(url)

    for _ in range(scroll_count):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(4)  

    
    html = driver.page_source

    driver.quit()

    return BeautifulSoup(html, "html.parser")


def internet_search(search: str) -> requests.Response:
    """
    Performs an internet search using the specified search query.

    Args:
        search: A string representing the search query to be used for the internet search.

    Returns:
        A requests.Response object containing the response from the internet search.
    """
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/98.0.4758.82'
    }
    return requests.get(SEARCH_URL, headers=headers, params={'q': search})


def get_html(url: str) -> BeautifulSoup:
    """
    Retrieves the HTML content of a webpage located at the specified URL and parses it using BeautifulSoup.

    Args:
        url: A string representing the URL of the webpage to retrieve.

    Returns:
        A BeautifulSoup object containing the parsed HTML content of the webpage.
    """
    html = urlopen(url).read().decode("utf-8")

    return BeautifulSoup(html, "html.parser")


def get_time_period(values: dict) -> tuple[None | datetime.datetime, None | datetime.datetime]:
    """
    Extracts start and end dates from a dictionary representing a time period.

    Args:
        values (dict): A dictionary containing information about the time period, including start date and end date.

    Returns: tuple[None | datetime.datetime, None | datetime.datetime]: A tuple containing the start date and end
    date of the time period. If the start date or end date is not provided in the input dictionary, it will be
    returned as None.
    """
    start_date: None | datetime.datetime = None
    end_date: None | datetime.datetime = None

    if values.get("timePeriod"):
        if values["timePeriod"].get("startDate"):
            start_year = values["timePeriod"]["startDate"].get("year", 0)
            start_month = values["timePeriod"]["startDate"].get("month", 0)

            start_date = datetime.datetime(start_year, start_month, 1)

        if values["timePeriod"].get("endDate"):
            end_year = values["timePeriod"]["endDate"].get("year", 0)
            end_month = values["timePeriod"]["endDate"].get("month", 0)

            end_date = datetime.datetime(end_year, end_month, 1)

    return start_date, end_date


def authenticate_linkedin() -> Linkedin | None:
    """
    Authenticates the user with LinkedIn using environment variables for username and password.

    Returns:
        LinkedIn: An authenticated instance of the LinkedIn class.
    """
    linkedin_connect = None

    amount_attempts = 0
    while not linkedin_connect:
        
        if amount_attempts >= 10:
            return None
        
        try:
            linkedin_connect = Linkedin(os.getenv("LINKEDIN_USER"), os.getenv("LINKEDIN_PASSWORD"))
        except Exception as e:
            print(f"[WARNING] Error while authenticating LinkedIn: {e}")

            amount_attempts += 1
            time.sleep(5.0)

    return linkedin_connect
