import pickle
import re
from httplib2 import Credentials
import spotipy
import os
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import math
import json
import requests
from dotenv import load_dotenv

from spotipy.oauth2 import SpotifyOAuth


class UpdatePlaylist:

    def __init__(self, playlist_id):
        self.youtube_playlist_id = playlist_id
        self.youtube_client, self.playlist_title = self.get_youtube_client()
        self.spotify_playlist_id = self.create_spotify_playlist()
        # can maybe put this somewhere else
        self.spotify_client = spotipy.Spotify(auth_manager=SpotifyOAuth(scope="user-library-read, playlist-modify-public"))
        self.titles = []

    def update_spotify_playlist(self):
        for song_title in self.titles:
            self.search_song(song_title)

    # def get_playlist_title(self, youtube_client):
    #     request = youtube_client.playlists().list(
    #         part="snippet,contentDetails",
    #         id=self.playlist_id
    #     )
    #     response = request.execute()
        
    #     return response['items']['snippet']['title']

    def create_spotify_playlist(self):

        print(self.spotify_client.current_user())
        user_id = self.spotify_client.current_user()['id']
        # can adjust later to update an existing Spotify playlist based on changes to YT playlist
        playlist_info = self.spotify_client.user_playlist_create(user_id, 'temp', public=True, description='')
        print(playlist_info['id'])
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
        print(response)
        
        playlist_title = response['items']['snippet']['title']

        # Save the credentials for the next run
        with open('token.pickle', 'wb') as f:
            print('Saving Credentials for Future Use...')
            pickle.dump(credentials, f)

        return youtube, playlist_title

    def get_youtube_titles(self, youtube_client):

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
        
        return vid_titles

    def search_song(self, title):
        result = self.spotify_client.search(title, 3, 0, 'track')
        print(result)
        return result


if __name__ == '__main__':
    # May change to reverse as well (Spotify to YT)
    load_dotenv()
    playlist_id = input("Enter your YouTube playlist ID: ")

    # search needs to be tested
    # test_title = ['Everybody Wants to Rule the World']
    # update = UpdatePlaylist(playlist_id)
    # update.titles = test_title

    # print(update)
    # print(update.titles)
    # titles = update.get_youtube_titles(update.youtube_client)
    # print(titles)

