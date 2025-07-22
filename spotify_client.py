import spotipy
from spotipy.oauth2 import SpotifyOAuth


class SpotifyClient:

    def __init__(self):
        self.spotify_client = spotipy.Spotify(auth_manager=SpotifyOAuth(scope="user-library-read, playlist-modify-public"))
        self.spotify_playlist_id = ""
        self.titles = []

    def update_spotify_playlist(self, title):
        if self.spotify_playlist_id == "":
            self.spotify_playlist_id = self.create_playlist(title)
        uris = []
        print("Searching for Spotify Titles")
        for song_title in self.titles:
            uri = self.getSongId(song_title)
            uris.append(uri)
        print("Found all Spotify Titles")
        print(f"Adding Spotify Titles to Playlist: {title}")
        self.spotify_client.playlist_add_items(self.spotify_playlist_id, uris)
        print(f"Updated Spotify Playlist: {title}")
        return

    def create_playlist(self, title):
        print(self.spotify_client.current_user())
        user_id = self.spotify_client.current_user()['id']
        playlist_info = self.spotify_client.user_playlist_create(user_id, title, public=True, description='')
        print(f"Created Spotify Playlist: {title}")
        return playlist_info['id']

    def getSongId(self, title):
        result = self.spotify_client.search(title, 3)
        uri = result['tracks']['items'][0]['uri']
        return uri