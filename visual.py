# Tkinter image help from https://stackoverflow.com/questions/10133856/how-to-add-an-image-in-tkinter
import tkinter as tk
from PIL import Image, ImageTk
import os

root = tk.Tk()
label = tk.Label(root, text="C# Transcript Software").grid(row=0, column=0)

entry = tk.Entry(root).grid(row=1, column=0)
button = tk.Button(root, text="Transcribe!").grid(row=2, column=0)

img = tk.PhotoImage(file="music_note.png")
img = img.subsample(16, 16) # scale down the image by a factor of 2
panel = tk.Label(root, image=img).grid(row=3, column=0)

canvas = tk.Canvas(root, width=400, height=300).grid(row=4, column=0)

root.mainloop()