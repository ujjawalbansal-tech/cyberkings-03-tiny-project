import cv2
import os
import numpy as np

dataset_path = "dataset"
recognizer = cv2.face.LBPHFaceRecognizer_create()  # Create recognizer
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

faces = []
labels = []

# Loop through all user folders
for user_folder in os.listdir(dataset_path):
    label = int(user_folder.split("_")[1])  # user_1 -> 1
    folder_path = os.path.join(dataset_path, user_folder)
    for image_name in os.listdir(folder_path):
        img_path = os.path.join(folder_path, image_name)
        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        faces.append(img)
        labels.append(label)

faces = np.array(faces)
labels = np.array(labels)

# Train the recognizer
recognizer.train(faces, labels)

# Save the trained model
recognizer.save("face_recognizer.yml")
print("Face recognition model trained and saved successfully!")