from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
import concurrent.futures
import time
from selenium.common.exceptions import NoSuchElementException


##FALTAN LINKS

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
driver.maximize_window()

movies_url = 'https://www.starz.com/us/en/movies'
driver.get(movies_url)
html_content = driver.page_source
soup = BeautifulSoup(html_content, 'html.parser')


movies_links = driver.find_elements(By.CLASS_NAME, "StandardSlide_img-container__XvbLR")

movies = []


for movie in movies_links:
    href = movie.get_attribute("href")
    if href not in movies:
        movies.append(href)

movies_dataset = []

for link in movies[:2]:
    driver.get(link)
    time.sleep(5)

    try:

        movie_name = driver.find_element(By.XPATH, "//div/h1").text
        movie_rating = driver.find_element(By.XPATH, "//div/span[1]").text
        movie_duration = driver.find_element(By.XPATH, "//div/span[2]").text
        movie_category = driver.find_element(By.XPATH, "//div/span[3]").text
        movie_year = driver.find_element(By.XPATH, "//div/span[4]").text
        movie_cast = driver.find_element(By.XPATH, "//p[@class='important-cast text-center text-xl-left pb-0 m-0 on-surface-1-variant-1']").text[9:]

        try:
            synopsis_button = driver.find_element(By.XPATH, "//p/button")
            synopsis_button.click()
            movie_synopsis = driver.find_element(By.XPATH, "//div/p[@class='on-surface-1 text-center mt-2 mb-1 mx-2']").text
        except:
            pass

        movies_dataset.append(
            {"Name":movie_name,
             "Rating":movie_rating,
             "Duration":movie_duration,
             "Category":movie_category,
             "Year":movie_year,
             "Cast":movie_cast,
             "Synopsis":movie_synopsis
            }
        )

    except NoSuchElementException:

        print("Element not found in:", link)


series_url = 'https://www.starz.com/us/en/series'
driver.get(series_url)
html_content = driver.page_source
soup = BeautifulSoup(html_content, 'html.parser')

series_links = driver.find_elements(By.CLASS_NAME, "StandardSlide_img-container__XvbLR")

series_list = []


for series in series_links:
    href = series.get_attribute("href")
    if href not in series_list:
        series_list.append(href)

series_dataset = []

for series_link in series_list[:4]:
    driver.get(series_link)
    time.sleep(5)

    try:

        series_name = driver.find_element(By.XPATH, "//div/h1").text
        series_rating = driver.find_element(By.XPATH, "//div/span[1]").text
        series_episodes = driver.find_element(By.XPATH, "//div/h2").text
        series_category = driver.find_element(By.XPATH, "//div/span[2]").text
        series_duration = driver.find_element(By.XPATH, "//div/span[3]").text
        series_cast = driver.find_element(By.XPATH, "//p[@class='important-cast text-center text-xl-left pb-0 m-0 on-surface-1-variant-1']").text[9:]

        try:
            synopsis_button = driver.find_element(By.XPATH, "//p/button")
            synopsis_button.click()
            series_synopsis = driver.find_element(By.XPATH, "//div/p[@class='on-surface-1 text-center mt-2 mb-1 mx-2']").text
        except:
            pass

        series_dataset.append(
            {"Name":series_name,
             "Rating":series_rating,
             "Episodes":series_episodes,
             "Category":series_category,
             "Duration":series_duration,
             "Cast":series_cast,
             "Synopsis":series_synopsis
            }
        )

    except NoSuchElementException:

        print("Element not found in:", link)


driver.quit()

