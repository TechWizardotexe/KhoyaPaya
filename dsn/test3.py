import cv2
import face_recognition
import os
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import tempfile
import subprocess
from PIL import Image, ImageTk
import time
import sys

# Function to search for image details in the "data" folder


def search_image_details(filename):
    details_file_path = os.path.join(
        "data", f"{os.path.splitext(filename)[0]}.txt")

    if os.path.exists(details_file_path):
        with open(details_file_path, "r") as details_file:
            return details_file.read()
    else:
        return "Details not available"

# Function to match a face with all faces in the "images" folder


def match_face(face_encoding):
    match_found = False
    for filename in os.listdir("images"):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            reference_image = face_recognition.load_image_file(
                os.path.join("images", filename))
            reference_face_encoding = face_recognition.face_encodings(
                reference_image)

            if len(reference_face_encoding) > 0:
                match = face_recognition.compare_faces(
                    [reference_face_encoding[0]], face_encoding)

                if match[0]:
                    # Search for image details
                    image_details = search_image_details(filename)

                    with open("results.txt", "a") as result_file:
                        result_file.write(
                            f"{datetime.now()} - Match Found: {filename}\n")
                        result_file.write(f"Details: {image_details}\n")

                    popup_window = tk.Toplevel()
                    popup_window.title("Face Match")

                    matched_image = cv2.imread(
                        os.path.join("images", filename))
                    matched_image = cv2.cvtColor(
                        matched_image, cv2.COLOR_BGR2RGB)
                    photo = ImageTk.PhotoImage(
                        image=Image.fromarray(matched_image))
                    label_image = tk.Label(popup_window, image=photo)
                    label_image.pack()
                    label_filename = tk.Label(
                        popup_window, text=f"File Name: {filename}")
                    label_filename.pack()
                    label_details = tk.Label(
                        popup_window, text=f"Details: {image_details}")
                    label_details.pack()

                    # Schedule the popup window to be destroyed after 2 seconds
                    popup_window.after(
                        2000, lambda: destroy_popup_and_exit(popup_window))

                    popup_window.mainloop()

                    match_found = True

    if not match_found:
        messagebox.showinfo("Face Match", "No Match Found")
        time.sleep(3)
        sys.exit()


def destroy_popup_and_exit(popup_window):
    popup_window.destroy()
    time.sleep(2)  # Delay for 2 seconds
    sys.exit()


# Create a tkinter window
root = tk.Tk()
root.withdraw()

cap = cv2.VideoCapture(0)

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        face_locations = face_recognition.face_locations(frame)
        if len(face_locations) > 0:
            face_encoding = face_recognition.face_encodings(
                frame, [face_locations[0]])[0]

            match_face(face_encoding)

except KeyboardInterrupt:
    pass

cap.release()
cv2.destroyAllWindows()


def remove_duplicates(file_path):
    with open(file_path, "r") as file:
        lines = file.readlines()

    # Remove duplicates
    unique_lines = list(set(lines))

    with open(file_path, "w") as file:
        file.writelines(unique_lines)


# Call the function to remove duplicates from "results.txt"
remove_duplicates("results.txt")
