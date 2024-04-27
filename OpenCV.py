import cv2
import serial
import time
import math

# Initialize serial connection (adjust port and baud rate as needed)
ser = serial.Serial('COM5', 9600)  # Change port if necessary

# Load the pre-trained Haar cascade classifiers for human and dog detection
human_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_alt.xml')
dog_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_alt2.xml')  # Use alt2.xml for better dog detection

# Initialize video capture from the laptop camera
cap = cv2.VideoCapture(0)

# Set minimum size for detection
min_face_size = (50, 50)

# Initialize time variables
last_detection_time = time.time()
detection_interval = 5  # Detection interval in seconds

# Initialize variables for accuracy measurement
total_frames = 0
correct_human_detections = 0
correct_dog_detections = 0

while True:
    # Read frame from the camera
    ret, frame = cap.read()
    
    # Mirror the frame horizontally
    frame = cv2.flip(frame, 1)
    
    # Convert the frame to grayscale for detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Detect human faces
    human_faces = human_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=min_face_size)

    # Detect dog faces
    dog_faces = dog_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=min_face_size)

    # Determine the closest detection
    closest_face = None
    min_distance = float('inf')
    for (x, y, w, h) in human_faces:
        center_x = x + w // 2
        center_y = y + h // 2
        distance = math.sqrt((center_x - frame.shape[1] // 2) ** 2 + (center_y - frame.shape[0] // 2) ** 2)
        if distance < min_distance:
            min_distance = distance
            closest_face = (x, y, w, h)
    for (x, y, w, h) in dog_faces:
        center_x = x + w // 2
        center_y = y + h // 2
        distance = math.sqrt((center_x - frame.shape[1] // 2) ** 2 + (center_y - frame.shape[0] // 2) ** 2)
        if distance < min_distance:
            min_distance = distance
            closest_face = (x, y, w, h)
    
    # Determine the type of detection
    detection_type = None
    if closest_face is not None:
        if closest_face in human_faces:
            detection_type = 'human'
        else:
            detection_type = 'animal'
    
    # Send command to Arduino based on detection result if detection interval has elapsed
    if time.time() - last_detection_time >= detection_interval:
        if detection_type == 'human':
            ser.write(b'H')  # Send 'H' for human detection
            print("Human detected - Dustbin opened")
            correct_human_detections += 1
        elif detection_type == 'animal':
            ser.write(b'D')  # Send 'D' for dog detection
            print("Dog detected - Buzzer turned on")
            correct_dog_detections += 1
        else:
            ser.write(b'N')  # Send 'N' for no detection
            print("No human or animal detected")
        
        # Update last detection time
        last_detection_time = time.time()
    
    # Increment total frame count
    total_frames += 1
    
    # Draw rectangle around the closest detected face
    if closest_face is not None:
        (x, y, w, h) = closest_face
        if detection_type == 'human':
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            cv2.putText(frame, 'Human', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)
        elif detection_type == 'animal':
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(frame, 'Animal', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
    
    # Display the mirrored frame with detection results
    cv2.imshow('Object Detection', frame)
    
    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Calculate accuracy
human_accuracy = (correct_human_detections / total_frames) * 100 if total_frames > 0 else 0
dog_accuracy = (correct_dog_detections / total_frames) * 100 if total_frames > 0 else 0

print(f"Human detection accuracy: {human_accuracy:.2f}%")
print(f"Dog detection accuracy: {dog_accuracy:.2f}%")
