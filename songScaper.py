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



if __name__ == "__main__":
    os.environ["SPOTIPY_CLIENT_ID"] = sp_client_id
    os.environ["SPOTIPY_CLIENT_SECRET"] = sp_client_secret
    os.environ["SPOTIPY_REDIRECT_URI"] = "http://localhost:8000/callback"

    token = util.prompt_for_user_token(sp_username, 'user-library-read')
    if token == None:
        print("Can't get token for ", sp_username)
        exit
    
    #get lyrics of all songs in current user saved tracks
    lyricsList = []
    sp = spotipy.Spotify(auth=token)
    results = sp.current_user_saved_tracks()['items']
    for item in results:
        track = item['track']
        print(track['name'] + ' - ' + track['artists'][0]['name'])
        lyrics = get_lyrics(track['artists'][0]['name'], track['name'])
        if lyrics != None:
            lyricsList.append(lyrics)
    
    #add code here to get all lyrics of songs in either current user recently played or current user top tracks using curl



    #aws lambda magic hitting API endpoint
    from requests_aws4auth import AWS4Auth
    endpoint = 'https://ce3xt72isc.execute-api.us-east-1.amazonaws.com/testStage/'
    auth = AWS4Auth(aws_access_key_id, aws_secret_access_key, 'us-east-1', 'lambda')
    otherDict = {}
    otherDict['songs'] = lyricsList
    response = requests.post(endpoint, auth=auth, data=json.dumps(otherDict))
    print(response.text)
