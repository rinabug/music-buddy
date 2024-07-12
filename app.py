import os
import sqlite3
from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import FlaskSessionCacheHandler
from backend.user_auth import create_users_table, is_valid_email, is_valid_password, hash_password
from backend.friend_system import create_friend_tables, send_friend_request, view_friend_requests, accept_friend_request, view_friends
from backend.trivia import create_leaderboard_table, get_leaderboard, generate_trivia_question, update_score
from backend.badges import create_badges_table, get_user_badges, check_and_award_badges
from backend.concert_recommendations import get_concert_recommendations
from backend.music_recommendation import get_music_recommendations

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(64)
DATABASE = 'users.db'

client_id = '908db28b7d8e4d03888632068918bff1'
client_secret = '92919a8126964ba5b4da358d97c729ef'
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
    create_leaderboard_table(conn)
    create_badges_table(conn)
    conn.close()

@app.route('/')
def start_page():
    if 'username' in session:
        return redirect(url_for('index'))
    return render_template('start-page.html')

@app.route('/loginSpotify')
def loginSpotify():
    if 'username' not in session:
        flash("Please log in to your account first before connecting Spotify.")
        return redirect(url_for('login'))
    return redirect(sp_oauth.get_authorize_url())

@app.route('/callback')
def callback():
    if 'username' not in session:
        flash("Please log in to your account first.")
        return redirect(url_for('login'))
    
    token_info = sp_oauth.get_access_token(request.args['code'])
    session['token_info'] = token_info
    return redirect(url_for('index'))

@app.route('/index')
def index():
    if 'username' not in session:
        flash("Please log in to access this page.")
        return redirect(url_for('login'))

    username = session['username']

    token_info = session.get('token_info', None)
    if not token_info:
        flash("Please connect your Spotify account.")
        return redirect(url_for('loginSpotify'))

    try:
        sp = Spotify(auth=token_info['access_token'])
        playlists = sp.current_user_playlists()
        playlists_info = [(pl['name'], pl['external_urls']['spotify']) for pl in playlists['items']]
    except Exception as e:
        print(f"Error fetching Spotify playlists: {e}")
        flash("There was an error connecting to Spotify. Please try logging in again.")
        return redirect(url_for('loginSpotify'))

    # Fetch leaderboard data
    conn = get_db_connection()
    leaderboard = get_leaderboard(conn)

    # Generate a trivia question
    question_data = generate_trivia_question("Billie Eilish")
    if question_data:
        session['current_question'] = question_data
        question = question_data['question']
        options = question_data['options']
    else:
        question = None
        options = None

    conn.close()

    return render_template('index.html',
                           username=username,
                           playlists_info=playlists_info,
                           leaderboard=leaderboard,
                           question=question,
                           options=options)

@app.route('/get_leaderboard')
def get_leaderboard_route():
    conn = get_db_connection()
    leaderboard = get_leaderboard(conn)
    conn.close()
    return jsonify(leaderboard)

@app.route('/get_trivia_question')
def get_trivia_question():
    question_data = generate_trivia_question("Billie Eilish")
    session['current_question'] = question_data
    return jsonify(question_data)

@app.route('/answer_trivia', methods=['POST'])
def answer_trivia():
    if 'username' not in session or 'current_question' not in session:
        return jsonify({'status': 'error', 'message': 'Invalid session'}), 400

    data = request.get_json()
    user_answer = data.get('answer')
    current_question = session['current_question']

    if user_answer == current_question['correct_answer']:
        conn = get_db_connection()
        update_score(conn, session['username'], 1)
        check_and_award_badges(conn, session['username'])
        conn.close()
        result = {'status': 'correct', 'message': 'Correct answer!'}
    else:
        result = {'status': 'incorrect', 'message': f"Wrong answer. The correct answer was {current_question['correct_answer']}."}

    return jsonify(result)

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
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if username exists
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            flash("Username already taken.")
            return render_template('signup.html')
        
        # Check if email is valid and not already registered
        if not is_valid_email(email):
            flash("Invalid email address.")
            return render_template('signup.html')
        
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            flash("Email already registered.")
            return render_template('signup.html')
        
        # Check if password is valid
        if not is_valid_password(password):
            flash("Invalid password. It must be at least 8 characters long and contain at least one special character.")
            return render_template('signup.html')
        
        # Hash the password and insert the new user
        hashed_password = hash_password(password)
        cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", (username, email, hashed_password))
        conn.commit()
        conn.close()
        
        flash("Registration successful. Please log in.")
        return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        identifier = request.form['identifier']
        password = request.form['password']
        
        conn = get_db_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE username = ? OR email = ?", (identifier, identifier))
        user = cursor.fetchone()
        
        if user and user['password'] == hash_password(password):
            session['username'] = user['username']
            flash("Logged in successfully.")
            return redirect(url_for('index'))
        else:
            flash("Invalid username/email or password.")
        
        conn.close()
    
    return render_template('login.html')

