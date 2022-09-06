import pickle
from httplib2 import Credentials
import spotipy
import os
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import math

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

        next_page_token = -1
        index = 0

        while next_page_token is not None:
            # first token but can't be None
            if next_page_token == -1:
                next_page_token = None
            request = youtube.playlistItems().list(
                part='contentDetails',
                playlistId=playlist_id,
                maxResults=50,
                pageToken=next_page_token
            )

            response = request.execute()
            next_page_token = response.get('nextPageToken')
            total_vids = response['pageInfo']['totalResults']

            # init array to hold ids of size 50
            if index == 0:
                # need to separate vid_ids in groups of 50
                arr_space = math.ceil(total_vids / 50)
                vid_ids = [''] * arr_space

            for item in response['items']:
                vid_id = item['contentDetails']['videoId']
                vid_ids[index] = vid_ids[index] + vid_id + ','
            index += 1

        vid_titles = []

        for vid_id in vid_ids:
            request = youtube.videos().list(
                part="snippet,contentDetails,statistics",
                id=vid_id[:-1] # take out last comma
            )
        
            response = request.execute()
            for vid_info in response['items']:
                title = vid_info['snippet']['title']
                vid_titles.append(title)
        
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as f:
            print('Saving Credentials for Future Use...')
            pickle.dump(credentials, f)


if __name__ == '__main__':
    # May change to reverse as well (Spotify to YT)
    playlist_id = input("Enter your YouTube playlist ID: ")

    update = UpdatePlaylist(playlist_id)
    # update.update_spotify_playlist()