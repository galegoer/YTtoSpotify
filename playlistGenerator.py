import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from youtube_client import YoutubeClient

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

def getBandName(soup):
    band = soup.find(class_="setlistHeadline").find('span').text
    return band

if __name__ == '__main__':
    # TODO: change to reverse as well (Spotify to YT)
    load_dotenv()

    setlist_url = input("Enter the Setlist FM URL: ")

    soup = retrieveHtml(setlist_url)
    songs = getSongList(soup)
    band = getBandName(soup)
    print(f"Found {len(songs)} songs for {band}")
    print(songs)
    client = YoutubeClient()
    playlist_id = client.createPlaylist(f"{band} Setlist") # TODO: add date to playlist title (band)
    for song in songs:
        song_id = client.getYoutubeSongId(song, band)
        client.addSongToPlaylist(playlist_id, song_id)