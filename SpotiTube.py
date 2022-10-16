import dearpygui.dearpygui as dpg
import requests
import os
import math
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import webbrowser
import time
import re
import csv

SPOTIFY_TEXT = "Enter the link to the Spotify playlist\n\
you wish to convert to a YouTube playlist.\
\n\nTo find this link:\n\
1) Go to your playlist on Spotify\n\
2) Click the 3 dots (...)\n\
3) Click 'Share'\n\
4) Click 'Copy link to playlist'"
                    
LYRICS_TEXT = "This setting specifies whether you want\n\
your Spotify playlist to be converted to\n\
lyrics videos or to music videos\n"

PRIVACY_TEXT = "This setting specifies the privacy status of your\n\
playlist:\n\n\
Public - Anyone on YouTube can search for and view your\n\
playlist\n\
Private - Only you can view your playlist\n\
Unlisted - Anyone with the link can view your playlist"

NAME_TEXT = "What name your YouTube playlist will have"

LINK_TEXT = "Clicking this button will take you to\n\
your generated YouTube playlist"

SPOTIFY_CSV_TEXT = 'Note: you can expand the window of\n\
the directory selector.\n\
A file name can only contain the\n\
following characters:\n\
- alphanumeric characters, underscores and hyphens'

scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

"""
SET SPOTIPY_CLIENT_ID="c2937fabb232491fb8b36feb8f232a37"  
SET SPOTIPY_CLIENT_SECRET="5680d832bd254fbabd9a797da8559198"
SET SPOTIPY_REDIRECT_URI="http://localhost/"
https://open.spotify.com/playlist/7JafI1GmeNMhJaeaH7ESP4 me(131)
https://open.spotify.com/playlist/3FuyHlu9qC9YxweeHsEsX0?si=e51eaf21e17740b5 me(2)
https://open.spotify.com/playlist/0fKSKzeJZOrxR49eIKbhMR?si=38549d3c9e314fa1 danvir
print(json.dumps(r.json(), indent=1))
"""

csv_files_location = ""
youtube_playlist_scraped = False
youtube_playlist = []

