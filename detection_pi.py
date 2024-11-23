import cv2
import tkinter as tk
from picamera2 import Picamera2
import numpy as np
from ultralytics import YOLO

# Initialize the camera and YOLO model
camera = Picamera2()
camera.configure(camera.create_still_configuration())
trained_model = YOLO("/home/t49/Downloads/best_model.pt")

# Function to capture an image, run YOLO inference, and display the result
def capture_and_process():
    # Capture an image from the camera
    camera.start()
    image = camera.capture_array()
    camera.stop()

    # Convert the image from BGR to RGB for displaying
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Run YOLO inference
    results = trained_model(image)

    # Get bounding boxes
    boxes = results[0].boxes.xyxy.cpu().numpy().astype(int)

    # Draw bounding boxes on the image
    for box in boxes:
        x1, y1, x2, y2 = box
        cv2.rectangle(image_rgb, (x1, y1), (x2, y2), (0, 255, 0), 2)

    # Convert the image to Tkinter-compatible format
    height, width, _ = image_rgb.shape
    image_tk = tk.PhotoImage(data=cv2.imencode('.png', image_rgb)[1].tobytes())

    # Display the image on the canvas
    canvas.config(width=width, height=height)
    canvas.create_image(0, 0, anchor=tk.NW, image=image_tk)
    canvas.image = image_tk  # Keep a reference to avoid garbage collection

# Initialize the Tkinter GUI
root = tk.Tk()
root.title("Capture and Process Image")

# Create a Canvas to display the image
canvas = tk.Canvas(root)
canvas.pack()

# Create a button to capture and process the image
capture_button = tk.Button(root, text="Capture", command=capture_and_process, font=("Helvetica", 14))
capture_button.pack(pady=10)

# Run the Tkinter main loop
root.mainloop()
