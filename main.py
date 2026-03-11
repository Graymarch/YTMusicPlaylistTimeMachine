import re
import requests
import spotipy
from bs4 import BeautifulSoup
from spotipy import SpotifyOAuth

header = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36"}
client_id = "7720e2e715024c5db28435cd730bbb09"
client_secret = "17ed407ae6f44ace9e765b492fb7f3ca"
redirect_uri = "https://example.com"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope = "playlist_modify-private"
))

target_pattern = r"[0-9]{4}-[0-9]{2}-[0-9]{2}"
cleaning_pattern = r"\n|\t"
target_date = input("Choose a date and I will find the top 100 songs from that date (YYYY-MM-DD): ")
while re.search(target_pattern, target_date) is None:
    target_date = input("Malformed date. Try again (YYYY-MM-DD): ")
target_url = f"https://www.billboard.com/charts/hot-100/{target_date}/"

response = requests.get(url=target_url, headers=header).text
bs = BeautifulSoup(response, "html.parser")
song_titles = [re.sub(
    cleaning_pattern,
    "",
    item.text
) for item in bs.select(".o-chart-results-list__item #title-of-a-story")]

song_artists = [re.sub(
    cleaning_pattern,
    "",
    (item.select_one(".o-chart-results-list__item .c-label")).text
) for item in bs.select(".a-chart-result-item-container")]

