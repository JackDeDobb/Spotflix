import json
import os
import re
import requests
import sys
import spotipy
import spotipy.util as util
import urllib.request
from bs4 import BeautifulSoup
from credentials import *
from requests_aws4auth import AWS4Auth

def get_lyrics(artist,song_title):
    
    # remove all except alphanumeric characters from artist and song_title
    artist = re.sub('[^A-Za-z0-9]+', "", artist.lower())
    song_title = re.sub('[^A-Za-z0-9]+', "", song_title.lower())
    
    if artist.startswith("the"):    # remove starting 'the' from artist e.g. the who -> who
        artist = artist[3:]
    url = "http://azlyrics.com/lyrics/"+artist+"/"+song_title+".html"
    
    try:
        content = urllib.request.urlopen(url).read()
        soup = BeautifulSoup(content, 'html.parser')
        lyrics = str(soup)
        # lyrics lies between up_partition and down_partition
        up_partition = '<!-- Usage of azlyrics.com content by any third-party lyrics provider is prohibited by our licensing agreement. Sorry about that. -->'
        down_partition = '<!-- MxM banner -->'
        lyrics = lyrics.split(up_partition)[1]
        lyrics = lyrics.split(down_partition)[0]
        lyrics = lyrics.replace('<br>','').replace('</br>','').replace('</div>','').strip()
        return lyrics

    except Exception as e:
        print("Exception occurred \n" +str(e))
        return None


# Send a post request to the AWS with the songlist
def query_lambda(lyrics_list):

    endpoint = 'https://ce3xt72isc.execute-api.us-east-1.amazonaws.com/testStage/'
    auth = AWS4Auth(aws_access_key_id, aws_secret_access_key, 'us-east-1', 'lambda')
    params = {}
    params['songs'] = lyrics_list
    response = requests.post(endpoint, auth=auth, data=json.dumps(params))
    
    # Creates a list of movie titles for now
    response = json.loads(response.text)["body"]
    return response

# Helper function to parse API responses
def parse_list(top,recent):

    tracks = set()
    tracks_list = []
    lyrics_list = []
    
    for track in top['items']:
        if track['name'] not in tracks:
            tracks.add(track['name'])
            tracks_list.append(track)

    for track in recent['items']:
        track = track['track']
        if track['name'] not in tracks:
            tracks.add(track['name'])
            tracks_list.append(track)

    for track in tracks_list:
        lyrics = get_lyrics(track['artists'][0]['name'], track['name'])
        if lyrics != None:
            lyrics_list.append(lyrics)

    response = query_lambda(lyrics_list)

    return response