def main():
    def disabler(*args):
        for arg in args:
            dpg.disable_item(arg)

    def enabler(*args):
        for arg in args:
            dpg.enable_item(arg)
            
    # boilerplate code for DPG
    dpg.create_context()

    def create_double_csv(): # called by submit
        global csv_files_location
        global youtube_playlist_scraped
        global youtube_playlist
        fileName = dpg.get_value(div8_textbar)

        if youtube_playlist_scraped:
            if csv_files_location == "" or not re.search(r'^[a-zA-Z0-9_-]+$', fileName):
                dpg.configure_item(div8_success_text, color=[255, 0, 0])
                dpg.set_value(div8_success_text, "Make sure you have chosen a correct file name and a directory")
            else:
                dpg.configure_item(div8_success_text, color=[0, 255, 0])
                dpg.set_value(div8_success_text, f"SUCCESS: Files saved as {fileName}_spotify.csv and {fileName}_youtube.csv at {csv_files_location}")

                with open(csv_files_location + "\\" + fileName + "_spotify.csv", "w", newline="") as file:
                    spotify_playlist = spotify_scraper(dpg.get_value(div1_textbar))
                    writer = csv.DictWriter(file, fieldnames=["song", "album", "artists", "length"])
                    writer.writeheader()
                    for song in spotify_playlist:
                        writer.writerow({"song": song["song"], "album": song["album"], "artists": song["artists"], "length": song["length"]})

                with open(csv_files_location + "\\" + fileName + "_youtube.csv", "w", newline="") as file:
                    writer = csv.DictWriter(file, fieldnames=["id"])
                    writer.writeheader()
                    for song in youtube_playlist:
                        writer.writerow({"id": song})
                youtube_playlist_scraped = False
        else:
            dpg.set_value(div8_success_text, "You must submit a playlist before you can export it")
            dpg.configure_item(div8_success_text, color=[255, 0, 0])
        
    def callback(sender, app_data):
        global csv_files_location
        csv_files_location = app_data["file_path_name"]

    def check_spotify_link():
        global youtube_playlist_scraped
        youtube_playlist_scraped = False
        spotify_playlist = spotify_scraper(dpg.get_value(div1_textbar))

        if spotify_playlist == "Incorrect format for playlist URL" or spotify_playlist == "Playlist does not exist":
            dpg.set_value(div1_text, spotify_playlist + ". Make sure the URL\nis correct and the playlist is set to public.")
            dpg.configure_item(div1_text, color=[255, 0, 0])
        else:
            dpg.set_value(div1_text, "Playlist Found")
            dpg.configure_item(div1_text, color=[0, 255, 0])
            disabler(div1_textbar, div1_submit)
            enabler(div2_radio, div3_radio, div4_textbar, div4_submit)
            return spotify_playlist

    def youtube_generator():
        global youtube_playlist_scraped
        global youtube_playlist
        # boilerplate code for YouTube API
        api_service_name = "youtube"
        api_version = "v3"
        client_secrets_file = "client_secrets.json"

        # Get credentials and create an API client
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            client_secrets_file, scopes)
        credentials = flow.run_console()
        youtube = googleapiclient.discovery.build(
            api_service_name, api_version, credentials=credentials)

        spotify_playlist = spotify_scraper(dpg.get_value(div1_textbar))

        youtube_playlist = []
        errors_list = []
        # SONG, ALBUM, LENGTH, ARTISTS
        if dpg.get_value(div2_radio) == "Lyrics videos":
            for song in spotify_playlist:
                query = f'{song["song"]} {song["album"]} {song["artists"]} lyrics video'
                # sending actual request
                request = youtube.search().list(
                    part="snippet",
                    maxResults=1,
                    q = query
                )
                response = request.execute()

                try:
                    youtube_playlist.append(response["items"][0]["id"]["videoId"])
                except KeyError:
                    errors_list.append(song)
        else:
            for song in spotify_playlist:
                query = f'{song["song"]} {song["album"]} {song["artists"]} official music video'
                # sending actual request
                request = youtube.search().list(
                    part="snippet",
                    maxResults=1,
                    q = query
                )
                response = request.execute()

                try:
                    youtube_playlist.append(response["items"][0]["id"]["videoId"])
                except KeyError:
                    errors_list.append(song)
            

        # create a playlist
        request = youtube.playlists().insert(
            part="id,snippet,status",
            body={
                "snippet": {
                    "title": f"{dpg.get_value(div4_textbar)}"
                },
                "status": {
                    "privacyStatus": f"{dpg.get_value(div3_radio).lower()}"
                }
            }
        )
        response = request.execute()
        youtube_playlist_id = (response["id"])

        for song in youtube_playlist:
            # prevent YouTube API data rate from being exceeded if error is being received
            # time.sleep(3)
            request = youtube.playlistItems().insert(
            part="snippet",
            body={
                "snippet": {
                    "playlistId": f"{youtube_playlist_id}",
                    "resourceId": {"kind": "youtube#video", "videoId": f"{song}"},
                }
            }
        )
            response = request.execute()

        dpg.set_value(div5_text, "SUCCESS: Your playlist is available at the following link:")
        dpg.configure_item(div5_text, color=[0, 255, 0])
        dpg.set_value(div6_text, f"https://www.youtube.com/playlist?list={response['snippet']['playlistId']}")
        dpg.configure_item(div6_text, color=[0, 255, 0])
        enabler(div7_link, div1_textbar, div1_submit)
        dpg.set_item_callback(div7_link, callback=lambda:webbrowser.open(f"https://www.youtube.com/playlist?list={response['snippet']['playlistId']}"))
        youtube_playlist_scraped = True
        disabler(div2_radio, div3_radio, div4_textbar, div4_submit)


    with dpg.window(tag="Primary Window"):
        # Enter your Spotify playlist link:
        dpg.add_text("Enter your Spotify playlist link:", tag="info_text_spotify_playlist_link")
        with dpg.tooltip("info_text_spotify_playlist_link"):
            dpg.add_text(SPOTIFY_TEXT)
        with dpg.group(horizontal=True):
            div1_textbar = dpg.add_input_text()
            dpg.set_item_width(div1_textbar, 550)
            div1_submit = dpg.add_button(label="Submit", callback=check_spotify_link)
        div1_text = dpg.add_text("", color=[37, 37, 38])


        # Lyrics videos or music videos:
        dpg.add_text("Lyrics videos or music videos:", tag="info_text_lyrics_or_music")
        with dpg.tooltip("info_text_lyrics_or_music"):
            dpg.add_text(LYRICS_TEXT)
        div2_radio = dpg.add_radio_button(("Lyrics videos", "Music videos"), horizontal=True, default_value="Lyrics videos")
        dpg.add_text()

        # Privacy status of playlist:
        dpg.add_text("Privacy status of playlist:", tag="info_text_privacy_status")
        with dpg.tooltip("info_text_privacy_status"):
            dpg.add_text(PRIVACY_TEXT)
        div3_radio = dpg.add_radio_button(("Public", "Private", "Unlisted"), horizontal=True, default_value="Public")
        dpg.add_text()

        # Enter the playlist name:    
        dpg.add_text("Enter the playlist name:", tag="info_text_playlist_name")
        with dpg.tooltip("info_text_playlist_name"):
            dpg.add_text(NAME_TEXT)
        with dpg.group(horizontal=True):
            div4_textbar = dpg.add_input_text()
            dpg.set_item_width(div4_textbar, 550)
            div4_submit= dpg.add_button(label="Submit", callback=youtube_generator)
        div4_text = dpg.add_text("", color=[37, 37, 38])

        # text for success and playlist link
        div5_text = dpg.add_text("", color=[37, 37, 38])
        div6_text = dpg.add_text("", color=[37, 37, 38])
        div7_text = dpg.add_text("Generated Link:")
        div7_link = dpg.add_button(label="LINK", callback=lambda:webbrowser.open("https://google.com"))
        with dpg.tooltip(div7_text):
            dpg.add_text(LINK_TEXT)

        # searchbars for where to save each file
        dpg.add_text("")
        dpg.add_text("Download two CSV files containing information about your Spotify and YouTube playlists:", tag="div8_text")
        with dpg.tooltip("div8_text"):
            dpg.add_text(SPOTIFY_CSV_TEXT)
        dpg.add_file_dialog(
            directory_selector=True, show=False, callback=callback, tag="file_dialog_id")
        with dpg.group(horizontal=True):
            div8_textbar = dpg.add_input_text(default_value="File Name")
            div8_directory_selector = dpg.add_button(label="Directory Selector", callback=lambda: dpg.show_item("file_dialog_id"))
            div8_submit = dpg.add_button(label="SUBMIT", callback=create_double_csv)
        div8_success_text = dpg.add_text("", color=[37, 37, 38])
    
        # disable divs 2 to 7 intially
        disabler(div2_radio, div3_radio, div4_textbar, div4_submit, div7_link)

    # boilerplate code for DPG
    dpg.create_viewport(title='SpotiTube', width=700, height=550)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.set_viewport_resizable(False)
    dpg.set_primary_window("Primary Window", True)
    dpg.set_viewport_vsync(True)
    dpg.start_dearpygui()
    dpg.destroy_context()


