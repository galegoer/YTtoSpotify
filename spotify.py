import pickle
from httplib2 import Credentials
import spotipy
import os
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

from spotipy.oauth2 import SpotifyClientCredentials


class UpdatePlaylist:

    def __init__(self, playlist_id):
        self.playlist_id = playlist_id
        self.youtube_client = self.get_playlist(playlist_id)
        self.all_song_info = {}

    def update_spotify_playlist(self):
        created_playlist_id = self.create_playlist()

    def get_playlist(self, playlist_id):
        
        credentials = None
        nextPageToken = None
        
        if os.path.exists('token.pickle'):
            print('Loading Credentials From File...')
            with open('token.pickle', 'rb') as token:
                credentials = pickle.load(token)

        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                print('Refreshing Access Token...')
                credentials.refresh(Request())
            else:
                print('Fetching New Tokens...')
                flow = InstalledAppFlow.from_client_secrets_file(
                    'client_secrets.json',
                    scopes=[
                        'https://www.googleapis.com/auth/youtube.readonly'
                    ]
                )

                flow.run_local_server(port=8080, prompt='consent', authorization_prompt_message='')
                credentials = flow.credentials
                print(credentials)

        youtube = build('youtube', 'v3', credentials=credentials)
        print(credentials)

        request = youtube.playlistItems().list(
            part='contentDetails',
            playlistId=playlist_id,
            maxResults=50,
            pageToken=nextPageToken
        )

        response = request.execute()

        print(response)

        # Save the credentials for the next run
        with open('token.pickle', 'wb') as f:
            print('Saving Credentials for Future Use...')
            pickle.dump(credentials, f)


if __name__ == '__main__':
    # May change to reverse as well (Spotify to YT)
    playlist_id = input("Enter your YouTube playlist ID: ")

    update = UpdatePlaylist(playlist_id)
    # update.update_spotify_playlist()