import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from youtube_client import YoutubeClient
from spotify_client import SpotifyClient

# TODO: type checking

def retrieveHtml(url):
    try:
        html = requests.get(url)
        soup = BeautifulSoup(html.text, 'html.parser')
        return soup
    except Exception:
        print("Failed to retrieve HTML")
        raise

def getSongList(soup):
    songs = []
    for song in soup.find_all(class_="songLabel"):
        songs.append(song.text)
    return songs

def getTourName(soup):
    try:
        tour = soup.find(class_="infoContainer").find('p').find_next('span').find_next('span').text
        return tour
    except:
        return ""

def getBandName(soup):
    band = soup.find(class_="setlistHeadline").find('span').text
    return band

if __name__ == '__main__':
    load_dotenv()
    playlist_type = input("Do you want YouTube or Spotify playlist? ")
    setlist_url = input("Enter the Setlist FM URL: ")

    soup = retrieveHtml(setlist_url)
    songs = getSongList(soup)
    band = getBandName(soup)
    tour = getTourName(soup)
    if tour:
        playlist_name = f"{band} Setlist {tour}"
    else:
        playlist_name = f"{band} Setlist"
    
    cleaned_songs = []
    for song in songs:
        # In the case of multiple songs in one they do a slash
        sub_songs = song.split("/")
        for sub_song in sub_songs:
            cleaned_songs.append(f"{sub_song.strip()} {band}")

    print(f"Found {len(cleaned_songs)} songs for {band}") 
    print(cleaned_songs)

    if playlist_type == "Spotify":
        client = SpotifyClient()
        client.titles = cleaned_songs
        client.update_spotify_playlist(title=playlist_name)
    else:
        client = YoutubeClient()
        playlist_id = client.createPlaylist(playlist_name)
        for song in cleaned_songs:
            song_id = client.getSongId(song, band)
            client.addSongToPlaylist(playlist_id, song_id)