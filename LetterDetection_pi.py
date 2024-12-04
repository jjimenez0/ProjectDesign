import tkinter as tk
import cv2
import pytesseract
from picamera2 import Picamera2
from ultralytics import YOLO
from PIL import Image, ImageTk

# Initialize the camera and the YOLO model
picam = Picamera2()
picam.configure(picam.create_still_configuration())
trained_model = YOLO("/home/t49/Downloads/best_model.pt")  # Path to your YOLO model

# Initialize the Tkinter GUI
root = tk.Tk()
root.title("Letter Detection")
root.geometry("800x600")

# Canvas to display the image and detected letters
canvas = tk.Canvas(root, width=600, height=400, bg="white")
canvas.pack(pady=10)

# Frame to display detected letters
letters_frame = tk.Frame(root)
letters_frame.pack(pady=10)

detected_letters_label = tk.Label(letters_frame, text="Detected Letters:", font=("Helvetica", 14))
detected_letters_label.pack(anchor="w")

letters_container = tk.Label(letters_frame, text="", font=("Helvetica", 18), fg="blue")
letters_container.pack(anchor="w")

# Function to capture an image, detect letters, and display results
def capture_and_detect():
    # Capture an image from the camera
    image_path = "/home/t49/Downloads/captured_image.jpg"
    picam.start()
    picam.capture_file(image_path)
    picam.stop()
    img = cv2.imread(image_path)

    # Perform detection with YOLO
    results = trained_model(img)
    boxes = results[0].boxes.xyxy.cpu().numpy().astype(int)

    # Sort boxes by x1 coordinate for left-to-right order
    boxes = sorted(boxes, key=lambda box: box[0])

    # Detected letters
    detected_letters = []

    # Crop segments and detect letters using PyTesseract
    for box in boxes:
        x1, y1, x2, y2 = box
        cropped_img = img[y1:y2, x1:x2]

        # Preprocess cropped image
        gray_cropped_img = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2GRAY)
        _, binary_img = cv2.threshold(gray_cropped_img, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

        # Perform OCR using Tesseract
        letter = pytesseract.image_to_string(
            binary_img, config='--psm 10 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        ).strip()

        if letter:  # Only add non-empty detections
            detected_letters.append(letter)

    # Combine detected letters into a string
    detected_string = ''.join(detected_letters)

    # Display detected letters in the Tkinter window
    letters_container.config(text=detected_string)

    # Convert the image to RGB for display in Tkinter
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_resized = cv2.resize(img_rgb, (600, 400))
    img_tk = ImageTk.PhotoImage(image=Image.fromarray(img_resized))

    # Update the canvas with the captured image
    canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)
    canvas.image = img_tk  # Keep a reference to avoid garbage collection

# Button to capture an image and process it
capture_button = tk.Button(root, text="Capture and Detect", command=capture_and_detect, font=("Helvetica", 14))
capture_button.pack(pady=10)

# Run the Tkinter main loop
root.mainloop()
