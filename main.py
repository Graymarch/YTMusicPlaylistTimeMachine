import json
import re
import requests
from bs4 import BeautifulSoup
import google_auth_oauthlib
import googleapiclient.discovery
import googleapiclient.errors

#Data for web requests
with open("conf.json") as file:
    conf = json.load(file)
header = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36"}
scopes = ["https://www.googleapis.com/auth/youtube"]

#OAuth Section - Creates a YouTube object authorized to manage the user's YouTube acct.
api_service_name = "youtube"
api_version = "v3"
auth = google_auth_oauthlib.get_user_credentials(scopes, conf["id"], conf["secret"])
yt = googleapiclient.discovery.build(api_service_name, api_version, credentials=auth)

#Billboard Section
#Regex patterns
target_pattern = r"[0-9]{4}-[0-9]{2}-[0-9]{2}" #Ensures the input is in the YYYY-MM-DD format
cleaning_pattern = r"\n|\t" #Removes newline characters from the collected text.

#Prompts for the target date and loops until a valid input is given.
target_date = input("Choose a date and I will find the top 100 songs from that date (YYYY-MM-DD): ")
while re.search(target_pattern, target_date) is None:
    target_date = input("Malformed date. Try again (YYYY-MM-DD): ")
target_url = f"https://www.billboard.com/charts/hot-100/{target_date}/"

#Collects the HTML based on the date given and creates a BS object.
billboard_response = requests.get(url=target_url, headers=header).text
bs = BeautifulSoup(billboard_response, "html.parser")

#Selects all the song titles from the playlist and uses the regex pattern to clean the text.
song_titles = [re.sub(
    cleaning_pattern,
    "",
    item.text
) for item in bs.select(".o-chart-results-list__item #title-of-a-story")]

#Due to the site's formatting, it selects all '.a-chart-result-item-container'
# elements and selects the first '.o-chart-results-list__item .c-label' to get the artist.
song_artists = [re.sub(
    cleaning_pattern,
    "",
    (item.select_one(".o-chart-results-list__item .c-label")).text
) for item in bs.select(".a-chart-result-item-container")]

#YT Video Collection Section - not implemented yet.
video_ids = []
for idx, song in enumerate(song_titles):
    request = yt.search().list(
        part="snippet",
        maxResults=1,
        q=f"{song} {song_artists[idx]}",
        type="video",
    )
    yt_search_response = request.execute()
    video_ids.append(yt_search_response["items"][0]["id"]["videoId"])
    if idx == 4: break

#Playlist Creation/Filling Section
#Builds an API request to create a playlist for the authenticated account.
request = yt.playlists().insert(
    part="snippet,status",
    body={
        "snippet":{
            "title":"Udemy Test Playlist",
            "description":"Test project playlist 3/12/26"
        },
        "status": {
            "privacyStatus":"private",
        }
    }
)
yt_playlist_response = request.execute() #Executes the playlist creation request and stores the response.
list_id = yt_playlist_response["id"] #Collects the new playlist's ID for the next step.

#For each video ID, it inserts the associated video into the new playlist.
for item in video_ids:
    request = yt.playlistItems().insert(
        part="snippet",
        body={
            "snippet":{
                "playlistId":list_id,
                "resourceId":{
                    "kind":"youtube#video",
                    "videoId":item
                }
            }
        }
    )
    request.execute()