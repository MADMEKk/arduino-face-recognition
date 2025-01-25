import cv2
import time
import os
import numpy as np
import serial
import gc
import logging
from threading import Thread, Lock
from queue import Queue
from deepface import DeepFace
from mtcnn import MTCNN

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

FACE_REFERENCE_DIR = "saved_faces"  # Directory containing registered face images
RECOGNITION_THRESHOLD = 0.4  # Lower values make matching stricter

face_detector = MTCNN()
face_queue = Queue()
face_results = {}  # Stores recognized face results
face_results_lock = Lock()  # Lock to avoid concurrent access issues

# Try connecting to Arduino
try:
    arduino = serial.Serial(port='/dev/ttyUSB0', baudrate=9600, timeout=1)
    time.sleep(2)
except serial.SerialException as e:
    logging.error(f"Could not connect to Arduino: {e}")
    arduino = None

def recognize_face(cropped_face):
    """Compares a detected face with saved faces and returns True if recognized."""
    for filename in os.listdir(FACE_REFERENCE_DIR):
        reference_image = os.path.join(FACE_REFERENCE_DIR, filename)

        try:
            result = DeepFace.verify(
                img1_path=cropped_face, 
                img2_path=reference_image, 
                model_name="VGG-Face",
                distance_metric="cosine",
                enforce_detection=False
            )

            if result["verified"]:
                logging.info(f"✅ User {filename} recognized. Distance: {result['distance']}")
                return True
            else:
                logging.info(f"❌ User {filename} not recognized. Distance: {result['distance']}")

        except Exception as e:
            logging.error(f"🚨 Face recognition error: {e}")

    return False

def send_signal(message):
    """Send a signal to Arduino."""
    if arduino:
        try:
            arduino.write(message.encode())
            logging.info(f"📡 Sent signal: {message}")
        except serial.SerialException as e:
            logging.error(f"⚠️ Error: Failed to send signal to Arduino: {e}")
    else:
        logging.warning("Arduino not connected. Simulating signal send.")
        logging.info(f"📡 Simulated signal: {message}")

    gc.collect()

def detect_faces(frame):
    """Detects faces in a frame and returns cropped faces with positions."""
    faces = face_detector.detect_faces(frame)
    detected_faces = []

    for face in faces:
        x, y, w, h = face['box']
        cropped_face = frame[y:y+h, x:x+w]
        detected_faces.append((cropped_face, (x, y, w, h)))

    return detected_faces

def face_recognition_worker():
    """Thread that processes face recognition from the queue."""
    while True:
        if not face_queue.empty():
            cropped_face, face_position = face_queue.get()
            recognized = recognize_face(cropped_face)

            with face_results_lock:
                face_results[face_position] = "Recognized" if recognized else "Not Recognized"
                logging.info(f"Updated face_results: {face_results}")

            if recognized:
                send_signal("OPEN")

        time.sleep(0.1)

def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        logging.error("Could not open camera.")
        return

    logging.info("📸 System Ready: Scanning for faces...")

    Thread(target=face_recognition_worker, daemon=True).start()

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                logging.error("Failed to grab frame.")
                break

            frame = cv2.resize(frame, (640, 480))
            detected_faces = detect_faces(frame)

            with face_results_lock:
                # Remove old results for faces that are no longer detected
                current_positions = {pos for _, pos in detected_faces}
                face_results_keys = list(face_results.keys())
                for key in face_results_keys:
                    if key not in current_positions:
                        del face_results[key]

            for cropped_face, (x, y, w, h) in detected_faces:
                face_queue.put((cropped_face, (x, y, w, h)))

                with face_results_lock:
                    label = face_results.get((x, y, w, h), "Processing...")
                    logging.info(f"Displaying label for face at {x}, {y}: {label}")

                # Set rectangle and text color based on recognition status
                if label == "Recognized":
                    color = (0, 255, 0)  # Green for recognized
                    message = "Face Recognized"
                else:
                    color = (0, 0, 255)  # Red for not recognized
                    message = "Not Recognized"

                # Draw rectangle around the face
                cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)

                # Display recognition message above the rectangle
                cv2.putText(frame, message, (x, y - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2, cv2.LINE_AA)

            # Display the frame
            cv2.imshow("Face Recognition", frame)

            # Exit on 'q' key press
            if cv2.waitKey(10) & 0xFF == ord('q'):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()
        if arduino:
            arduino.close()

if __name__ == "__main__":
    main()