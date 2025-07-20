# MoodMelody: AI-Based Music Therapist

## Project Overview

MoodMelody is an AI-powered music therapy application that recommends music based on emotional states. The application uses facial emotion recognition to detect the user's current mood and creates personalized playlists to enhance or change their emotional state.

## Features

- **User Authentication**: Sign up and login functionality
- **Emotion Detection**: Analyzes facial expressions to determine the user's current emotional state
- **Music Recommendation**: Recommends music based on detected emotions
- **Lyrics to Song**: Convert your lyrics to songs in the style of selected singers
- **Mood-Based Exercises**: Get exercise recommendations based on your emotional state
- **Top Artists Exploration**: Explore top 5 artists in different genres
- **Album Display**: Shows albums by genre with a focus on Indian music
- **Duration Selection**: Allows users to select the duration for music playback
- **Playlist Generation**: Creates personalized playlists based on emotion and preferences
- **Music Playback**: Plays music directly in the application

## Technical Components

1. **User Authentication**: Simple JSON-based user management system
2. **Facial Emotion Recognition**: Uses OpenCV and DeepFace to detect emotions from facial expressions
3. **Spotify API Integration**: Connects to Spotify for music data and playback
4. **Streamlit Web Interface**: Provides an interactive user interface
5. **Recommendation Engine**: Matches emotions to appropriate music genres and tracks
6. **Text-to-Speech**: Converts lyrics to songs using gTTS

## Setup Instructions

1. Clone this repository
2. Install the required packages:
   \`\`\`
   pip install -r requirements.txt
   \`\`\`
3. Set up your Spotify Developer credentials:
   - Create a Spotify Developer account at [developer.spotify.com](https://developer.spotify.com)
   - Create a new application
   - Add `http://127.0.0.1:8501/callback` to the Redirect URIs
   - Note your Client ID and Client Secret
   - The app already includes the provided credentials in the code

4. Run the application:
   \`\`\`
   streamlit run app.py
   \`\`\`

## How It Works

1. Sign up or log in to your account
2. Connect your Spotify account
3. The system analyzes your facial expression to detect your emotion
4. Based on the detected emotion, the system recommends appropriate music
5. You can select the duration and preferences for the playlist
6. The system generates a personalized playlist
7. You can play the music directly in the application
8. You can also convert lyrics to songs, get exercise recommendations, and explore top artists

## Emotion to Music Mapping

- **Happy**: Upbeat, cheerful music, Bollywood upbeat, Punjabi bhangra
- **Sad**: Melancholy, emotional tracks, Bollywood sad songs, ghazals
- **Angry**: Rock, metal, intense music, rap, Punjabi rap
- **Anxious**: Ambient, calming music, meditation tracks, Indian classical, flute
- **Energetic**: Dance, EDM, workout music, Bollywood dance, Tamil beats
- **Relaxed**: Acoustic, chill, lofi, Bollywood acoustic, Carnatic
- **Calm**: Piano, instrumental, soothing music, Indian instrumental, sitar

## Project Structure

- `app.py`: Main Streamlit application
- `requirements.txt`: List of required Python packages
- `.streamlit/secrets.toml`: Configuration file for Spotify API credentials (created automatically)
- `users.json`: User database (created automatically when users register)

## Future Enhancements

- Integration with more music streaming platforms
- More sophisticated emotion detection algorithms
- Personalized learning based on user feedback
- Support for voice commands
- Mobile application version
- Advanced AI for lyrics-to-song conversion

## Credits

This project uses the following technologies:
- Streamlit for the web interface
- Spotify API for music data and playback
- OpenCV and DeepFace for facial emotion recognition
- gTTS for text-to-speech conversion
- Python for backend processing
\`\`\`