@app.route('/profile')
def profile():
    if 'username' not in session:
        flash("Please log in to access this page.")
        return redirect(url_for('login'))
    
    username = session['username']
    conn = get_db_connection()
    friends = view_friends(conn, username)
    check_and_award_badges(conn, username)
    badges = get_user_badges(conn, username)
    conn.close()
    
    return render_template('profile.html', username=username, friends=friends, badges=badges)

@app.route('/send_friend_request', methods=['POST'])
def send_friend_request_route():
    if 'username' not in session:
        return jsonify({'status': 'error', 'message': 'Please log in.'}), 401
    
    data = request.get_json()
    receiver_username = data.get('receiver_username')
    
    conn = get_db_connection()
    result = send_friend_request(conn, session['username'], receiver_username)
    conn.close()
    if result:
        check_and_award_badges(conn, session['username'])
    conn.close()

    if result:
        return jsonify({'status': 'success', 'message': f'Friend request sent to {receiver_username}'})
    else:
        return jsonify({'status': 'error', 'message': 'User not found.'}), 404

@app.route('/view_friend_requests')
def view_friend_requests_route():
    if 'username' not in session:
        return jsonify({'status': 'error', 'message': 'Please log in.'}), 401
    
    conn = get_db_connection()
    requests = view_friend_requests(conn, session['username'])
    conn.close()
    
    if not requests:
        return jsonify({'status': 'success', 'message': 'No friend requests :(', 'requests': []})
    else:
        return jsonify({'status': 'success', 'requests': requests})

@app.route('/accept_friend_request', methods=['POST'])
def accept_friend_request_route():
    if 'username' not in session:
        return jsonify({'status': 'error', 'message': 'Please log in.'}), 401
    
    data = request.get_json()
    request_id = data.get('request_id')
    
    conn = get_db_connection()
    accept_friend_request(conn, session['username'], request_id)
    conn.close()
    
    return jsonify({'status': 'success', 'message': 'Friend request accepted'})

@app.route('/view_friends')
def view_friends_route():
    if 'username' not in session:
        return jsonify({'status': 'error', 'message': 'Please log in.'}), 401
    
    conn = get_db_connection()
    friends = view_friends(conn, session['username'])
    conn.close()
    
    return jsonify({'status': 'success', 'friends': friends})

@app.route('/discover')
def discover():
    token_info = session.get('token_info', None)
    try:
        sp = Spotify(auth=token_info['access_token'])
        
        top_artists = sp.current_user_top_artists(limit=5, time_range='short_term')
        genres = set()
        for artist in top_artists['items']:
            genres.update(artist['genres'])
        top_genres = list(genres)[:3]  

        user_location = "New York"  #change
        chatgpt_recommendation, all_events = get_concert_recommendations(user_location, top_genres, radius=50)
        music_recommendations = get_music_recommendations(sp)
        return render_template('discover.html', 
                               chatgpt_recommendation=chatgpt_recommendation,
                               all_events=all_events,music_recommendations=music_recommendations)
    except Exception as e:
        print(f"Error with recommendations: {e}")
        flash("There was an error.")
        return redirect(url_for('loginSpotify'))

@app.route('/collab')
def collab():
    return render_template('collab.html')

if __name__ == '__main__':
    app.run(debug=True, port=8080)
