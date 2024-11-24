import random
import cv2
from ultralytics import YOLO
from picamera2 import Picamera2, Preview
import pytesseract
import os
from tkinter import Tk, Label, Button, Canvas, PhotoImage

# Global variables for scoring and control
score = 0
word_count = 0
max_words = 10
random_word = None

# Initialize Picamera2
picam = Picamera2()
picam.configure(picam.create_still_configuration())

# Initialize TTS engine
import pyttsx3
tts_engine = pyttsx3.init()

# Function to play audio using pyttsx3 and display the word image
def play_audio_and_display_image(word):
    # Speak the word
    tts_engine.say(word)
    tts_engine.runAndWait()

    # Load and display the associated image
    image_file = os.path.join("/home/t49/Downloads/word_images", f"{word}.png")
    if os.path.exists(image_file):
        word_image = PhotoImage(file=image_file)
        canvas.delete("all")  # Clear the canvas
        canvas.create_image(300, 150, image=word_image, anchor="center")
        canvas.image = word_image  # Keep a reference to prevent garbage collection
    else:
        canvas.delete("all")  # Clear the canvas
        canvas.create_text(
            300, 150, text="Image not found", font=("Helvetica", 18), fill="red"
        )

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
    img = cv2.imread(captured_image_path)

    # Perform inference
    results = trained_model(img)

    # Get bounding box coordinates
    boxes = results[0].boxes.xyxy.cpu().numpy().astype(int)

    # Sort bounding boxes by x1 coordinate (left to right)
    boxes = sorted(boxes, key=lambda box: box[0])

    # Initialize an array to store detected letters
    detected_letters = []

    # Iterate through each bounding box
    for i, box in enumerate(boxes):
        x1, y1, x2, y2 = box
        cropped_img = img[y1:y2, x1:x2]

        # Preprocess the cropped image
        gray_cropped_img = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2GRAY)
        _, binary_img = cv2.threshold(gray_cropped_img, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

        # Perform OCR using PyTesseract with lower PSM values
        letter = pytesseract.image_to_string(
            binary_img,
            config='--psm 10 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        ).strip()

        # Add the detected letter to the array
        detected_letters.append(letter)

    # Combine detected letters into a string
    detected_string = ''.join(detected_letters)

    # Compare detected string to the random word
    if detected_string.upper() == random_word.upper():
        score += 1
        result_label.config(text=f"Correct! 🎉 (Detected: {detected_string})", fg="green")
    else:
        result_label.config(text=f"Incorrect. (Detected: {detected_string}, Expected: {random_word})", fg="red")

# Function to select a random word, voice it, and display the associated image
def select_random_word():
    global random_word, word_count

    # Check if the maximum word count is reached
    if word_count >= max_words:
        result_label.config(text=f"Game Over! Your score: {score}/{max_words}", fg="blue")
        next_button.config(state="disabled")
        return

    # Move to the next word
    word_count += 1
    random_word = random.choice(words)
    word_label.config(text=f"Spell This Word: {random_word}")
    result_label.config(text="")  # Clear previous result
    play_audio_and_display_image(random_word)

# List of words in all caps
words = [
    "APPLE", "BALL", "BOOK", "CUP", "DOG", "FISH", "STAR", "SUN", "TREE", "COLD",
    "FAMILY", "FAST", "GREEN", "HAPPY", "HOUSE", "JUMP", "RED", "SING", "YELLOW",
    "BEACH", "DOCTOR", "FARMER", "FOREST", "MOUNTAIN", "QUIET", "RIVER", "SUMMER",
    "TEACHER", "WINTER", "ANCIENT", "CLASSROOM", "EDUCATION", "ENVIRONMENT",
    "HOMEWORK", "INNOVATION", "KNOWLEDGE", "LANGUAGE", "RESEARCH", "SCIENCE"
]

# Load the trained YOLO model
trained_model = YOLO("/home/t49/Downloads/best_model.pt")

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
