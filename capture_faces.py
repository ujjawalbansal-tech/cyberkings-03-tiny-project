import cv2
import os

# Create main dataset folder if not exists
dataset_path = "dataset"
if not os.path.exists(dataset_path):
    os.makedirs(dataset_path)

# Load Haar cascade for face detection
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

# User input
user_id = input("Enter User ID: ").strip()
max_images = int(input("Kitni images leni hain?: "))

# Create folder for this user
user_folder = os.path.join(dataset_path, f"user_{user_id}")
if not os.path.exists(user_folder):
    os.makedirs(user_folder)

# Open webcam
cap = cv2.VideoCapture(0)

count = 0
print("Press 'q' to exit anytime.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Camera error")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        count += 1
        face = gray[y:y+h, x:x+w]
        face = cv2.resize(face, (200, 200))  # Resize face to 200x200
        cv2.imwrite(os.path.join(user_folder, f"{user_id}_{count}.jpg"), face)
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

    cv2.imshow("Capture Faces - Press Q to Exit", frame)

    if count >= max_images:
        print(f"Reached max images: {max_images}")
        break

    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Capture stopped by user")
        break

cap.release()
cv2.destroyAllWindows()
print(f"{count} images captured successfully for User {user_id}!")