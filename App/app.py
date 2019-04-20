import json
from flask import Flask, request, redirect, g, render_template
import requests
from urllib.parse import quote
from credentials import *
from songScraper import *

# Authentication Steps, paramaters, and responses are defined at https://developer.spotify.com/web-api/authorization-guide/
# Visit this url to see all the steps, parameters, and expected response.


app = Flask(__name__)

#  Client Keys
CLIENT_ID = sp_client_id
CLIENT_SECRET = sp_client_secret

# Spotify URLS
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE_URL = "https://api.spotify.com"
API_VERSION = "v1"
SPOTIFY_API_URL = "{}/{}".format(SPOTIFY_API_BASE_URL, API_VERSION)

# Server-side Parameters
CLIENT_SIDE_URL = "http://127.0.0.1"
PORT = 8080
REDIRECT_URI = "{}:{}/callback/q".format(CLIENT_SIDE_URL, PORT)
SCOPE = "user-top-read user-read-recently-played"
STATE = ""
SHOW_DIALOG_bool = True
SHOW_DIALOG_str = str(SHOW_DIALOG_bool).lower()

auth_query_parameters = {
    "response_type": "code",
    "redirect_uri": REDIRECT_URI,
    "scope": SCOPE,
    # "state": STATE,
    # "show_dialog": SHOW_DIALOG_str,
    "client_id": CLIENT_ID
}


@app.route("/")
def index():
    # Auth Step 1: Authorization
    url_args = "&".join(["{}={}".format(key, quote(val)) for key, val in auth_query_parameters.items()])
    auth_url = "{}/?{}".format(SPOTIFY_AUTH_URL, url_args)
    return redirect(auth_url)


@app.route("/callback/q")
def callback():
    # Auth Step 4: Requests refresh and access tokens
    auth_token = request.args['code']
    code_payload = {
        "grant_type": "authorization_code",
        "code": str(auth_token),
        "redirect_uri": REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
    }
    post_request = requests.post(SPOTIFY_TOKEN_URL, data=code_payload)

    # Auth Step 5: Tokens are Returned to Application
    response_data = json.loads(post_request.text)
    access_token = response_data["access_token"]
    refresh_token = response_data["refresh_token"]
    token_type = response_data["token_type"]
    expires_in = response_data["expires_in"]

    # Auth Step 6: Use the access token to access Spotify API
    authorization_header = {"Authorization": "Bearer {}".format(access_token)}

    # Get profile data
    user_profile_api_endpoint = "{}/me".format(SPOTIFY_API_URL)
    profile_response = requests.get(user_profile_api_endpoint, headers=authorization_header)
    profile_data = json.loads(profile_response.text)
    print(profile_data)

    # Get top tracks data
    recent_api_endpoint = "{}/me/player/recently-played".format(SPOTIFY_API_URL)
    params = {'limit':30}
    recent_response = requests.get(recent_api_endpoint, headers=authorization_header, params=params)
    recent_data = json.loads(recent_response.text)
    print(recent_data)

    # Get most recent tracks data
    top_api_endpoint = "{}/me/top/tracks".format(SPOTIFY_API_URL)
    params = {'limit':30}
    top_response = requests.get(top_api_endpoint, headers=authorization_header,params=params)
    top_data = json.loads(top_response.text)
    print(top_data)


    # Combine profile and playlist data to display
    display_arr = [profile_data] + top_data["items"]
    return render_template("index.html", sorted_array=display_arr)


if __name__ == "__main__":
    app.run(debug=True, port=PORT)
