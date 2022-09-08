import pickle
import spotipy
import os
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import math
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth


class UpdatePlaylist:

    def __init__(self, playlist_id):
        self.youtube_playlist_id = playlist_id
        self.youtube_client, self.playlist_title = self.get_youtube_client()
        # can maybe put this somewhere else
        self.spotify_client = spotipy.Spotify(auth_manager=SpotifyOAuth(scope="user-library-read, playlist-modify-public"))
        
        self.spotify_playlist_id = self.create_spotify_playlist()
        self.titles = []

    def update_spotify_playlist(self):
        uris = []
        print("Searching for Spotify Titles")
        for song_title in self.titles:
            uri = self.search_song(song_title)
            uris.append(uri)
        print("Found all Spotify Titles")
        print(f"Adding Spotify Titles to Playlist: {self.playlist_title}")
        self.spotify_client.playlist_add_items(self.spotify_playlist_id, uris)
        print(f"Updated Spotify Playlist: {self.playlist_title}")
        return

    def create_spotify_playlist(self):

        print(self.spotify_client.current_user())
        user_id = self.spotify_client.current_user()['id']
        # TODO: adjust to update an existing Spotify playlist based on changes to YT playlist
        playlist_info = self.spotify_client.user_playlist_create(user_id, self.playlist_title, public=True, description='')
        print(f"Created Spotify Playlist: {self.playlist_title}")
        return playlist_info['id']


    def get_youtube_client(self):
        
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

        # retrieve title of playlist from YT
        request = youtube.playlists().list(
            part="snippet,contentDetails",
            id=self.youtube_playlist_id
        )
        response = request.execute()
        
        playlist_title = response['items'][0]['snippet']['title']

        # Save the credentials for the next run
        with open('token.pickle', 'wb') as f:
            print('Saving Credentials for Future Use...')
            pickle.dump(credentials, f)

        return youtube, playlist_title

    def get_youtube_titles(self, youtube_client):
        print("Searching for YouTube Video Titles")

        next_page_token = -1
        index = 0

        while next_page_token is not None:
            # first token but can't be None
            if next_page_token == -1:
                next_page_token = None
            request = youtube_client.playlistItems().list(
                part='contentDetails',
                playlistId=self.youtube_playlist_id,
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
            request = youtube_client.videos().list(
                part="snippet,contentDetails,statistics",
                id=vid_id[:-1] # take out last comma
            )
        
            response = request.execute()
            for vid_info in response['items']:
                title = vid_info['snippet']['title']
                vid_titles.append(title)

        self.titles = vid_titles
        print("Found YouTube Video Titles")

        return vid_titles

    def search_song(self, title):
        result = self.spotify_client.search(title, 1, 0)
        uri = result['tracks']['items'][0]['uri']
        return uri


if __name__ == '__main__':
    # TODO: change to reverse as well (Spotify to YT)
    load_dotenv()
    playlist_id = input("Enter your YouTube playlist ID: ")

    update = UpdatePlaylist(playlist_id)

    update.get_youtube_titles(update.youtube_client)
    update.update_spotify_playlist()
