# SpotiTube
A basic Python program that converts a Spotify playlist into a new YouTube playlist using the Spotify and YouTube APIs. <br>
Users are able to input the link to their Spotify playlist, and once this has been validated, they are able to generate a new YouTube playlist and choose the following parameters for it: the name of the playlist, the privacy status of the playlist (public, private or unlisted) and whether they want the songs to be converted to lyrics videos or music videos. Furthermore, once a playlist has been created, the user is able to export data about the Spotify playlist as a CSV file as well as another CSV file that contains the video IDs of all the songs added to their YouTube playlist.<br><br>
# Getting Started

## Prerequisites
Make sure you have Python3 installed and you use it to run this program.
```
pip install dearpygui
```
```
pip install --upgrade google-api-python-client
```
```
pip install --upgrade google-auth-oauthlib google-auth-httplib2
```
## APIs
You are required to get the API key from Spotify, as well as the API key and OAuth 2.0 Client IDs from Google.<br>
* [Follow Step 1 on this guide to get an API key and an OAuth 2.0 client ID for the YouTube API](https://developers.google.com/youtube/v3/quickstart/python)
* [Follow the steps here to get CLIENT_ID and CLIENT_SECRET keys for the Spotify API](https://developer.spotify.com/documentation/web-api/quick-start/)<br><br>

# Basic Functionality and Future Improvements
<ins>Basic Functionality:</ins>
* Input Spotify playlist link
* Choose whether the YouTube playlist should consist of lyrics videos or music videos
* Set the privacy status of your new playlist (public, private or unlisted)
* Choose the name of your new playlist
* Creates the playlist using the user's YouTube account
* Generates a link that takes the user to their playlist<br>
* Allows the user to export data about their Spotify and YouTube playlists in two seperate CSV files
<div dr="rtl"><ins>Future Improvements</u></div>

* Give user more specific instructions on why their playlist could not be generated (e.g., they have input a link to an album instead of a playlist, they have input a playlist that is private so they need to make their playlist public)
* Provide error checking to make sure that all of the songs in the YouTube playlist match the Spotify playlist, and allow the user to replace any incorrect songs in-app by providing the correct URL for these songs
* Upgrade the UI so that the application looks more modern, and improve the speed of the program since certain functions had to be run multiple times simply due to the limitations of Dear PyGui
* Another improvement is to verify the app via the Google Cloud Console, so that users don't have to input an authentication code. Furthermore, applying for a quota increase for the YouTube Data API v3, so that users are able to convert more songs in a single day. Note: this is not related to the code itself, but moreso the account that uses the YouTube API.
<br><br>
# Project Demo
Video example: [https://www.youtube.com/watch?v=5ACiHCeikwo](https://www.youtube.com/watch?v=5ACiHCeikwo)
