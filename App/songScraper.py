import json
import os
import re
import requests
import urllib.request
from bs4 import BeautifulSoup
from requests_aws4auth import AWS4Auth
from credentials import *

def get_lyrics(artist_name, song_title):
    base_url = 'https://api.genius.com'
    headers = {'Authorization': 'Bearer ' + genius_token}
    search_url = base_url + '/search'
    data = {'q': song_title + ' ' + artist_name}
    response = requests.get(search_url, data=data, headers=headers)

    remote_song_info = None
    for hit in response.json()['response']['hits']:
        if artist_name.lower() in hit['result']['primary_artist']['name'].lower():
            remote_song_info = hit
            break
    
    if remote_song_info:
        song_url = remote_song_info['result']['url']
        page = requests.get(song_url)
        html = BeautifulSoup(page.text, 'html.parser')
        return html.find('div', class_='lyrics').get_text()

    return None


# Send a post request to the AWS with the songlist
def query_lambda(lyrics_list, task, total):
    endpoint = 'https://ce3xt72isc.execute-api.us-east-1.amazonaws.com/testStage/'
    auth = AWS4Auth(aws_access_key_id, aws_secret_access_key, 'us-east-1', 'lambda')
    response = requests.post(endpoint, auth=auth, data=json.dumps({'songs': lyrics_list}))
    task.update_state(state='PROGRESS', meta={'current': total, 'total': total})
    return json.loads(response.text)["body"]


# Helper function to parse API responses
def parse_list(task, top, recent):
    tracks = set()
    for track in top['items']:
        tracks.add((track['name'], track['artists'][0]['name']))
    for track in recent['items']:
        track = track['track']
        tracks.add(((track['name'], track['artists'][0]['name'])))
    
    total = int(len(tracks)*1.25)

    # Set the initial progress to 0 and the total to len(tracks)
    lyrics_list = []
    for idx, track in enumerate(tracks):
        task.update_state(state='PROGRESS', meta={'current': idx + 1, 'total': total})
        lyrics = get_lyrics(track[1], track[0])
        if lyrics != None:
            lyrics_list.append(lyrics)

    return query_lambda(lyrics_list, task, total)
