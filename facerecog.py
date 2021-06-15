import time
start = time.time()
import cv2
import face_recognition
import numpy as np
import pickle
import time
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import os
import sqlite3

idMatch = []
registeredPersons = []
incomingPerson = []
window = tk.Tk()
window.geometry("1200x640")
window.wm_title("Face Recognition")

connection = sqlite3.connect("Database")
cursor = connection.cursor()


def createTable():
    cursor.execute("CREATE TABLE IF NOT EXISTS db (name TEXT, date TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS dbReg (id INTEGER, name TEXT)")
    connection.commit()


def addData(name, date):
    cursor.execute("Insert Into db Values (?, ?)", (str(name), str(date),))
    connection.commit()


def dbEntry(id, name):
    cursor.execute("Insert Or Ignore Into dbReg VALUES (?, ?)", (int(id), str(name),))
    connection.commit()


def incomingPerson():
    cursor.execute("Select * From db")
    data = cursor.fetchall()
    for i in data:
        incomingPerson.append(i)


def registeredPersons():
    cursor.execute("Select * From dbReg")
    data = cursor.fetchall()
    for i in data:
        registeredPersons.append(i)


def faceRecognition():
    cap = cv2.VideoCapture(1)
    while True:
        ret, image_np = cap.read()
        with open('dataset_faces.dat', 'rb') as f:
            faces = pickle.load(f)

        faces_encoded = np.array(list(faces.values()))
        known_face_names = np.array(list(faces.keys()))
        img = image_np
        face_locations = face_recognition.face_locations(img)
        unknown_face_encodings = face_recognition.face_encodings(img, face_locations)
        face_names = []

        for face_encoding in unknown_face_encodings:
            matches = face_recognition.compare_faces(faces_encoded, face_encoding, tolerance=0.45)
            name = "Not Recognized"
            login = "Login Confirmed"
            face_distances = face_recognition.face_distance(faces_encoded, face_encoding)
            best_match_index = np.argmin(face_distances)

            if matches[best_match_index]:
                name = known_face_names[best_match_index]
                face_names.append(name)
                
                for (top, right, bottom, left), name in zip(face_locations, face_names):
                    cv2.rectangle(image_np, (left - 20, top - 20), (right + 20, bottom + 20), (127, 255, 0), 2)
                    cv2.rectangle(image_np, (left - 20, bottom - 15), (right + 20, bottom + 20), (127, 255, 0), cv2.FILLED)
                    font = cv2.FONT_HERSHEY_DUPLEX
                    cv2.putText(image_np, name, (left - 20, bottom + 15), font, 1.0, (255, 255, 255), 2)
                    cv2.putText(image_np, login, (left - 20, bottom - 60), font, 1.0, (255, 255, 255), 2)
                    if name in incomingPerson:
                        continue
                    else:
                        addData(name=name, date=time.strftime("%m/%d/%Y, %H:%M:%S", time.localtime()))

            else:
                name1 = "Not Recognized"
                face_names.append(name)

                for (top, right, bottom, left), name in zip(face_locations, face_names):
                     cv2.rectangle(image_np, (left - 20, top - 20), (right + 20, bottom + 20), (0, 0, 255), 2)
                     cv2.rectangle(image_np, (left - 20, bottom - 15), (right + 20, bottom + 20), (0, 0, 255), cv2.FILLED)
                     font = cv2.FONT_HERSHEY_DUPLEX
                     cv2.putText(image_np, name1, (left - 20, bottom + 15), font, 1.0, (255, 255, 255), 2)

        cv2.imshow('Video', image_np)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break

def getEncodedFaces():
    encoded = {}
    for dirpath, dnames, fnames in os.walk("./faces"):
        for f in fnames:
            if f.endswith(".jpg") or f.endswith(".png") or f.endswith(".jpeg"):
                face = face_recognition.api.load_image_file("faces/" + f)
                encoding = face_recognition.face_encodings(face)[0]
                encoded[f.split(".")[0]] = encoding
    with open('dataset_faces.dat', 'wb') as f:
        pickle.dump(encoded, f)

    message_box = messagebox.showinfo(title="Info", message="Person Registered")
    print(message_box)
    return encoded


def getPersons():
    i = 0
    for i in range(len(incomingPerson)):
        listBox.insert(i, incomingPerson[i])
        i = i + 1


def getRegisteredPersons():
    i = 0
    for i in range(len(registeredPersons)):
        listBox1.insert(i, registeredPersons[i])
        i = i + 1


def registerPerson():
    cap = cv2.VideoCapture(1)
    while True:
        ret, save_photo = cap.read()
        value = entry.get()
        additional = ".jpg"
        id = int(entry2.get())
        info = "Press 'k' to save"

        dbEntry(id, name=value)

        cv2.imshow('Video', save_photo)
        if cv2.waitKey(1) & 0xFF == ord('k'):
            cv2.imwrite("./faces/" + value + additional, save_photo)
            cv2.destroyAllWindows()
            break

pw = ttk.Panedwindow(window, orient=tk.HORIZONTAL)
pw.pack(fill=tk.BOTH, expand=True)

m2 = ttk.Panedwindow(pw, orient=tk.VERTICAL)

frame2 = ttk.Frame(pw, width=400, height=340, relief=tk.RIDGE)
frame3 = ttk.Frame(pw, width=620, height=300, relief=tk.RAISED)
m2.add(frame2)
m2.add(frame3)

frame1 = ttk.Frame(pw, width=460, height=640, relief=tk.GROOVE)
pw.add(m2)
pw.add(frame1)

label1 = tk.Label(frame2, text="")
label1.place(x=35, y=90)

label2 = tk.Label(frame2, text="Kişi Adı: Info: Press the 'k' key when the camera is turned on to take a photo!")
label2.place(x=5, y=120)

entry = tk.Entry(frame2, width=35)
entry.insert(string="", index=0)
entry.place(x=70, y=120)

label4 = tk.Label(frame2, text="id: ")
label4.place(x=5, y=150)

entry2 = tk.Entry(frame2, width=35)
entry2.insert(string="", index=0)
entry2.place(x=70, y=150)


button1 = tk.Button(frame2, text="Take a Photo", command=registerPerson, width=20, height=3)
button1.place(x=350, y=100)

button3 = tk.Button(frame2, text="Save", command=getEncodedFaces, width=20, height=3)
button3.place(x=350, y=170)

button2 = tk.Button(frame3, text="Open Person Recognition", command=faceRecognition, width=30, height=6)
button2.place(x=200, y=100)

button3 = tk.Button(frame1, text="Incoming Persons", command=getPersons, width=20, height=3)
button3.place(x=70, y=20)

button4 = tk.Button(frame1, text="People Registered in the System", command=getRegisteredPersons, width=20, height=3)
button4.place(x=380, y=20)

listBox = tk.Listbox(frame1, selectmode=tk.MULTIPLE, command=incomingPerson(), height=25, width=50)
listBox.place(x=30, y=120)

listBox1 = tk.Listbox(frame1, selectmode=tk.MULTIPLE, command=registeredPersons(), height=25, width=30)
listBox1.place(x=360, y=120)

window.mainloop()
