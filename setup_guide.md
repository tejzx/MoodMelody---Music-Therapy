# VS Code Setup Guide for MoodMelody

## Step 1: Install VS Code Extensions

1. Open VS Code
2. Go to Extensions (Ctrl+Shift+X or Cmd+Shift+X on Mac)
3. Search for and install the following extensions:
   - Python (Microsoft)
   - Pylance
   - Jupyter
   - Streamlit Snippets (optional, but helpful)

## Step 2: Set Up the Project

1. Create a new folder for your project
2. Download all the files from this conversation and place them in the folder
3. Open the folder in VS Code (File > Open Folder)

## Step 3: Create a Virtual Environment

Open a terminal in VS Code (Ctrl+` or Terminal > New Terminal) and run:

\`\`\`bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
\`\`\`

## Step 4: Install Required Packages

With the virtual environment activated, install the required packages:

\`\`\`bash
pip install -r requirements.txt
\`\`\`

This will install all the necessary dependencies including:
- streamlit
- spotipy
- opencv-python
- deepface
- tensorflow
- numpy
- pandas
- matplotlib
- pillow
- requests
- gtts

## Step 5: Run the Application

With everything set up, you can now run the application:

\`\`\`bash
streamlit run app.py
\`\`\`

The application should open in your default web browser at http://127.0.0.1:8501

## Troubleshooting Common Issues

### TensorFlow/DeepFace Compatibility Issues

If you encounter errors related to TensorFlow or DeepFace:

1. Make sure you're using the correct versions as specified in requirements.txt
2. The code already includes a fix for the "LocallyConnected2D" error by setting the TF_ENABLE_ONEDNN_OPTS environment variable to "0"

### Webcam Access Issues

If the webcam doesn't work:

1. Make sure your webcam is connected and working
2. Check that you've granted browser permissions for camera access
3. Try using the "Upload Image" option instead

### Spotify Authentication Issues

If Spotify authentication fails:

1. The app is already configured with the provided credentials
2. Make sure your internet connection is working
3. If needed, you can create your own Spotify Developer account and update the credentials in the code

## Additional Resources

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Spotify Web API Documentation](https://developer.spotify.com/documentation/web-api/)
- [DeepFace Documentation](https://github.com/serengil/deepface)
- [OpenCV Documentation](https://docs.opencv.org/)
\`\`\`

## Step-by-Step Guide to Use the Enhanced MoodMelody Project

I've fixed the errors in your project and implemented all the requested features. Here's how to use the enhanced application:

### Setting Up the Project

1. **Download the Code:**
   - Save all the files provided above to your project folder
   - Make sure to include app.py, requirements.txt, and README.md

2. **Install Dependencies:**
   - Open a terminal in VS Code
   - Create and activate a virtual environment (recommended)
   \`\`\`bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   \`\`\`
   - Install the required packages
   \`\`\`bash
   pip install -r requirements.txt
   \`\`\`

3. **Run the Application:**
   \`\`\`bash
   streamlit run app.py
   \`\`\`
   - The application will open in your browser at http://127.0.0.1:8501

### Key Fixes and Enhancements

1. **Fixed TensorFlow Compatibility Issue:**
   - Added `os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"` to fix the LocallyConnected2D import error
   - Updated the TensorFlow version in requirements.txt

2. **Added Sign-up and Login Page:**
   - Users can now create accounts and log in
   - User data is stored in a JSON file

3. **Added Lyrics-to-Song Feature:**
   - New tab where users can input lyrics and select a singer
   - Uses gTTS to convert lyrics to speech in the style of the selected singer
   - Users can download the generated song

4. **Added Mood-Based Exercises:**
   - New tab that recommends exercises based on the detected mood
   - Each exercise includes description, duration, intensity, and benefits

5. **Added Top Artists Exploration:**
   - New tab to explore the top 5 artists in different genres
   - Shows artist details including popularity, followers, and genres

### Using the Application

1. **Sign up or log in** with your username and password
2. **Connect to Spotify** using the sidebar button
3. **Detect your emotion** using webcam or uploaded image
4. **Generate a playlist** based on your mood
5. **Create songs from your lyrics** in the Lyrics to Song tab
6. **Get exercise recommendations** based on your mood in the Mood Exercises tab
7. **Explore top artists** in different genres in the Top Artists tab

The application now includes all the features you requested and should run without the errors you were experiencing.

