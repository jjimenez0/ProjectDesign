import random
import requests
import cv2
from picamera2 import Picamera2
from tkinter import Tk, Label, Button, Canvas, PhotoImage
from io import BytesIO
from PIL import Image, ImageTk
import pyttsx3

# Global variables
score = 0
word_count = 0
max_words = 10
random_word = None

# Initialize Picamera2
picam = Picamera2()
picam.configure(picam.create_still_configuration())

# Initialize TTS engine
tts_engine = pyttsx3.init()

# Function to play audio using pyttsx3 and display the word image
def play_audio_and_display_image(word):
    tts_engine.say(word)
    tts_engine.runAndWait()

    # Load and display the associated image
    image_file = f"/home/t49/Downloads/word_images/{word}.png"
    if os.path.exists(image_file):
        word_image = PhotoImage(file=image_file)
        canvas.delete("all")
        canvas.create_image(300, 150, image=word_image, anchor="center")
        canvas.image = word_image
    else:
        canvas.delete("all")
        canvas.create_text(300, 150, text="Image not found", font=("Helvetica", 18), fill="red")

# Function to capture an image from the camera
def capture_image():
    image_path = "/home/t49/Downloads/captured_image.jpg"
    picam.start()
    picam.capture_file(image_path)
    picam.stop()
    return image_path

# Function to process the captured image
def process_image():
    global random_word, score

    # Capture an image
    captured_image_path = capture_image()
    with open(captured_image_path, "rb") as image_file:
        response = requests.post(
            "http://<COLAB_SERVER_IP>:5000/process", 
            files={"image": image_file},
            data={"expected_word": random_word}
        )

    # Parse the response
    result = response.json()
    detected_string = result.get("detected", "")
    is_correct = result.get("is_correct", False)

    # Update the score and display results
    if is_correct:
        score += 1
        result_label.config(text=f"Correct! 🎉 (Detected: {detected_string})", fg="green")
    else:
        result_label.config(text=f"Incorrect. (Detected: {detected_string}, Expected: {random_word})", fg="red")

# Function to select a random word, voice it, and display the associated image
def select_random_word():
    global random_word, word_count

    if word_count >= max_words:
        result_label.config(text=f"Game Over! Your score: {score}/{max_words}", fg="blue")
        next_button.config(state="disabled")
        return

    word_count += 1
    random_word = random.choice(words)
    word_label.config(text=f"Spell This Word: {random_word}")
    result_label.config(text="")
    play_audio_and_display_image(random_word)

# List of words
words = [
    "APPLE", "BALL", "BOOK", "CUP", "DOG", "FISH", "STAR", "SUN", "TREE", "COLD",
    "FAMILY", "FAST", "GREEN", "HAPPY", "HOUSE", "JUMP", "RED", "SING", "YELLOW",
]

# Initialize tkinter GUI
root = Tk()
root.title("Spell the Word")
root.geometry("800x600")

# Word label
word_label = Label(root, text="Click 'Next' to hear the word", font=("Helvetica", 16))
word_label.pack(pady=10)

# Canvas for displaying the word image
canvas = Canvas(root, width=600, height=300)
canvas.pack()

# Button to check spelling using the camera
check_button = Button(root, text="Check Spelling", command=process_image, font=("Helvetica", 14))
check_button.pack(pady=10)

# Next button to select a new word
next_button = Button(root, text="Next", command=select_random_word, font=("Helvetica", 14))
next_button.pack(pady=10)

# Result label
result_label = Label(root, text="", font=("Helvetica", 14))
result_label.pack(pady=10)

# Run the tkinter main loop
root.mainloop()
