import requests
import urllib.parse
from flask import Flask , redirect , request , jsonify , session
from pytube import YouTube
import os
import googleapiclient.discovery

API_KEY = "AIzaSyBWLPatJaPNdqB6FgcZVBzVmL99WJzkp3o"

youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=API_KEY)

app = Flask(__name__)
app.secret_key = "ThisIsSecret"

CLIENT_ID = '4ca87b810a644820bbc54915184a59f2'
CLIENT_SECRET = 'e6a93e3ec969479499f7a41e094bd936'
REDIRECT_URI = 'http://127.0.0.1:5000/callback'    

AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'
API_BASE_URL = 'https://api.spotify.com/v1/'

@app.route('/')
def index():
    return "Thank you for using my spotify downloader <a href = '/login'> click on this to login </a>"

@app.route('/login')
def login():
    scope = "playlist-read-private"

    params = {
        'client_id' : CLIENT_ID,
        'response_type' : 'code',
        'redirect_uri' : REDIRECT_URI,
        'scope' : scope
    }

    auth_url = f"{AUTH_URL}?{urllib.parse.urlencode(params)}"
    return redirect(auth_url)

@app.route('/callback')
def callback():
    params = {
        'grant_type' : 'authorization_code',
        'code' : request.args['code'],
        'redirect_uri' : REDIRECT_URI,
        'client_id' : CLIENT_ID,
        'client_secret' : CLIENT_SECRET
    }

    response = requests.post(TOKEN_URL, data=params)
    token_info = response.json()
    
    session['access_token'] = token_info['access_token']

    return redirect('/playlists')
LIST_id = []
LIST_name = []
SONGS = []
ARTISTS = []
@app.route('/playlists')
def playlists():

    headers = {
        'authorization' : f"Bearer {session['access_token']}"
    }

    response = requests.get(f"{API_BASE_URL}me/playlists?limit=2" , headers=headers)
    playlist_list = response.json()
    for data in playlist_list['items']:
        LIST_id.append(data['id'])
        LIST_name.append(data['name'])

    for i in range (0 , len(LIST_id)):
        song = []
        artists = []
        response = requests.get(f"{API_BASE_URL}playlists/{LIST_id[i]}/tracks" , headers=headers)
        
        playlist_tracks = response.json()
        
        for j in playlist_tracks['items']:
            song.append(j['track']['name'])
            artists.append(j['track']['album']['artists'][0]['name'])
        SONGS.append(song)
        ARTISTS.append(artists)
    
    return redirect('/download')

@app.route('/download')
def download():

    for i in range(0 , len(LIST_id)):
        for j in range(0, len(SONGS[i])):
            search_results = youtube.search().list(
                maxResults = 1,
                q = SONGS[i][j] +" - "+ ARTISTS[i][j],
                part = "snippet"
            ).execute()
            #print(search_results)
            url = f"https://www.youtube.com/watch?v={search_results['items'][0]['id']['videoId']}"
            
            mp4 = YouTube(url)

            mp4 = mp4.streams.get_audio_only()

            mp4.download()
        os.mkdir(f'{LIST_name[i]}')
        files = os.listdir()
        for file in files:
            if file[-3:] == "mp4":
                
                os.rename(file , f"{LIST_name[i]}/{file}")    
    return "Thank You"




if(__name__ == "__main__"):
    app.run(host = '0.0.0.0')