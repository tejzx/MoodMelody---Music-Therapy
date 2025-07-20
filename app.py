import streamlit as st
import cv2
import numpy as np
import time
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
import base64
import json
import os
from PIL import Image
import matplotlib.pyplot as plt
import random
import requests
from io import BytesIO
import tempfile
from gtts import gTTS
import hashlib
import re

# Disable TensorFlow OneDNN optimization to fix compatibility issues
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

# Import DeepFace after setting environment variable
from deepface import DeepFace

# Set page configuration
st.set_page_config(
    page_title="MoodMelody - AI Music Therapist",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1DB954;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #1DB954;
        margin-bottom: 1rem;
    }
    .card {
        background-color: #f0f0f0;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
    }
    .emotion-card {
        background-color: #f9f9f9;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border-left: 5px solid #1DB954;
    }
    .spotify-button {
        background-color: #1DB954;
        color: white;
        padding: 10px 20px;
        border-radius: 20px;
        text-align: center;
        margin: 10px 0;
        font-weight: bold;
    }
    .stButton>button {
        background-color: #1DB954;
        color: white;
        font-weight: bold;
        border-radius: 20px;
        padding: 10px 30px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #18a449;
    }
    .welcome-footer {
        text-align: center;
        margin-top: 50px;
        font-size: 0.8rem;
        color: #888;
    }
    .exercise-card {
        background-color: #f5f5f5;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border-left: 5px solid #4CAF50;
    }
    .artist-card {
        background-color: #f5f5f5;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border-left: 5px solid #2196F3;
    }
    .login-container {
        max-width: 500px;
        margin: 0 auto;
        padding: 20px;
        background-color: #f9f9f9;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .tab-content {
        padding: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state variables
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'show_welcome' not in st.session_state:
    st.session_state.show_welcome = True
if 'emotion' not in st.session_state:
    st.session_state.emotion = None
if 'playlist' not in st.session_state:
    st.session_state.playlist = None
if 'duration' not in st.session_state:
    st.session_state.duration = 30
if 'current_track' not in st.session_state:
    st.session_state.current_track = None
if 'is_playing' not in st.session_state:
    st.session_state.is_playing = False
if 'auth_manager' not in st.session_state:
    st.session_state.auth_manager = None
if 'sp' not in st.session_state:
    st.session_state.sp = None
if 'user_activities' not in st.session_state:
    st.session_state.user_activities = {}

# User authentication functions
def hash_password(password):
    """Hash a password for storing."""
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    """Load users from JSON file."""
    if os.path.exists('users.json'):
        with open('users.json', 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    """Save users to JSON file."""
    with open('users.json', 'w') as f:
        json.dump(users, f)

def register_user(username, email, password):
    """Register a new user."""
    users = load_users()
    if username in users:
        return False, "Username already exists"
    
    # Validate email format
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return False, "Invalid email format"
    
    # Validate password strength
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    
    users[username] = {
        'email': email,
        'password': hash_password(password)
    }
    save_users(users)
    return True, "Registration successful"

def login_user(username, password):
    """Login a user."""
    users = load_users()
    if username not in users:
        return False, "Username not found"
    
    if users[username]['password'] != hash_password(password):
        return False, "Incorrect password"
    
    return True, "Login successful"

# User activity tracking functions
def load_user_activities():
    """Load user activities from JSON file."""
    activities_file = f"activities_{st.session_state.username}.json"
    if os.path.exists(activities_file):
        with open(activities_file, 'r') as f:
            return json.load(f)
    return {}

def save_user_activities(activities):
    """Save user activities to JSON file."""
    activities_file = f"activities_{st.session_state.username}.json"
    with open(activities_file, 'w') as f:
        json.dump(activities, f)

def save_user_activity(activity_description):
    """Save a new user activity."""
    if not st.session_state.logged_in:
        return
        
    activities = load_user_activities()
    current_date = time.strftime("%Y-%m-%d")
    
    if current_date not in activities:
        activities[current_date] = []
        
    activities[current_date].append({
        "time": time.strftime("%H:%M:%S"),
        "description": activity_description
    })
    
    save_user_activities(activities)

# Function to show login/signup page
def show_login_page():
    st.markdown("<h1 class='main-header'>Welcome to MoodMelody</h1>", unsafe_allow_html=True)
    
    st.markdown("<div class='login-container'>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        st.markdown("<h3>Login to Your Account</h3>", unsafe_allow_html=True)
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Login", key="login_button"):
            if username and password:
                success, message = login_user(username, password)
                if success:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
            else:
                st.warning("Please enter both username and password")
    
    with tab2:
        st.markdown("<h3>Create a New Account</h3>", unsafe_allow_html=True)
        new_username = st.text_input("Username", key="signup_username")
        email = st.text_input("Email")
        new_password = st.text_input("Password", type="password", key="signup_password")
        confirm_password = st.text_input("Confirm Password", type="password")
        
        if st.button("Sign Up", key="signup_button"):
            if new_username and email and new_password:
                if new_password != confirm_password:
                    st.error("Passwords do not match")
                else:
                    success, message = register_user(new_username, email, new_password)
                    if success:
                        st.success(message)
                        st.info("Please login with your new account")
                    else:
                        st.error(message)
            else:
                st.warning("Please fill in all fields")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Add information about the app
    st.markdown("""
    <div class="card" style="margin-top: 30px;">
        <h3 class='sub-header'>About MoodMelody</h3>
        <p>MoodMelody is an AI-powered music therapy application that recommends music based on your emotional state.
        The app uses facial emotion recognition to detect your mood and creates personalized playlists to enhance or change your emotional state.</p>
        
        <h4>Features:</h4>
        <ul>
            <li>🎭 <strong>Emotion Detection</strong> - Advanced facial analysis</li>
            <li>🎵 <strong>Personalized Playlists</strong> - Curated for your specific mood</li>
            <li>🎤 <strong>Lyrics to Song</strong> - Convert your lyrics to songs</li>
            <li>🧘 <strong>Mood-Based Exercises</strong> - Get exercise recommendations based on your mood</li>
            <li>🌟 <strong>Top Artists</strong> - Explore top artists in different genres</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# Function to show welcome page
def show_welcome_page():
    st.markdown("<h1 class='main-header'>Welcome to MoodMelody</h1>", unsafe_allow_html=True)
    
    # Create columns for layout
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown(f"""
        <div class="card">
            <h2 class='sub-header'>Hello, {st.session_state.username}!</h2>
            <p>Welcome to your AI Music Therapist. MoodMelody uses advanced AI to detect your emotions and create personalized music recommendations that can help:</p>
            <ul>
                <li>Improve your mood</li>
                <li>Reduce stress and anxiety</li>
                <li>Boost your energy levels</li>
                <li>Help you relax and focus</li>
                <li>Process and express emotions</li>
            </ul>
            <p>Our unique blend of emotion recognition technology and music therapy principles creates a personalized experience just for you.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="card">
            <h2 class='sub-header'>How It Works</h2>
            <ol>
                <li><strong>Detect Your Emotion</strong> - We analyze your facial expressions to understand your current mood</li>
                <li><strong>Generate Personalized Playlist</strong> - Based on your emotional state, we create a custom playlist</li>
                <li><strong>Enjoy & Feel Better</strong> - Listen to your personalized recommendations and feel the difference</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Display a welcoming image
        st.image("https://images.unsplash.com/photo-1514525253161-7a46d19cd819?auto=format&fit=crop&q=80&w=1000", 
                 caption="Music for your mood")
        
        st.markdown("""
        <div class="card">
            <h2 class='sub-header'>Features</h2>
            <ul>
                <li>🎭 <strong>Emotion Detection</strong> - Advanced facial analysis</li>
                <li>🎵 <strong>Personalized Playlists</strong> - Curated for your specific mood</li>
                <li>🎤 <strong>Lyrics to Song</strong> - Convert your lyrics to songs</li>
                <li>🧘 <strong>Mood-Based Exercises</strong> - Get exercise recommendations based on your mood</li>
                <li>🌟 <strong>Top Artists</strong> - Explore top artists in different genres</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Get started button
    st.markdown("<div style='text-align: center; margin-top: 30px;'>", unsafe_allow_html=True)
    if st.button("Get Started", key="lets_start_welcome", help="Click to start using MoodMelody"):
        st.session_state.show_welcome = False
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Add information about Spotify connection
    st.markdown("""
    <div class="card" style="margin-top: 20px; background-color: #f9f9f9;">
        <h3 style="color: #1DB954;">Connect with Spotify</h3>
        <p>MoodMelody uses Spotify to provide music recommendations. You'll need to connect your Spotify account to use all features.</p>
        <p style="font-size: 0.9em; color: #666;">Note: This application requires a Spotify account and proper API credentials setup.</p>
    </div>
    """, unsafe_allow_html=True)

# Function to authenticate with Spotify
def spotify_auth():
    try:
        # Use the provided Spotify credentials
        client_id = "75389525d45a4a9fa1200f00c7b4c157"
        client_secret = "5457624416194aa6af13a05c9dfe4410"
        
        auth_manager = SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri="http://127.0.0.1:8501/callback",
            scope="user-library-read user-read-playback-state user-modify-playback-state user-read-currently-playing streaming playlist-modify-private playlist-modify-public"
        )
        
        st.session_state.auth_manager = auth_manager
        st.session_state.sp = spotipy.Spotify(auth_manager=auth_manager)
        return True
    except Exception as e:
        st.error(f"Authentication error: {e}")
        return False

# Function to detect emotion from facial expression
def detect_emotion(image):
    try:
        # Convert the image to RGB (DeepFace expects RGB)
        if len(image.shape) == 2:  # If grayscale
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        elif image.shape[2] == 4:  # If RGBA
            image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
        
        # Analyze the image with DeepFace
        result = DeepFace.analyze(image, actions=['emotion'], enforce_detection=False)
        
        # Get the dominant emotion
        if isinstance(result, list):
            emotions = result[0]['emotion']
        else:
            emotions = result['emotion']
        
        dominant_emotion = max(emotions.items(), key=lambda x: x[1])[0]
        
        # Map DeepFace emotions to our simplified set
        emotion_mapping = {
            'happy': 'happy',
            'sad': 'sad',
            'angry': 'angry',
            'fear': 'anxious',
            'surprise': 'energetic',
            'disgust': 'calm',
            'neutral': 'relaxed'
        }
        
        return emotion_mapping.get(dominant_emotion, 'neutral'), emotions
    except Exception as e:
        st.error(f"Error in emotion detection: {e}")
        return "neutral", {"neutral": 100}

# Function to get music recommendations based on emotion
def get_recommendations(emotion, duration_minutes=30, include_indian=True):
    if st.session_state.sp is None:
        st.error("Spotify authentication required")
        return None
    
    # Define emotion to music genre/mood mapping
    emotion_mapping = {
        'happy': ['happy', 'cheerful', 'upbeat', 'bollywood upbeat', 'punjabi bhangra'],
        'sad': ['sad', 'melancholy', 'emotional', 'bollywood sad songs', 'ghazal'],
        'angry': ['rock', 'metal', 'intense', 'rap', 'punjabi rap'],
        'anxious': ['ambient', 'calming', 'meditation', 'indian classical', 'flute'],
        'energetic': ['dance', 'edm', 'workout', 'bollywood dance', 'tamil beats'],
        'relaxed': ['acoustic', 'chill', 'lofi', 'bollywood acoustic', 'carnatic'],
        'calm': ['piano', 'instrumental', 'soothing', 'indian instrumental', 'sitar']
    }
    
    # Get seed genres and search terms
    seed_terms = emotion_mapping.get(emotion, ['pop'])
    
    # Add Indian music focus if requested
    indian_terms = [term for term in seed_terms if 'bollywood' in term or 
                   'indian' in term or 'punjabi' in term or 
                   'carnatic' in term or 'ghazal' in term or 
                   'sitar' in term or 'tamil' in term]
    
    # Calculate number of tracks needed based on duration (assuming ~3.5 min per track)
    tracks_needed = int(duration_minutes / 3.5) + 1
    
    # Get recommendations
    tracks = []
    
    # First try with Indian terms if include_indian is True
    if include_indian and indian_terms:
        for term in indian_terms:
            needed = max(1, tracks_needed - len(tracks))
            results = st.session_state.sp.search(q=term, type='track', limit=min(20, needed))
            for item in results['tracks']['items']:
                if len(tracks) < tracks_needed:
                    tracks.append({
                        'id': item['id'],
                        'name': item['name'],
                        'artist': item['artists'][0]['name'],
                        'album': item['album']['name'],
                        'image_url': item['album']['images'][0]['url'] if item['album']['images'] else None,
                        'preview_url': item['preview_url'],
                        'duration_ms': item['duration_ms']
                    })
                else:
                    break
    
    # Then fill remaining slots with general emotion-based tracks
    for term in seed_terms:
        if len(tracks) >= tracks_needed:
            break
        results = st.session_state.sp.search(q=term, type='track', limit=min(20, tracks_needed - len(tracks)))
        for item in results['tracks']['items']:
            if len(tracks) < tracks_needed:
                # Check if track is already in the list
                if not any(track['id'] == item['id'] for track in tracks):
                    tracks.append({
                        'id': item['id'],
                        'name': item['name'],
                        'artist': item['artists'][0]['name'],
                        'album': item['album']['name'],
                        'image_url': item['album']['images'][0]['url'] if item['album']['images'] else None,
                        'preview_url': item['preview_url'],
                        'duration_ms': item['duration_ms']
                    })
            else:
                break
    
    # Shuffle the tracks for variety
    random.shuffle(tracks)
    
    return tracks

def create_spotify_playlist(tracks, emotion):
    """
    Create a Spotify playlist with the recommended tracks.
    """
    try:
        if st.session_state.sp is None:
            return False, "Spotify authentication required"
        
        # Create a new playlist
        user_id = st.session_state.sp.current_user()["id"]
        current_date = time.strftime("%Y-%m-%d")
        playlist_name = f"MoodMelody: {emotion.capitalize()} - {current_date}"
        
        playlist = st.session_state.sp.user_playlist_create(
            user_id, 
            playlist_name, 
            public=False, 
            description=f"Generated by MoodMelody based on {emotion} mood on {current_date}"
        )
        
        # Add tracks to the playlist
        track_uris = [f"spotify:track:{track['id']}" for track in tracks]
        st.session_state.sp.playlist_add_items(playlist["id"], track_uris)
        
        # Save this activity in user history
        save_user_activity(f"Created playlist '{playlist_name}' with {len(tracks)} tracks")
        
        return True, playlist["external_urls"]["spotify"]
    except Exception as e:
        return False, f"Error creating playlist: {e}"

# Function to get albums by genre
def get_albums_by_genre(genre, limit=10):
    if st.session_state.sp is None:
        st.error("Spotify authentication required")
        return []
    
    results = st.session_state.sp.search(q=f'genre:"{genre}"', type='album', limit=limit)
    
    albums = []
    for item in results['albums']['items']:
        albums.append({
            'id': item['id'],
            'name': item['name'],
            'artist': item['artists'][0]['name'],
            'image_url': item['images'][0]['url'] if item['images'] else None,
            'release_date': item['release_date']
        })
    
    return albums

# Function to display album grid
def display_album_grid(genre_name, albums):
    st.markdown(f"<h3 class='sub-header'>{genre_name} Albums</h3>", unsafe_allow_html=True)
    
    # Create columns for the grid display
    cols = st.columns(5)
    
    for i, album in enumerate(albums):
        with cols[i % 5]:
            if album['image_url']:
                st.image(album['image_url'], width=150)
            st.markdown(f"**{album['name']}**")
            st.caption(f"By {album['artist']}")
            st.caption(f"Released: {album['release_date'][:4]}")

# Function to get top artists by genre
def get_top_artists_by_genre(genre, limit=5):
    if st.session_state.sp is None:
        st.error("Spotify authentication required")
        return []
    
    results = st.session_state.sp.search(q=f'genre:"{genre}"', type='artist', limit=limit)
    
    artists = []
    for item in results['artists']['items']:
        artists.append({
            'id': item['id'],
            'name': item['name'],
            'image_url': item['images'][0]['url'] if item['images'] else None,
            'popularity': item['popularity'],
            'followers': item['followers']['total'],
            'genres': item['genres']
        })
    
    # Sort by popularity
    artists.sort(key=lambda x: x['popularity'], reverse=True)
    
    return artists[:5]  # Ensure we only return top 5

# Function to generate song from lyrics
def generate_song_from_lyrics(lyrics, singer):
    """
    Generate a song from lyrics in the style of the selected singer.
    This is a simplified implementation using text-to-speech with voice modulation.
    """
    try:
        # Create a temporary file for the audio
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        temp_file.close()
        
        # Save activity
        save_user_activity(f"Generated song in the style of {singer} from user lyrics")
        
        # Use gTTS to convert lyrics to speech
        # We'll use different language settings to simulate different singing styles
        language = 'en'
        slow_speech = False
        
        # Adjust TTS parameters based on singer to simulate different styles
        if singer in ["Adele", "Beyoncé"]:
            language = 'en-uk'  # British accent for Adele
            slow_speech = True  # Slower for more emotional delivery
        elif singer in ["Arijit Singh", "Sonu Nigam", "Shreya Ghoshal", "Lata Mangeshkar"]:
            language = 'hi'  # Hindi for Indian singers
        elif singer == "A.R. Rahman":
            language = 'ta'  # Tamil for A.R. Rahman
        
        tts = gTTS(text=lyrics, lang=language, slow=slow_speech)
        tts.save(temp_file.name)
        
        return temp_file.name
    except Exception as e:
        st.error(f"Error generating song: {e}")
        return None

# Function to get mood-based exercises
def get_mood_exercises(mood):
    """
    Return exercise recommendations based on the detected mood.
    """
    exercises = {
        'happy': [
            {
                'name': 'Dance Workout',
                'description': 'A fun dance workout to maintain your positive energy.',
                'duration': '20 minutes',
                'intensity': 'Moderate',
                'benefits': 'Enhances mood, improves cardiovascular health, and boosts energy levels.'
            },
            {
                'name': 'Social Walk',
                'description': 'Take a walk with friends or family to share your positive mood.',
                'duration': '30 minutes',
                'intensity': 'Low',
                'benefits': 'Strengthens social bonds, maintains positive mood, and provides light exercise.'
            },
            {
                'name': 'Yoga Flow',
                'description': 'A flowing yoga sequence to channel your positive energy.',
                'duration': '15 minutes',
                'intensity': 'Low to Moderate',
                'benefits': 'Improves flexibility, maintains positive energy, and enhances body awareness.'
            }
        ],
        'sad': [
            {
                'name': 'Gentle Yoga',
                'description': 'Slow, gentle yoga poses to lift your mood and energy.',
                'duration': '15 minutes',
                'intensity': 'Low',
                'benefits': 'Reduces sadness, increases energy, and improves body awareness.'
            },
            {
                'name': 'Nature Walk',
                'description': 'A peaceful walk in nature to clear your mind and lift your spirits.',
                'duration': '20 minutes',
                'intensity': 'Low',
                'benefits': 'Improves mood, provides gentle exercise, and connects you with nature.'
            },
            {
                'name': 'Deep Breathing',
                'description': 'Simple deep breathing exercises to calm your mind and reduce sadness.',
                'duration': '5 minutes',
                'intensity': 'Very Low',
                'benefits': 'Reduces stress, calms the mind, and helps process emotions.'
            }
        ],
        'angry': [
            {
                'name': 'High-Intensity Interval Training (HIIT)',
                'description': 'Short bursts of intense exercise to channel and release anger.',
                'duration': '15 minutes',
                'intensity': 'High',
                'benefits': 'Releases tension, burns energy, and reduces anger through physical exertion.'
            },
            {
                'name': 'Punching Bag Workout',
                'description': 'A boxing-inspired workout to safely release anger and frustration.',
                'duration': '10 minutes',
                'intensity': 'High',
                'benefits': 'Provides a physical outlet for anger, improves coordination, and builds strength.'
            },
            {
                'name': 'Progressive Muscle Relaxation',
                'description': 'Systematically tense and relax muscle groups to release physical tension.',
                'duration': '10 minutes',
                'intensity': 'Low',
                'benefits': 'Reduces physical tension, calms the nervous system, and decreases anger.'
            }
        ],
        'anxious': [
            {
                'name': 'Mindful Walking',
                'description': 'A slow, mindful walk focusing on each step and breath to reduce anxiety.',
                'duration': '15 minutes',
                'intensity': 'Low',
                'benefits': 'Reduces anxiety, improves mindfulness, and provides gentle exercise.'
            },
            {
                'name': '4-7-8 Breathing',
                'description': 'A breathing technique where you inhale for 4 counts, hold for 7, and exhale for 8.',
                'duration': '5 minutes',
                'intensity': 'Very Low',
                'benefits': 'Quickly reduces anxiety, activates the parasympathetic nervous system, and improves focus.'
            },
            {
                'name': 'Gentle Stretching',
                'description': 'Simple stretches to release tension in the body and calm the mind.',
                'duration': '10 minutes',
                'intensity': 'Low',
                'benefits': 'Reduces physical tension, improves flexibility, and decreases anxiety.'
            }
        ],
        'energetic': [
            {
                'name': 'Full Body Workout',
                'description': 'A comprehensive workout to channel your high energy levels.',
                'duration': '30 minutes',
                'intensity': 'High',
                'benefits': 'Utilizes excess energy, builds strength, and improves overall fitness.'
            },
            {
                'name': 'Running or Jogging',
                'description': 'A cardio session to make the most of your energetic state.',
                'duration': '20 minutes',
                'intensity': 'Moderate to High',
                'benefits': 'Improves cardiovascular health, burns energy, and enhances endurance.'
            },
            {
                'name': 'Dance Party',
                'description': 'Put on your favorite music and dance freely to express your energy.',
                'duration': '15 minutes',
                'intensity': 'Moderate',
                'benefits': 'Fun way to use energy, improves mood, and provides cardiovascular exercise.'
            }
        ],
        'relaxed': [
            {
                'name': 'Gentle Yoga Flow',
                'description': 'A flowing sequence of yoga poses to maintain your relaxed state.',
                'duration': '20 minutes',
                'intensity': 'Low to Moderate',
                'benefits': 'Maintains relaxation, improves flexibility, and enhances body awareness.'
            },
            {
                'name': 'Tai Chi',
                'description': 'Slow, flowing movements that maintain relaxation while gently exercising the body.',
                'duration': '15 minutes',
                'intensity': 'Low',
                'benefits': 'Maintains calm, improves balance, and provides gentle exercise.'
            },
            {
                'name': 'Mindful Stretching',
                'description': 'Gentle stretches with mindful awareness to maintain your relaxed state.',
                'duration': '10 minutes',
                'intensity': 'Low',
                'benefits': 'Enhances relaxation, improves flexibility, and increases body awareness.'
            }
        ],
        'calm': [
            {
                'name': 'Walking Meditation',
                'description': 'A meditative walk to maintain your calm and centered state.',
                'duration': '15 minutes',
                'intensity': 'Low',
                'benefits': 'Maintains calm, improves mindfulness, and provides light exercise.'
            },
            {
                'name': 'Gentle Swimming',
                'description': 'Slow, relaxed swimming to complement your calm state.',
                'duration': '20 minutes',
                'intensity': 'Low to Moderate',
                'benefits': 'Maintains relaxation, provides full-body exercise, and improves cardiovascular health.'
            },
            {
                'name': 'Body Scan Meditation',
                'description': 'A lying meditation where you systematically scan your body for sensations.',
                'duration': '10 minutes',
                'intensity': 'Very Low',
                'benefits': 'Deepens calm, increases body awareness, and improves mindfulness.'
            }
        ]
    }
    
    return exercises.get(mood, exercises['relaxed'])

# Main application logic
if not st.session_state.logged_in:
    show_login_page()
else:
    if st.session_state.show_welcome:
        show_welcome_page()
    else:
        st.markdown("<h1 class='main-header'>MoodMelody: AI Music Therapist</h1>", unsafe_allow_html=True)

        # Sidebar for authentication and controls
        with st.sidebar:
            st.markdown("<h3>Welcome to MoodMelody</h3>", unsafe_allow_html=True)


        # Sidebar for authentication and controls
        with st.sidebar:
            st.markdown("<h2 class='sub-header'>Controls</h2>", unsafe_allow_html=True)
            
            # Logout button
            if st.button("Logout"):
                st.session_state.logged_in = False
                st.session_state.username = None
                st.rerun()
            
            # Spotify Authentication
            if st.session_state.sp is None:
                st.info("Please authenticate with Spotify to use all features")
                if st.button("Connect to Spotify"):
                    with st.spinner("Connecting to Spotify..."):
                        if spotify_auth():
                            st.success("Connected to Spotify!")
                            st.rerun()
            else:
                st.success("Connected to Spotify ✓")
            
            # Duration selector
            st.markdown("### Select Playlist Duration")
            duration = st.slider("Minutes", min_value=10, max_value=120, value=st.session_state.duration, step=5)
            if duration != st.session_state.duration:
                st.session_state.duration = duration
            
            # Indian music preference
            include_indian = st.checkbox("Focus on Indian Music", value=True)
            
            # Manual emotion selection
            st.markdown("### Select Emotion Manually")
            emotions = ['happy', 'sad', 'angry', 'anxious', 'energetic', 'relaxed', 'calm']
            selected_emotion = st.selectbox("Choose emotion", emotions)
            
            if st.button("Generate Playlist from Selection"):
                with st.spinner("Generating your personalized playlist..."):
                    st.session_state.emotion = selected_emotion
                    st.session_state.playlist = get_recommendations(
                        selected_emotion, 
                        duration_minutes=st.session_state.duration,
                        include_indian=include_indian
                    )
                    save_user_activity(f"Generated {st.session_state.duration}-minute playlist for {selected_emotion} mood")
                    st.rerun()

        # Main content area
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "Emotion Detection", 
            "Your Playlist", 
            "Lyrics to Song", 
            "Mood Exercises", 
            "Top Artists",
            "Activity History"
        ])
        
        # Tab 1: Emotion Detection
        with tab1:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<h2 class='sub-header'>Detect Your Emotion</h2>", unsafe_allow_html=True)
            st.write("Let's analyze your current mood through facial expression to recommend the perfect music.")
            
            col1, col2 = st.columns([2, 3])
            
            with col1:
                option = st.radio("Choose input method:", ["Webcam", "Upload Image"])
                
                if option == "Webcam":
                    if st.button("Capture from Webcam"):
                        with st.spinner("Starting camera..."):
                            try:
                                # Initialize webcam
                                cap = cv2.VideoCapture(0)
                                if not cap.isOpened():
                                    st.error("Could not open webcam. Please check your camera connection.")
                                else:
                                    # Countdown
                                    for i in range(3, 0, -1):
                                        st.write(f"Capturing in {i}...")
                                        time.sleep(1)
                                    
                                    # Capture frame
                                    ret, frame = cap.read()
                                    if ret:
                                        # Convert BGR to RGB
                                        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                                        
                                        # Display the captured image
                                        st.image(rgb_frame, caption="Captured Image", width=300)
                                        
                                        # Detect emotion
                                        emotion, emotion_scores = detect_emotion(rgb_frame)
                                        st.session_state.emotion = emotion
                                        save_user_activity(f"Detected emotion: {emotion}")
                                        
                                        # Generate playlist based on emotion
                                        if st.session_state.sp is not None:
                                            with st.spinner("Generating your personalized playlist..."):
                                                st.session_state.playlist = get_recommendations(
                                                    emotion, 
                                                    duration_minutes=st.session_state.duration,
                                                    include_indian=include_indian
                                                )
                                                save_user_activity(f"Generated {st.session_state.duration}-minute playlist for {emotion} mood")
                                    else:
                                        st.error("Failed to capture image from webcam")
                                
                                # Release webcam
                                cap.release()
                            except Exception as e:
                                st.error(f"Error accessing webcam: {e}")
                
                elif option == "Upload Image":
                    uploaded_file = st.file_uploader("Upload a photo of yourself", type=["jpg", "jpeg", "png"])
                    if uploaded_file is not None:
                        # Read the image
                        image = Image.open(uploaded_file)
                        st.image(image, caption="Uploaded Image", width=300)
                        
                        # Convert to numpy array for processing
                        image_array = np.array(image)
                        
                        # Detect emotion
                        emotion, emotion_scores = detect_emotion(image_array)
                        st.session_state.emotion = emotion
                        save_user_activity(f"Detected emotion: {emotion}")
                        
                        # Generate playlist based on emotion
                        if st.session_state.sp is not None:
                            with st.spinner("Generating your personalized playlist..."):
                                st.session_state.playlist = get_recommendations(
                                    emotion, 
                                    duration_minutes=st.session_state.duration,
                                    include_indian=include_indian
                                )
                                save_user_activity(f"Generated {st.session_state.duration}-minute playlist for {emotion} mood")
            
            with col2:
                if st.session_state.emotion:
                    st.markdown("<div class='emotion-card'>", unsafe_allow_html=True)
                    st.markdown(f"### Detected Emotion: {st.session_state.emotion.capitalize()}")
                    
                    # Display emotion description and music recommendation explanation
                    emotion_descriptions = {
                        'happy': "You seem happy and cheerful! Upbeat and energetic music can complement your positive mood.",
                        'sad': "You appear to be feeling down. Soothing melodies might help process emotions or uplifting tunes could help shift your mood.",
                        'angry': "You seem frustrated or angry. Calming music might help soothe your nerves, or you might prefer intense tracks to match your energy.",
                        'anxious': "You look a bit anxious. Gentle, slow-tempo music can help reduce stress and anxiety.",
                        'energetic': "You're looking energetic and excited! Fast-paced, rhythmic music can match your high energy.",
                        'relaxed': "You appear relaxed and content. Ambient or acoustic tracks can maintain this peaceful state.",
                        'calm': "You seem calm and collected. Instrumental or classical music can complement this balanced state."
                    }
                    
                    st.write(emotion_descriptions.get(st.session_state.emotion, ""))
                    
                    if st.session_state.playlist:
                        st.write(f"Based on your {st.session_state.emotion} mood, we've created a personalized playlist for you!")
                        st.markdown("<a href='#your-playlist' class='spotify-button'>View Your Playlist</a>", unsafe_allow_html=True)
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.info("Capture or upload an image to detect your emotion and get personalized music recommendations.")
            
            st.markdown("</div>", unsafe_allow_html=True)

        # Tab 2: Playlist
        with tab2:
            st.markdown("<div class='card' id='your-playlist'>", unsafe_allow_html=True)
            st.markdown("<h2 class='sub-header'>Your Personalized Playlist</h2>", unsafe_allow_html=True)
            
            if st.session_state.playlist:
                st.write(f"Here's your {st.session_state.duration}-minute playlist based on your {st.session_state.emotion} mood:")
                
                # Calculate total duration
                total_duration_ms = sum(track['duration_ms'] for track in st.session_state.playlist)
                total_duration_min = total_duration_ms / (1000 * 60)
                
                st.write(f"Total duration: {total_duration_min:.1f} minutes ({len(st.session_state.playlist)} tracks)")
                
                # Display tracks
                for i, track in enumerate(st.session_state.playlist):
                    col1, col2, col3 = st.columns([1, 3, 1])
                    
                    with col1:
                        if track['image_url']:
                            st.image(track['image_url'], width=100)
                    
                    with col2:
                        st.markdown(f"**{i+1}. {track['name']}**")
                        st.write(f"Artist: {track['artist']}")
                        st.write(f"Album: {track['album']}")
                        st.write(f"Duration: {track['duration_ms']/1000/60:.1f} minutes")
                    
                    with col3:
                        if track['preview_url']:
                            st.audio(track['preview_url'])
                        else:
                            st.write("Preview not available")
                
                # Option to save playlist (placeholder - would require additional Spotify permissions)
                if st.button("Save this playlist to Spotify"):
                    with st.spinner("Saving playlist to your Spotify account..."):
                        success, result = create_spotify_playlist(st.session_state.playlist, st.session_state.emotion)
                        if success:
                            st.success("Playlist saved to your Spotify account!")
                            st.markdown(f"[Open in Spotify]({result})", unsafe_allow_html=True)
                        else:
                            st.error(result)
            else:
                if st.session_state.emotion:
                    st.info("Generating your playlist... If it doesn't appear, try clicking 'Generate Playlist from Selection' in the sidebar.")
                else:
                    st.info("Detect your emotion or select one manually to generate a personalized playlist.")
            
            st.markdown("</div>", unsafe_allow_html=True)

        # Tab 3: Lyrics to Song
        with tab3:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<h2 class='sub-header'>Convert Lyrics to Song</h2>", unsafe_allow_html=True)
            st.write("Enter your lyrics and select a singer to create a song in their style.")
            
            # Lyrics input
            lyrics = st.text_area("Enter your lyrics", height=200, 
                                placeholder="Write your lyrics here...\nFor example:\nI'm walking down this road\nThinking of you and our memories\nThe sun is setting low\nAnd I'm feeling so free")
            
            # Singer selection
            singers = ["Adele", "Ed Sheeran", "Taylor Swift", "Arijit Singh", "A.R. Rahman", 
                      "Lata Mangeshkar", "Sonu Nigam", "Shreya Ghoshal", "Justin Bieber", "Beyoncé"]
            selected_singer = st.selectbox("Select singer style", singers)
            
            # Generate button
            if st.button("Generate Song") and lyrics:
                with st.spinner(f"Creating song in the style of {selected_singer}..."):
                    # Generate song
                    song_file = generate_song_from_lyrics(lyrics, selected_singer)
                    
                    if song_file:
                        st.success(f"Song created in the style of {selected_singer}!")
                        
                        # Display audio player
                        st.audio(song_file)
                        
                        # Download button
                        with open(song_file, "rb") as file:
                            btn = st.download_button(
                                label="Download Song",
                                data=file,
                                file_name=f"song_{selected_singer.lower().replace(' ', '_')}.mp3",
                                mime="audio/mp3"
                            )
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Additional information
            st.markdown("""
            <div class="card" style="margin-top: 20px;">
                <h3>About Lyrics to Song Feature</h3>
                <p>This feature uses text-to-speech technology to convert your lyrics into a song. In a full implementation, 
                this would use more sophisticated AI models to generate music that matches the style of the selected singer.</p>
                
                <p>Tips for better results:</p>
                <ul>
                    <li>Write lyrics with clear structure (verses, chorus)</li>
                    <li>Keep lines at a reasonable length</li>
                    <li>Consider the rhythm and flow of your words</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

        # Tab 4: Mood Exercises
        with tab4:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<h2 class='sub-header'>Mood-Based Exercises</h2>", unsafe_allow_html=True)
            
            if st.session_state.emotion:
                st.write(f"Based on your {st.session_state.emotion} mood, here are some recommended exercises:")
                
                exercises = get_mood_exercises(st.session_state.emotion)
                
                for exercise in exercises:
                    st.markdown(f"""
                    <div class='exercise-card'>
                        <h3>{exercise['name']}</h3>
                        <p><strong>Description:</strong> {exercise['description']}</p>
                        <p><strong>Duration:</strong> {exercise['duration']}</p>
                        <p><strong>Intensity:</strong> {exercise['intensity']}</p>
                        <p><strong>Benefits:</strong> {exercise['benefits']}</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Detect your emotion first to get personalized exercise recommendations.")
                
                # Allow manual selection for exercises
                st.markdown("### Or select a mood manually")
                moods = ['happy', 'sad', 'angry', 'anxious', 'energetic', 'relaxed', 'calm']
                selected_mood = st.selectbox("Choose mood for exercise recommendations", moods, key="exercise_mood")
                
                if st.button("Show Exercises"):
                    exercises = get_mood_exercises(selected_mood)
                    
                    for exercise in exercises:
                        st.markdown(f"""
                        <div class='exercise-card'>
                            <h3>{exercise['name']}</h3>
                            <p><strong>Description:</strong> {exercise['description']}</p>
                            <p><strong>Duration:</strong> {exercise['duration']}</p>
                            <p><strong>Intensity:</strong> {exercise['intensity']}</p>
                            <p><strong>Benefits:</strong> {exercise['benefits']}</p>
                        </div>
                        """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Additional information about exercise benefits
            st.markdown("""
            <div class="card" style="margin-top: 20px;">
                <h3>Benefits of Exercise for Emotional Wellbeing</h3>
                <p>Exercise has been shown to have significant benefits for mental and emotional health:</p>
                <ul>
                    <li><strong>Reduces stress and anxiety</strong> by lowering stress hormones and stimulating endorphin production</li>
                    <li><strong>Improves mood</strong> through the release of feel-good neurotransmitters</li>
                    <li><strong>Enhances sleep quality</strong>, which is essential for emotional regulation</li>
                    <li><strong>Boosts self-confidence</strong> and provides a sense of accomplishment</li>
                    <li><strong>Offers a healthy outlet</strong> for processing difficult emotions</li>
                </ul>
                <p>Even short periods of exercise can have immediate positive effects on your mood and emotional state.</p>
            </div>
            """, unsafe_allow_html=True)

        # Tab 5: Top Artists
        with tab5:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<h2 class='sub-header'>Explore Top Artists by Genre</h2>", unsafe_allow_html=True)
            
            # Genre selection
            genres = [
                "Pop", "Rock", "Hip Hop", "R&B", "Electronic", 
                "Jazz", "Classical", "Country", "Bollywood", 
                "Indian Classical", "Punjabi", "Tamil", "Telugu"
            ]
            
            selected_genre = st.selectbox("Select a genre", genres)
            
            if st.button("Show Top Artists") or 'top_artists' in st.session_state:
                if st.session_state.sp is not None:
                    with st.spinner(f"Finding top artists in {selected_genre}..."):
                        top_artists = get_top_artists_by_genre(selected_genre)
                        st.session_state.top_artists = top_artists
                        
                        if top_artists:
                            st.markdown(f"### Top 5 Artists in {selected_genre}")
                            
                            for i, artist in enumerate(top_artists):
                                st.markdown(f"""
                                <div class='artist-card'>
                                    <h3>{i+1}. {artist['name']}</h3>
                                    <p><strong>Popularity:</strong> {artist['popularity']}/100</p>
                                    <p><strong>Followers:</strong> {artist['followers']:,}</p>
                                    <p><strong>Genres:</strong> {', '.join(artist['genres'][:5]) if artist['genres'] else 'Not specified'}</p>
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.info(f"No artists found for {selected_genre}. Try another genre.")
                else:
                    st.error("Please connect to Spotify first to use this feature.")
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Additional information about music genres
            st.markdown("""
            <div class="card" style="margin-top: 20px;">
                <h3>About Music Genres</h3>
                <p>Music genres represent different styles and traditions in music. Each genre has its own characteristics, 
                history, and cultural significance. Exploring different genres can help you discover new music and expand your musical taste.</p>
                
                <p>Popular genres around the world:</p>
                <ul>
                    <li><strong>Pop</strong> - Catchy, commercial music with broad appeal</li>
                    <li><strong>Rock</strong> - Guitar-driven music with various subgenres</li>
                    <li><strong>Hip Hop</strong> - Rhythmic music with rapping and beats</li>
                    <li><strong>Electronic</strong> - Computer-generated music with various subgenres</li>
                </ul>
                
                <p>Popular Indian genres:</p>
                <ul>
                    <li><strong>Bollywood</strong> - Music from Indian cinema</li>
                    <li><strong>Indian Classical</strong> - Traditional music with rich history</li>
                    <li><strong>Punjabi</strong> - Energetic music from Punjab region</li>
                    <li><strong>Tamil & Telugu</strong> - Music from South Indian cinema and culture</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

        # Tab 6: Activity History
        with tab6:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<h2 class='sub-header'>Your Activity History</h2>", unsafe_allow_html=True)
            st.write("Here's a record of your previous activities in MoodMelody:")
            
            activities = load_user_activities()
            
            if not activities:
                st.info("No activities recorded yet. Start using MoodMelody to build your history!")
            else:
                # Sort dates in reverse chronological order
                sorted_dates = sorted(activities.keys(), reverse=True)
                
                for date in sorted_dates:
                    with st.expander(f"Activities on {date}"):
                        for activity in activities[date]:
                            st.markdown(f"**{activity['time']}** - {activity['description']}")
        
        st.markdown("</div>", unsafe_allow_html=True)

        # Footer
        st.markdown("---")
        st.markdown("### About MoodMelody")
        st.write("""
        MoodMelody is an AI-powered music therapy application that recommends music based on your emotional state.
        The app uses facial emotion recognition to detect your mood and creates personalized playlists to enhance or change your emotional state.
        """)

        st.markdown("### How It Works")
        st.write("""
        1. **Emotion Detection**: We analyze your facial expressions to determine your current emotional state.
        2. **Music Recommendation**: Based on your emotion, we recommend music that can either complement or help shift your mood.
        3. **Playlist Generation**: We create a personalized playlist with the duration you specify.
        4. **Lyrics to Song**: Convert your lyrics into songs in the style of your favorite artists.
        5. **Mood Exercises**: Get exercise recommendations based on your emotional state.
        6. **Top Artists**: Explore the top artists in different music genres.
        """)

        st.markdown("### Music Therapy Benefits")
        st.write("""
        - **Stress Reduction**: Calming music can lower stress hormones and reduce anxiety.
        - **Mood Enhancement**: Upbeat music can boost your mood and energy levels.
        - **Emotional Processing**: Music can help you process and express difficult emotions.
        - **Focus Improvement**: Certain types of music can enhance concentration and productivity.
        - **Sleep Quality**: Gentle, slow-tempo music can improve sleep quality.
        """)

# Create a .streamlit directory and secrets.toml file if they don't exist
if not os.path.exists('.streamlit'):
    os.makedirs('.streamlit')

# Write Spotify credentials to secrets.toml
with open('.streamlit/secrets.toml', 'w') as f:
    f.write(f'SPOTIFY_CLIENT_ID = "75389525d45a4a9fa1200f00c7b4c157"\n')
    f.write(f'SPOTIFY_CLIENT_SECRET = "5457624416194aa6af13a05c9dfe4410"\n')
