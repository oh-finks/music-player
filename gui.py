#!/bin/python3
import tkinter as tk
from tkinter import ttk
from os import listdir
songs = listdir("/home/oh_finks/Music/4K YouTube to MP3")
songs.sort()
paused = False
def search(event="this code sucks"):
    results = []
    query = search_entry.get()
    for i in songs:
        if query.lower() in i.lower():
            results.append(i)
    searchResults.delete(0,'end')
    for i in results:
        searchResults.insert('end',i)
def play_pause():
    global paused
    if paused:
        play_pause.configure(text="⏵")
    else:
        play_pause.configure(text="⏸")
    paused = not(paused)
def skip():
    # Implement functionality for button b here
    print("skip")
def shuffle():
    # Implement functionality for button c here
    print("shuffle")
def clear():
    print("clear")
    # Implement functionality for button d here
    pass
def addSong(event="lol"):
    playlist.insert('end', searchResults.get(searchResults.curselection()))
window = tk.Tk()
test = ["song1", "song2"]

playlistControl = tk.Frame(window)
searchControl = tk.Frame(window)
# Create the two lists
playlist = tk.Listbox(playlistControl)
playlist.pack(fill="both",expand=True)
searchResults = tk.Listbox(searchControl)
searchResults.pack(fill="both",expand=True)

# Create the search bar
search_entry = tk.Entry(searchControl)
search_button = tk.Button(searchControl, text="Search", command=search)
search_entry.pack(fill="x")
search_entry.bind("<Return>", search)
search_button.pack(fill="x")

# Create the progress bar
progress = ttk.Progressbar(playlistControl, mode="indeterminate")
progress.pack(fill="x")

# Create the buttons
buttons = tk.Frame(playlistControl)
play_pause = tk.Button(buttons, text="⏯", command=play_pause)
skip = tk.Button(buttons, text="⏭", command=skip)
shuffle = tk.Button(buttons, text="shuffle", command=shuffle)
clear = tk.Button(buttons, text="clear", command=clear)
play_pause.pack(side="left", fill="x", expand=True)
skip.pack(side="left", fill="x", expand=True)
shuffle.pack(side="left", fill="x", expand=True)
clear.pack(side="left", fill="x", expand=True)
buttons.pack(fill="x")

playlistControl.pack(side="left", fill="both",expand=True)
searchControl.pack(side="right", fill="both",expand=True)
searchResults.bind("<<ListboxSelect>>", addSong)
window.mainloop()
