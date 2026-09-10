import tkinter as tk
import subprocess
import sys
import os

BASE_DIR = os.path.dirname(__file__)

def run_us():
    root.destroy()
    subprocess.Popen([sys.executable, os.path.join(BASE_DIR, "realtime_asl.py")])

def run_india():
    root.destroy()
    subprocess.Popen([sys.executable, os.path.join(BASE_DIR, "realtime_isl.py")])

root = tk.Tk()
root.title("Sign Language Translator")
root.geometry("500x300")
root.configure(bg="#f0f0f0")

label = tk.Label(root, text="Select Sign Language Version", font=("Arial", 16), bg="#f0f0f0")
label.pack(pady=20)

tk.Button(
    root,
    text="🇺🇸 US Version (ASL)",
    width=25,
    font=("Arial", 12),
    command=run_us
).pack(pady=10)

tk.Button(
    root,
    text="🇮🇳 Indian Version (ISL)",
    width=25,
    font=("Arial", 12),
    command=run_india
).pack(pady=10)

tk.Button(
    root,
    text="Exit",
    width=25,
    command=root.destroy
).pack(pady=10)

root.mainloop()