def spotify_scraper(playlist_link):
    """ Creates a list of the songs in a Spotify playlist """

    # boilerplate code to use the Spotify API
    AUTH_URL = "https://accounts.spotify.com/api/token"
    CLIENT_ID=os.environ.get("SPOTIPY_CLIENT_ID")
    CLIENT_SECRET=os.environ.get("SPOTIPY_CLIENT_SECRET")

    auth_response = requests.post(AUTH_URL, {
        'grant_type': 'client_credentials',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
    })
    auth_response_data = auth_response.json()
    access_token = auth_response_data['access_token']

    headers = {
        'Authorization': 'Bearer {token}'.format(token=access_token)
    }

    # asks user for playlist link
    playlist_id = playlist_link

    # catch IndexError if URL is in the incorrect format
    try:
        if "?" in playlist_id:
            playlist_id = playlist_id.split("/")[4].split("?")[0]
        else:
            playlist_id = playlist_id.split("/")[4]
    except IndexError:
        return "Incorrect format for playlist URL"
    
    # catches KeyError if playlist does not exist
    try:
        playlist_url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
        raw_spotify_data = requests.get(playlist_url, headers=headers)
        raw_spotify_data = raw_spotify_data.json()
        playlist_length = raw_spotify_data["total"]
        items = raw_spotify_data["items"]
        songs_list = []
        counter = 0
    except KeyError:
        return "Playlist does not exist"

    # loops through the playlist 100 songs at a time, since Spotify's API
    # only returns 100 songs at a time
    for i in range(0, roundup(playlist_length), 100):
        # fetches playlist data
        playlist_url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks?offset={i}"
        raw_spotify_data = requests.get(playlist_url, headers=headers)
        raw_spotify_data = raw_spotify_data.json()
        playlist_length = raw_spotify_data["total"]
        items = raw_spotify_data["items"]

        # adds each song to the songs_list
        for row in items:
          # in format: song name, album name, song length, FOR LOOP for artists
            songs_list.append(dict())
            songs_list[counter]["song"] = row["track"]["name"]
            songs_list[counter]["album"] = row["track"]["album"]["name"]
            songs_list[counter]["length"] = row["track"]["duration_ms"]
            songs_list[counter]["artists"] = ""
            for artist in row["track"]["artists"]:
                songs_list[counter]["artists"] += f'{artist["name"]},' 

            counter += 1

    # removes last character from each song element in the list (",")
    for i in range(playlist_length):
        songs_list[i]["artists"] = songs_list[i]["artists"][:-1]

    return songs_list


def roundup(x):
    """ Returns inputted integer rounded up to the nearest hundred """
    return int(math.ceil(x / 100.0)) * 100


if __name__ == "__main__":
    main()
