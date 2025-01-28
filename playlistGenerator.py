import requests
from bs4 import BeautifulSoup

# TODO: type checking

def retrieveHtml(url):
    html = requests.get(url)
    soup = BeautifulSoup(html.text, 'html.parser')
    return soup

def getSongList(soup):
    songs = []
    for song in soup.find_all(class_="songLabel"):
        songs.append(song.text)
    return songs

def getBandName(soup):
    band = soup.find(class_="setlistHeadline").find('span')
    return band

