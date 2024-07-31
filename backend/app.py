# app.py

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

DEVELOPER_TOKEN = os.getenv('DEVELOPER_TOKEN')
USER_TOKEN = os.getenv('USER_TOKEN')

def search_playlists(query):
    url = f'https://api.music.apple.com/v1/catalog/us/search?term={query}&types=playlists'
    headers = {
        'Authorization': f'Bearer {DEVELOPER_TOKEN}',
        'Music-User-Token': USER_TOKEN
    }
    response = requests.get(url, headers=headers)
    return response.json()

def get_playlist_tracks(playlist_id):
    url = f'https://api.music.apple.com/v1/catalog/us/playlists/{playlist_id}'
    headers = {
        'Authorization': f'Bearer {DEVELOPER_TOKEN}',
        'Music-User-Token': USER_TOKEN
    }
    response = requests.get(url, headers=headers)
    data = response.json()
    tracks = data['data'][0]['relationships']['tracks']['data']
    return [track['id'] for track in tracks]

def create_playlist(name, description, track_ids):
    url = 'https://api.music.apple.com/v1/me/library/playlists'
    headers = {
        'Authorization': f'Bearer {DEVELOPER_TOKEN}',
        'Music-User-Token': USER_TOKEN,
        'Content-Type': 'application/json'
    }
    playlist_data = {
        'attributes': {
            'name': name,
            'description': description
        },
        'relationships': {
            'tracks': {
                'data': [{'id': track_id, 'type': 'songs'} for track_id in track_ids]
            }
        }
    }
    response = requests.post(url, json=playlist_data, headers=headers)
    return response.json()

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    playlists = search_playlists(query)
    return jsonify(playlists)

@app.route('/tracks/<playlist_id>', methods=['GET'])
def tracks(playlist_id):
    tracks = get_playlist_tracks(playlist_id)
    return jsonify(tracks)

@app.route('/create_playlist', methods=['POST'])
def create():
    data = request.json
    name = data.get('name')
    description = data.get('description')
    track_ids = data.get('track_ids')
    new_playlist = create_playlist(name, description, track_ids)
    return jsonify(new_playlist)

if __name__ == '__main__':
    app.run(debug=True)
