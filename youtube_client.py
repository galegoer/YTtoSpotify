import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

class YoutubeClient:
    def __init__(self):
        self.youtube_client = self.get_youtube_client()

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
                        'https://www.googleapis.com/auth/youtube'
                    ]
                )

                flow.run_local_server(port=8080, prompt='consent', authorization_prompt_message='')
                credentials = flow.credentials
                print(credentials)

        youtube = build('youtube', 'v3', credentials=credentials)
        
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as f:
            print('Saving Credentials for Future Use...')
            pickle.dump(credentials, f)

        return youtube
    
    def getYoutubeSongId(self, song, band):
        # retrieve title of playlist from YT
        request = self.youtube_client.search().list(
            part="snippet",
            q=f"{song} {band}",
        )
        response = request.execute()

        try:
            video_id = response['items'][0]['id']['videoId']
            print(video_id)
            return video_id
        except Exception as e:
            # TODO: retry
            print(f"No video found: {e}")

    def addSongToPlaylist(self, playlistId, songId):
        # TODO: Refactor similar code for sending requests
        request = self.youtube_client.playlistItems().insert(
            part="snippet",
            body={
                "snippet": {
                    "playlistId": playlistId,
                    "resourceId": {
                        "kind": "youtube#video",
                        "videoId": songId
                    }
                }
            }
        )
        try:
            response = request.execute()
            print(response)
        except Exception as e:
            # TODO: retry
            print(f"Failed to add song to playlist: {songId}, Error: {e}")

    def createPlaylist(self, playlistTitle):
        # TODO: Make private public option
        request = self.youtube_client.playlists().insert(
            part="snippet",
            body={
                "snippet": {
                    "title": playlistTitle
                }
            }
        )
        try:
            response = request.execute()
            playlistId = response['id']
            print(playlistId)
            return playlistId
        except Exception as e:
            # TODO: retry
            print(f"Failed to create playlist: {e}")

