import json
import os
import re
import requests
import urllib.request
from bs4 import BeautifulSoup
from requests_aws4auth import AWS4Auth
from credentials import *

def get_lyrics(artist_name,song_title):
    base_url = 'https://api.genius.com'
    headers = {'Authorization': 'Bearer ' + genius_token}
    search_url = base_url + '/search'
    data = {'q': song_title + ' ' + artist_name}
    response = requests.get(search_url, data=data, headers=headers)

    json = response.json()
    remote_song_info = None

    for hit in json['response']['hits']:
        if artist_name.lower() in hit['result']['primary_artist']['name'].lower():
            remote_song_info = hit
            break
    
    if remote_song_info:
        song_url = remote_song_info['result']['url']
        page = requests.get(song_url)
        html = BeautifulSoup(page.text, 'html.parser')
        lyrics = html.find('div', class_='lyrics').get_text()
        return lyrics

    return None


# Send a post request to the AWS with the songlist
def query_lambda(lyrics_list,task,total):

    endpoint = 'https://ce3xt72isc.execute-api.us-east-1.amazonaws.com/testStage/'
    auth = AWS4Auth(aws_access_key_id, aws_secret_access_key, 'us-east-1', 'lambda')
    params = {}
    params['songs'] = lyrics_list
    response = requests.post(endpoint, auth=auth, data=json.dumps(params))
    task.update_state(state='PROGRESS',meta={'current': total, 'total': total})
    # Creates a list of movie titles for now
    response = json.loads(response.text)["body"]
    return response

# Helper function to parse API responses
def parse_list(task,top,recent):

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
    
    count = 0
    total = int(len(tracks)*1.5)
    print("Total:")
    print(total)

    # Set the initial progress to 0 and the total to len(tracks)
    task.update_state(state='PROGRESS',meta={'current': count, 'total':total})

    for track in tracks_list:
        lyrics = get_lyrics(track['artists'][0]['name'], track['name'])
        count += 1
        
        # Increment the progress by 1
        task.update_state(state='PROGRESS',meta={'current': count, 'total': total})
        
        if lyrics != None:
            lyrics_list.append(lyrics)

    #print(lyrics_list)
    response = query_lambda(lyrics_list,task,total)

    return response
