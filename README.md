# Face Recognition with Arduino Control

This project implements a real-time face recognition system using OpenCV, DeepFace, and MTCNN. The system detects faces via a webcam, verifies them against stored reference images, and sends signals to an Arduino to open a door if a face is recognized.

## Features
- **Face Detection**: Uses MTCNN to detect faces in real time.
- **Face Recognition**: Compares detected faces with stored images using DeepFace (VGG-Face model).
- **Arduino Integration**: Sends a signal to an Arduino to open a door upon recognizing a face.
- **Multi-threading**: Uses threading to improve recognition performance.
- **Real-time UI Updates**: Displays recognition status with green/red rectangles and text labels.

## Requirements

Ensure you have the following installed:

- Python 3.x
- OpenCV (`cv2`)
- DeepFace
- MTCNN
- NumPy
- PySerial (for Arduino communication)

To install dependencies, run:
```bash
pip install opencv-python deepface mtcnn numpy pyserial
```

## Setup
1. **Connect Arduino**: Ensure your Arduino is connected via USB and recognized as `/dev/ttyUSB0` (Linux) or `COMx` (Windows).
2. **Prepare Face Reference Images**:
   - Create a folder named `saved_faces`.
   - Store images of authorized faces inside this folder.
3. **Run the Program**:
```bash
python face_recognition.py
```

## How It Works
1. The camera captures frames and detects faces using MTCNN.
2. Detected faces are cropped and sent to a background thread for recognition.
3. If the face matches a stored image (confidence > 60%), the system:
   - Draws a **green rectangle** around the face.
   - Displays **'Face Recognized'**.
   - Sends a **'OPEN'** signal to Arduino.
4. If not recognized:
   - Draws a **red rectangle**.
   - Displays **'Not Recognized'**.

## Arduino Integration
This project sends a simple command (`OPEN`) to an Arduino via serial communication. The Arduino should be programmed to read this signal and trigger a relay or motor.

### Example Arduino Code
```cpp
void setup() {
    Serial.begin(9600);
    pinMode(13, OUTPUT);
}
void loop() {
    if (Serial.available()) {
        String command = Serial.readStringUntil('\n');
        if (command == "OPEN") {
            digitalWrite(13, HIGH);
            delay(5000);
            digitalWrite(13, LOW);
        }
    }
}
```

## Keyboard Controls
- **Press 'q'** to quit the program.

## Future Improvements
- Add a GUI for managing stored faces.
- Implement a cloud-based face database.
- Improve recognition speed with GPU acceleration.

## License
This project is open-source and available under the MIT License.

## Author
Developed by MkMAD

