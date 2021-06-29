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
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import os
from PIL import ImageTk, Image
import threading
import sqlite3
from collections import defaultdict
import collections

id_esleme = []
kayitliKisiler = []
gelenKisiler = []
window = tk.Tk()
window.geometry("1200x640")
window.wm_title("Yuz tanima")

baglanti = sqlite3.connect("Giris Otomasyon")
imlec = baglanti.cursor()


def tablo_olustur():
    imlec.execute("CREATE TABLE IF NOT EXISTS vt (isim TEXT, zaman TEXT)")
    imlec.execute("CREATE TABLE IF NOT EXISTS vt_kayit (id INTEGER, isim, TEXT)")
    baglanti.commit()


def veri_ekle(isim, zaman):
    imlec.execute("Insert Into vt Values (?, ?)", (str(isim), str(zaman),))
    baglanti.commit()

def vt_kayit(id, isim):
    imlec.execute("Insert Or Ignore Into vt_kayit VALUES (?, ?)", (int(id), str(isim),))
    baglanti.commit()

def veri_al():
    imlec.execute("Select * From vt")
    veri = imlec.fetchall()
    for i in veri:
        gelenKisiler.append(i)

def kayitli_kisiler():
    imlec.execute("Select * From vt_kayit")
    veri = imlec.fetchall()
    for i in veri:
        kayitliKisiler.append(i)

def yuztanima():
    cap = cv2.VideoCapture(0)
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
            matches = face_recognition.compare_faces(faces_encoded, face_encoding,tolerance=0.45)
            name = "Taninmiyor"
            giris = "Giris Onaylandi"
            face_distances = face_recognition.face_distance(faces_encoded, face_encoding)
            best_match_index = np.argmin(face_distances)
            
            if matches[best_match_index]:
                name = known_face_names[best_match_index]
                face_names.append(name)
                        
                for (top, right, bottom, left), name in zip(face_locations, face_names):
                        cv2.rectangle(image_np, (left-20, top-20), (right+20, bottom+20), (255, 0, 0), 2)
                        cv2.rectangle(image_np, (left-20, bottom -15), (right+20, bottom+20), (255, 0, 0), cv2.FILLED)
                        font = cv2.FONT_HERSHEY_DUPLEX
                        cv2.putText(image_np, name, (left -20, bottom +15), font, 1.0, (255, 255, 255), 2)
                        cv2.putText(image_np, giris, (left -20, bottom  -60), font, 1.0, (255, 255, 255), 2)
                        if name in gelenKisiler:
                             continue
                        else:
                            veri_ekle(isim=name, zaman=time.strftime("%m/%d/%Y, %H:%M:%S", time.localtime()))

        cv2.imshow('Video', image_np)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break

def KisileriGetir():
    i = 0
    for i in range(len(gelenKisiler)):
        listBox.insert(i, gelenKisiler[i])
        i = i + 1

def kayitli_kisileri_getir():
    i = 0
    for i in range(len(kayitliKisiler)):
        listBox1.insert(i, kayitliKisiler[i])
        i = i + 1

def KisiKaydet():
    cap = cv2.VideoCapture(0)
    while True:
        ret, save_photo = cap.read()
        value = entry.get()
        ek = ".jpg"
        id = int(entry2.get())
        bilgi = " Kayıt için k tuşuna basın"

        vt_kayit(id, isim=value)

        cv2.imshow('Video', save_photo)
        if cv2.waitKey(1) & 0xFF == ord('k'):
            cv2.imwrite("./faces/"+value+ek, save_photo)
            cv2.destroyAllWindows()
            break

def get_encoded_faces():
                encoded = {}
                for dirpath, dnames, fnames in os.walk("./faces"):
                    for f in fnames:
                        if f.endswith(".jpg") or f.endswith(".png") or f.endswith(".jpeg"):
                            face = face_recognition.load_image_file("faces/" + f)
                            encoding = face_recognition.face_encodings(face)[0]
                            encoded[f.split(".")[0]] = encoding
                with open('dataset_faces.dat', 'wb') as f:
                     pickle.dump(encoded, f)
                
                message_box=messagebox.showinfo(title = "info", message = "Kişi Kaydedildi")
                print(message_box)
                return encoded



pw = ttk.Panedwindow(window, orient = tk.HORIZONTAL)
pw.pack(fill = tk.BOTH, expand = True)

m2 = ttk.Panedwindow(pw, orient = tk. VERTICAL)

frame2 = ttk.Frame(pw, width = 400, height = 340, relief = tk.RIDGE)
frame3 = ttk.Frame(pw, width = 620, height = 300, relief = tk.RAISED)
m2.add(frame2)
m2.add(frame3)

frame1 = ttk.Frame(pw, width = 460, height = 640, relief = tk.GROOVE)
pw.add(m2)
pw.add(frame1)

label1 = tk.Label(frame2, text = "Fotoğraf Çekmek için kamera açılınca 'k' tuşuna basın!")
label1.place(x = 35, y = 90)

label2 = tk.Label(frame2, text = "Kişi Adı: ")
label2.place(x = 5, y = 120)

label4 = tk.Label(frame2, text = "Id: ")
label4.place(x = 5, y = 150)

entry = tk.Entry(frame2, width = 35)
entry.insert(string = "",index = 0)
entry.place(x=70, y=120)

entry2 = tk.Entry(frame2, width = 35)
entry2.insert(string = "",index = 0)
entry2.place(x=70, y=150)

button1=tk.Button(frame2, text="Fotoğraf Çek", command=KisiKaydet, width=20, height=3)
button1.place(x=350, y=100)

button3=tk.Button(frame2, text="Kişiyi Kaydet", command=get_encoded_faces, width=20, height=3)
button3.place(x=350, y=170)

button2=tk.Button(frame3, text="Kişi Tanımayı Aç", command=yuztanima, width=30, height=6)
button2.place(x=200, y=100)

button3=tk.Button(frame1, text="Gelen Kişiler", command=KisileriGetir, width=20, height=3)
button3.place(x=70, y=20)

button4=tk.Button(frame1, text="Sistemde Kayıtlı Kişiler", command=kayitli_kisileri_getir, width=20, height=3)
button4.place(x=380, y=20)

listBox = tk.Listbox(frame1, selectmode = tk.MULTIPLE, command=veri_al(), height=25, width=50)
listBox.place(x = 30, y = 120)

listBox1 = tk.Listbox(frame1, selectmode = tk.MULTIPLE, command=kayitli_kisiler(), height = 25, width = 30)
listBox1.place(x = 360, y = 120)

window.mainloop()
