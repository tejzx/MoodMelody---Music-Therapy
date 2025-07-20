# 🎵 MoodMelody: Your AI-Powered Music Therapist
*Transforming emotions into musical journeys.*
---
## 🌟 Project Overview

**MoodMelody** is an intelligent, emotion-aware music therapy application that bridges the gap between mental well-being and sound. By analyzing facial expressions through AI-driven emotion recognition, it delivers curated music experiences that uplift, calm, energize, or soothe—whatever your soul needs.

Whether you're looking to boost your mood, relax your mind, or explore songs that resonate with how you feel, MoodMelody is your perfect companion.

---

## 🎧 Key Features

* 🔐 **User Authentication**: Sign up and log in securely
* 😊 **Emotion Detection**: Real-time facial emotion analysis using AI
* 🎶 **Mood-Based Music Recommendations**: Curated playlists tailored to your current mood
* 🧠 **Lyrics to Song Generator**: Convert your own lyrics into songs styled like your favorite artists
* 🏃‍♀️ **Mood-Based Exercise Tips**: Get exercise suggestions aligned with your emotional state
* 🌍 **Explore Top Artists**: Discover top 5 trending artists across genres
* 🎵 **Album Showcase**: Dive into music albums with a focus on diverse Indian genres
* ⏱️ **Set Your Vibe Duration**: Choose how long your playlist should run
* 📃 **Dynamic Playlist Creation**: Generate personalized playlists on-the-go
* ▶️ **Integrated Music Playback**: Listen to music directly within the app

---

## ⚙️ Tech Stack & Tools

| Component                | Technology Used                  |
| ------------------------ | -------------------------------- |
| 👥 User Management       | JSON-based custom authentication |
| 🤖 Emotion Detection     | OpenCV + DeepFace                |
| 🎵 Music Integration     | Spotify API                      |
| 🌐 Web Interface         | Streamlit                        |
| 🎯 Recommendation Engine | Emotion-to-genre mapping         |
| 🎤 Lyrics-to-Song        | gTTS (Google Text-to-Speech)     |

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/moodmelody.git
cd moodmelody
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Spotify API

* Create an account at [Spotify for Developers](https://developer.spotify.com)
* Create an application and add the following Redirect URI:
  `http://127.0.0.1:8501/callback`
* Use the provided credentials in your code or `secrets.toml` file

### 4. Launch the App

```bash
streamlit run app.py
```

---

## 🔍 How It Works

1. **Log In** to your account
2. **Connect to Spotify** for music playback
3. **Capture Emotion** via webcam using facial recognition
4. **Receive Song Recommendations** that align with your mood
5. **Generate Playlist** tailored to mood, duration, and preference
6. **Play Music** directly within the interface
7. **Explore** exercises, top artists, and convert lyrics to songs

---

## 🎼 Emotion-to-Music Mapping

| Emotion      | Music Style                                               |
| ------------ | --------------------------------------------------------- |
| 😊 Happy     | Bollywood upbeat, Punjabi bhangra, cheerful pop           |
| 😢 Sad       | Bollywood ballads, soulful ghazals, emotional melodies    |
| 😡 Angry     | Rock, metal, intense rap, Punjabi rap                     |
| 😰 Anxious   | Ambient, calming meditation, Indian classical, flute      |
| 💪 Energetic | EDM, Bollywood dance tracks, Tamil beats, workout anthems |
| 😌 Relaxed   | Acoustic, lofi, Carnatic, unplugged Bollywood             |
| 🧘 Calm      | Piano, instrumental, sitar-based Indian melodies          |

---

## 🗂️ Project Structure

```
📁 moodmelody/
├── app.py                      # Main Streamlit application
├── requirements.txt           # Python dependencies
├── users.json                 # Auto-generated user database
├── .streamlit/
│   └── secrets.toml           # Spotify credentials (auto-created)
```

---
## 🌱 Future Enhancements

* 🎤 Voice command integration
* 📱 Mobile-friendly app version
* 🎼 Smarter AI for song synthesis from lyrics
* 🔁 Adaptive learning via user feedback
* 🎵 Integration with Apple Music, YouTube, JioSaavn, etc.
---
## 🙌 Built With

* **Streamlit** – Frontend web app
* **Spotify API** – Real-time music data
* **OpenCV + DeepFace** – Facial emotion recognition
* **gTTS** – Text-to-speech song synthesis
* **Python** – Core backend scripting
---
> *"Music speaks what cannot be expressed, soothes the mind and gives it rest."*
---
## Feel free to contact
reachteju10@gmail.com
