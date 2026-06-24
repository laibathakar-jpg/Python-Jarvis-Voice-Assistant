# main.py
import speech_recognition as sr
import pyttsx3
import webbrowser
import os
import random
import sounddevice as sd
import numpy as np
from urllib.parse import quote

# Initialize text-to-speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)  # Set speech rate
engine.setProperty('volume', 1.0)  # Set volume to max

# Ensure voices are available
voices = engine.getProperty('voices')
if voices:
    engine.setProperty('voice', voices[0].id)
    print("TTS voice set successfully.")
else:
    print("Warning: No TTS voices found. Install voices in Windows Settings > Time & Language > Speech.")

# Global state for search mode
search_mode = None  # Can be None, 'google', 'youtube'

def speak(text):
    """Speak the given text using pyttsx3"""
    try:
        engine.say(text)
        engine.runAndWait()
    except KeyboardInterrupt:
        raise  # Re-raise KeyboardInterrupt to allow user to quit
    except Exception as e:
        print(f"TTS error: {e}. Falling back to print.")
        print(text)

def listen_command():
    """Listen to user voice and return as text, with text input fallback"""
    # Try using sounddevice for audio input
    try:
        print("Listening...")
        sample_rate = 16000  # 16kHz
        duration = 5  # seconds max
        
        # Record audio using sounddevice
        audio_data = sd.rec(int(sample_rate * duration), samplerate=sample_rate, channels=1, dtype='float32')
        sd.wait()  # Wait for recording to finish
        
        # Convert to int16 format that speech_recognition expects
        audio_int16 = np.int16(audio_data * 32767)
        
        # Create AudioData object for speech_recognition
        recognizer = sr.Recognizer()
        audio = sr.AudioData(audio_int16.tobytes(), sample_rate, 2)
        
        try:
            command = recognizer.recognize_google(audio)
            print(f"User said: {command}")
            return command.lower()
        except sr.UnknownValueError:
            print("Sorry, I could not understand audio.")
            speak("Sorry, I could not understand audio.")
            return ""
        except sr.RequestError as e:
            print(f"Could not request results: {e}")
            speak("Could not request results from Google Speech Recognition service.")
            return ""
    
    except Exception as e:
        print(f"Audio recording error: {e}")
        print("Using text input instead.")
        try:
            command = input("Please type a command instead: ")
            return command.lower() if command else ""
        except KeyboardInterrupt:
            raise

def play_music(folder_path="music"):
    """Play a random song from the specified folder"""
    if not os.path.exists(folder_path):
        speak("Music folder not found!")
        return
    songs = [file for file in os.listdir(folder_path) if file.endswith((".mp3", ".wav"))]
    if songs:
        song = random.choice(songs)
        song_path = os.path.join(folder_path, song)
        speak(f"Playing {song}")
        print(f"Playing: {song_path}")
        os.startfile(song_path)  # Works on Windows
    else:
        speak("No songs found in the folder.")

def process_command(command):
    """Process recognized command"""
    global search_mode
    
    # Check for search mode exit commands first
    if "stop search" in command or "close search" in command:
        speak("Stopping search mode")
        search_mode = None
        return
    
    # If in search mode, search for the command
    if search_mode == 'google':
        speak(f"Searching for {command}")
        search_url = f"https://www.google.com/search?q={quote(command)}"
        webbrowser.open(search_url)
        return
    
    if search_mode == 'youtube':
        speak(f"Searching YouTube for {command}")
        search_url = f"https://www.youtube.com/results?search_query={quote(command)}"
        webbrowser.open(search_url)
        return
    
    # Normal command processing
    if "open chrome" in command or "open google" in command:
        speak("Opening Chrome in search mode. Say anything to search.")
        webbrowser.open("https://www.google.com")
        search_mode = 'google'
    elif "open youtube" in command:
        speak("Opening YouTube in search mode. Say anything to search on YouTube.")
        webbrowser.open("https://www.youtube.com")
        search_mode = 'youtube'
    elif "play music" in command:
        play_music()  # default folder: ./music
    elif "hello" in command:
        speak("Hello! How are you?")
    elif "quit" in command or "exit" in command:
        speak("Goodbye!")
        exit()
    else:
        speak("Command not recognized. Say 'open chrome' to search on Google, or 'open youtube' to search on YouTube.")

def main():
    try:
        speak("Hello! I am your assistant. Say something.")
    except KeyboardInterrupt:
        return
    
    while True:
        try:
            command = listen_command()
            if command:
                process_command(command)
        except KeyboardInterrupt:
            print("\nAssistant shutting down...")
            try:
                speak("Goodbye!")
            except KeyboardInterrupt:
                pass
            break

if __name__ == "__main__":
    main()