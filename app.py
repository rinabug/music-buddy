import os
import sqlite3
from flask import Flask, render_template, request, redirect, session, url_for, flash
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import FlaskSessionCacheHandler
from backend.user_auth import create_users_table, is_valid_email, is_valid_password, hash_password
from backend.friend_system import create_friend_tables, send_friend_request, view_friend_requests, accept_friend_request, view_friends

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(64)
DATABASE = 'users.db'

client_id = '6d71bbd76afd4e52a9399c06a7d36124'
client_secret = '59fdb7c8afab4c03afc3021435f49d83'
redirect_uri = 'http://localhost:8080/callback'
scope = 'playlist-read-private,user-follow-read,user-top-read,user-read-recently-played'
cache_handler = FlaskSessionCacheHandler(session)

sp_oauth = SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope=scope,
    cache_handler=cache_handler,
    show_dialog=True
)

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    return conn

@app.before_request
def initialize_database():
    conn = get_db_connection()
    create_users_table(conn)
    create_friend_tables(conn)
    conn.close()

@app.route('/')
def start_page():
    if 'token_info' in session:
        return redirect(url_for('index'))
    return render_template('start-page.html')

@app.route('/loginSpotify')
def loginSpotify():
    return redirect(sp_oauth.get_authorize_url())

@app.route('/callback')
def callback():
    token_info = sp_oauth.get_access_token(request.args['code'])
    session['token_info'] = token_info
    return redirect(url_for('index'))

@app.route('/index')
def index():
    token_info = session.get('token_info', None)
    if not token_info:
        return redirect(url_for('login'))
    
    sp = Spotify(auth=token_info['access_token'])
    playlists = sp.current_user_playlists()
    playlists_info = [(pl['name'], pl['external_urls']['spotify']) for pl in playlists['items']]
    return render_template('index.html', playlists_info=playlists_info)

@app.route('/get_playlists')
def get_playlists():
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)
    
    sp = Spotify(auth_manager=sp_oauth)
    playlists = sp.current_user_playlists()
    playlists_info = [(pl['name'], pl['external_urls']['spotify']) for pl in playlists['items']]
    playlists_html = '<br>'.join([f'<a href="{url}">{name}</a>' for name, url in playlists_info])
    return f'<h1>Your Playlists</h1>{playlists_html}<br><a href="/logout">Logout</a>'

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('start_page'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

@app.route('/friend_requests', methods=['GET', 'POST'])
def friend_requests():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    username = session['username']
    
    if request.method == 'POST':
        if 'send_request' in request.form:
            receiver_username = request.form['receiver_username']
            send_friend_request(conn, username, receiver_username)
        elif 'accept_request' in request.form:
            request_id = request.form['request_id']
            accept_friend_request(conn, username, request_id)
    
    friend_requests_list = view_friend_requests(conn, username)
    friends = view_friends(conn, username)
    conn.close()
    
    return render_template('friend_requests.html', friend_requests=friend_requests_list, friends=friends)

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/discover')
def discover():
    return render_template('discover.html')

@app.route('/collab')
def collab():
    return render_template('collab.html')

if __name__ == '__main__':
    app.run(debug=True, port=8080)
