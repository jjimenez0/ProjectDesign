import random
import cv2
from ultralytics import YOLO
from picamera2 import Picamera2
import pytesseract
import os
from tkinter import Tk, Label, Button, Canvas, PhotoImage
from transformers import MarianTokenizer, MarianMTModel
import pyttsx3

# Global variables for scoring and control
score = 0
word_count = 0
max_words = 10
random_word = None

# Initialize Picamera2
picam = Picamera2()
picam.configure(picam.create_still_configuration())

# Initialize TTS engine
tts_engine = pyttsx3.init()

# Load MarianMT model for spelling correction
model_path = "/content/drive/MyDrive/MarianMT_Model"
tokenizer = MarianTokenizer.from_pretrained(model_path)
mt_model = MarianMTModel.from_pretrained(model_path)

# Function to correct spelling errors using MarianMT
def correct_spelling(input_text):
    inputs = tokenizer(input_text, return_tensors="pt", max_length=512, truncation=True, padding=True)
    outputs = mt_model.generate(**inputs, max_length=512, num_beams=5, early_stopping=True)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

# Function to play audio and display the word image
def play_audio_and_display_image(word):
    # Speak the word
    tts_engine.say(word)
    tts_engine.runAndWait()

    # Capture and display an image from the camera
    captured_image_path = capture_image()
    img = PhotoImage(file=captured_image_path)
    canvas.delete("all")
    canvas.create_image(300, 150, image=img, anchor="center")
    canvas.image = img

# Function to capture an image
def capture_image():
    image_path = "/home/t49/Downloads/captured_image.jpg"
    picam.start()
    picam.capture_file(image_path)
    picam.stop()
    return image_path

# Function to process the captured image and check spelling
def process_image():
    global random_word, score

    captured_image_path = capture_image()
    img = cv2.imread(captured_image_path)

    # Perform inference
    results = trained_model(img)
    boxes = results[0].boxes.xyxy.cpu().numpy().astype(int)
    boxes = sorted(boxes, key=lambda box: box[0])

    detected_letters = []
    for box in boxes:
        x1, y1, x2, y2 = box
        cropped_img = img[y1:y2, x1:x2]
        gray_cropped_img = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2GRAY)
        _, binary_img = cv2.threshold(gray_cropped_img, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

        letter = pytesseract.image_to_string(
            binary_img, config='--psm 10 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        ).strip()
        detected_letters.append(letter)

    detected_string = ''.join(detected_letters)
    corrected_string = correct_spelling(detected_string)

    if corrected_string.upper() == random_word.upper():
        score += 1
        result_label.config(text=f"Correct! 🎉 (Detected: {corrected_string})", fg="green")
    else:
        result_label.config(
            text=f"Incorrect. (Detected: {corrected_string}, Expected: {random_word})", fg="red"
        )

# Function to select a random word
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
    'A', 'I', 'AM', 'AT', 'DO', 'GO', 'HE', 'IF', 'IN', 'IS', 'IT', 'ME', 'MY', 'NO',
    'OF', 'OH', 'ON', 'SO', 'TO', 'UP', 'US', 'WE', 'YES', 'AND', 'BED', 'BIG', 'BOY',
    'BUT', 'CAN', 'CAR', 'CAT', 'COW', 'DAD', 'DAY', 'DID', 'DOG', 'FAT', 'FOR', 'FUN',
    'GET', 'HAD', 'HAT', 'HEN', 'HIM', 'HIS', 'LET', 'MAN', 'MAY', 'MOM', 'NOT', 'OLD',
    'ONE', 'PAN', 'PET', 'PIG', 'RAN', 'RAT', 'RED', 'SAT', 'SEE', 'SHE', 'SIT', 'SIX',
    'SUN', 'TEN', 'THE', 'TOP', 'TOY', 'TWO', 'WAS', 'YOU', 'BOOK', 'HOME', 'INTO',
    'LOOK', 'PLAY', 'STOP', 'THIS', 'WILL', 'GOOD'
]

# Load the trained YOLO model
trained_model = YOLO("/home/t49/Downloads/YOLO_BEST.pt")

# Initialize tkinter GUI
root = Tk()
root.title("Spell the Word")
root.geometry("800x600")

word_label = Label(root, text="Click 'Next' to hear the word", font=("Helvetica", 16))
word_label.pack(pady=10)

canvas = Canvas(root, width=600, height=300)
canvas.pack()

check_button = Button(root, text="Check Spelling", command=process_image, font=("Helvetica", 14))
check_button.pack(pady=10)

next_button = Button(root, text="Next", command=select_random_word, font=("Helvetica", 14))
next_button.pack(pady=10)

result_label = Label(root, text="", font=("Helvetica", 14))
result_label.pack(pady=10)

root.mainloop()
