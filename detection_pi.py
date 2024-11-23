import cv2
from picamera2 import Picamera2
from ultralytics import YOLO
from tkinter import Tk, Button, Canvas
from PIL import Image, ImageTk

# Initialize Picamera2
picam = Picamera2()

# Set up camera configuration
camera_config = picam.create_still_configuration()
picam.configure(camera_config)

# Initialize YOLO model
model = YOLO("/path/to/your/yolo_model.pt")  # Replace with your model path

# Function to capture an image and process it with the YOLO model
def capture_and_process():
    # Capture image
    picam.start()
    image_path = "/home/pi/captured_image.jpg"  # Replace with your desired path
    picam.capture_file(image_path)
    picam.stop()

    # Load the captured image
    img = cv2.imread(image_path)

    # Perform inference
    results = model(img)

    # Draw bounding boxes on the image
    for box in results[0].boxes.xyxy:
        x1, y1, x2, y2 = map(int, box[:4])  # Bounding box coordinates
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)  # Green rectangle

    # Convert the image to a format suitable for tkinter
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(img_rgb)
    tk_img = ImageTk.PhotoImage(pil_img)

    # Display the image with bounding boxes on the canvas
    canvas.delete("all")  # Clear any previous content
    canvas.create_image(0, 0, anchor="nw", image=tk_img)
    canvas.image = tk_img  # Keep a reference to prevent garbage collection

# Initialize tkinter GUI
root = Tk()
root.title("Capture and Detect")
root.geometry("800x600")

# Canvas to display the image
canvas = Canvas(root, width=640, height=480, bg="black")
canvas.pack(pady=20)

# Capture button
capture_button = Button(root, text="Capture", command=capture_and_process, font=("Helvetica", 14))
capture_button.pack()

# Run tkinter main loop
root.mainloop()
