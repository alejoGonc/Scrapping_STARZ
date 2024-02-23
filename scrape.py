from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
import pandas as pd
import time
from selenium.common.exceptions import NoSuchElementException 
from pymongo import MongoClient


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

for link in movies:
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
            time.sleep(2)
        except:
            pass

        try:
            movie_synopsis = driver.find_element(By.XPATH, "//div/p[@class='on-surface-1 text-center mt-2 mb-1 mx-2']").text   
        except NoSuchElementException:
            movie_synopsis = driver.find_element(By.XPATH, "//div/p/span[@class='p on-surface-1-variant-1']").text
             

        movies_dataset.append(
            {"Name":movie_name,
             "Rating":movie_rating,
             "Duration":movie_duration,
             "Category":movie_category,
             "Year":movie_year,
             "Cast":movie_cast,
             "Synopsis":movie_synopsis,
             "Link":link
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
season_dataset = []
episodes_dataset = []

for series_link in series_list:
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
            time.sleep(2)
            series_synopsis = driver.find_element(By.XPATH, "//div/p[@class='on-surface-1 text-center mt-2 mb-1 mx-2']").text
        except:
            series_synopsis = None

        series_dataset.append(
            {"Name":series_name,
             "Rating":series_rating,
             "Episodes":series_episodes,
             "Category":series_category,
             "Duration":series_duration,
             "Cast":series_cast,
             "Synopsis":series_synopsis,
             "Link":series_link
            }
        )

        series_url = driver.current_url

        season_links = driver.find_elements(By.XPATH, "//div[@class='SeasonCard_slide__hTAA_ col-xs-12 col-sm-6 col-md-4 col-xl-4']/div[@class='SeasonCard_image-container__9YQZy']/a[@class='SeasonCard_hover-content__Qvwds']")
        season_number = [season.get_attribute("href") for season in season_links]
        print(season_number)

        for season in season_number:
            driver.get(season)
            time.sleep(3)

            season_name = driver.find_element(By.XPATH, "//button/span").text
            season_episodes = driver.find_element(By.XPATH, "//div/h2").text
            season_synopsis = driver.find_element(By.XPATH, "//p/span").text

            season_dataset.append({
                "Series": series_name,
                "Season": season_name,
                "Episodes": season_episodes,
                "Synopsis": season_synopsis,
                "Link": season
            })

            episode_containers = driver.find_elements(By.XPATH,"//div[@class='EpisodeCard_slide__WdptO col-xs-12 col-sm-6 col-md-4 col-xl-4']")

            for episode in episode_containers:
                try:
                    episode_name = episode.find_element(By.XPATH, ".//div[@class='EpisodeCard_detail-container__vXjLd']/button").text
                    episode_description = episode.find_element(By.XPATH, ".//span[@class='slide-description p on-surface-1']").text
                    episode_metadata = episode.find_element(By.XPATH,".//div[@class='EpisodeCard_slide-details__esa7g on-surface-1-variant-1 metadata-copy small']").text.split(' | ')

                    episodes_dataset.append({
                        "Episode": episode_name,
                        "Description": episode_description,
                        "Duration":episode_metadata[1],
                        "Year":episode_metadata[2],
                        "Series":series_name
                    })
                except:
                    pass

                

    except NoSuchElementException:
         print("Element not found in:", series_link)

episodes_df = pd.DataFrame(episodes_dataset)
seasons_df = pd.DataFrame(season_dataset)
movies_df = pd.DataFrame(movies_dataset)

episodes_df.to_csv('episodes.csv')
movies_df.to_csv('movies.csv')
seasons_df.to_csv('seasons.csv')


records_episodes = episodes_df.to_dict(orient='records')
records_seasons = seasons_df.to_dict(orient='records')
records_movies = movies_df.to_dict(orient='records')

client = MongoClient('mongodb://localhost:27017/')

db = client['admin'] 
collection_movies = db['Movies']
collection_seasons = db['Seasons']
collection_episodes = db['Episodes']

collection_episodes.insert_many(records_episodes)
collection_seasons.insert_many(records_seasons)
collection_movies.insert_many(records_movies)

driver.quit()

