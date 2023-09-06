#!/bin/python3

from os import listdir, get_terminal_size, mkdir, path, system
from sys import argv
from threading import Thread
from random import sample, choice
from time import sleep
cliMode = False
for arg in argv:
    if arg == "-c":
        cliMode = True

moduleLoaderFail = False
if cliMode:
    print("cli mode")
else:
    print("gui mode")
    try:
        import tkinter as tk
        from tkinter import ttk
    except:
        print("tkinter not installed, if you would like to use this program as a cli application please specify -c")
        moduleLoaderFail = True
    try:
        from mutagen.mp3 import MP3
    except:
        print("mutagen not installed, please install it")
        exit()
try:
    from pygame import mixer
except:
    print("pygame not installed, please install it")
    moduleLoaderFail = True
if moduleLoaderFail:
    exit()

if(not(path.exists("songs"))):
    print("please create a directory named 'songs' in the current directory, or symlink an already existing music folder")
    exit()
mixer.init()
mixer.music.set_volume(100)
playerRunning = False
paused = False
currentsong = "none"
shuffling = False
queue = []

def loadsongs():
    global songs
    songs = listdir("songs")
    songs.sort()
    print(len(songs), "songs loaded")

def refreshPlaylist():
    global playlist
    global queue
    playlist.delete(0,'end')
    for song in queue:
        playlist.insert('end',song)

def blankLines(lines):
    if lines > 0:
        print("\n"*(lines - 1))

def clear():
    global queue
    if(len(queue) == 0):
        print("cannot clear, queue is already empty")
        lessLines = 1
    elif(len(queue) == 1):
        print("only one song in queue")
        lessLines = 1
    else:
        queue = [queue[0]]
        lessLines = 0
    if not(cliMode):
        refreshPlaylist()

def player(): # goes through the queue and plays each song until the queue is empty, removing songs once finished
    global queue
    global playerRunning
    global currentsong
    global songLength
    playerRunning = True
    while(not(queue == [])):
        currentsong = queue[0]
        try:
            mixer.music.load("songs/" + currentsong)
            mixer.music.play()
            if not(cliMode):
                songLength = MP3("songs/" + currentsong)
                songLength = songLength.info.length
        except:
            print("error while attempting to play",currentsong)
        if cliMode:
            while(mixer.music.get_busy() or paused):
                sleep(.25)
        else:
            while(mixer.music.get_busy() or paused):
                update_progress()
                sleep(.5)
        if not(queue == []) and queue[0] == currentsong:
            queue.remove(queue[0])
        if shuffling and queue == []:
            queue.append(choice(songs))
        if not(cliMode):
            refreshPlaylist()
    playerRunning = False

def startPlayer():
    global playerThread
    if(not(playerRunning)):
        playerThread = Thread(target=player)
        playerThread.start()

def update_progress():
    progress_value = int(mixer.music.get_pos()/1000)  # Example value, replace with your changing variable
    progress['value'] = progress_value/songLength*100

def truncateWidth(string):
    global terminalWidth
    if len(string) > terminalWidth:
        return(string[:terminalWidth-2] + " >")
    else:
        return(string)

def skip(ID=1):
    if len(queue) == 1 and shuffling:
        queue.append(choice(songs))
    queue.remove(queue[ID-1])
    if ID == 1:
        mixer.music.stop()

def randomSongs(number=1):
    queue += sample(songs, number)

def GUIsearch(arg="none"):
    results = []
    query = search_entry.get()
    for i in songs:
        if query.lower() in i.lower():
            results.append(i)
    searchResults.delete(0,'end')
    for i in results:
        searchResults.insert('end',i)

def shuffle(command=""):
    global shuffling
    global lessLines
    if shuffling == False and not(command == "stop"):
        shuffling = True
        if queue == []:
            queue.append(choice(songs))
        if not(playerRunning):
            startPlayer()
        print("shuffling enabled")
    else:
        shuffling = False
        print("shuffling disabled")
    lessLines = 1
    refreshPlaylist()

def togglePause():
    global paused
    if not(paused):
        mixer.music.pause()
        print("playback paused")
        paused = True
        if(not(cliMode)):
            pauseButton.configure(text="⏵")
    else:
        mixer.music.unpause()
        print("playback resumed")
        paused = False
        if(not(cliMode)):
            pauseButton.configure(text="⏸")

def addSong(event="lol"):
    queue.append(searchResults.get(searchResults.curselection()))
    startPlayer()
    refreshPlaylist()

loadsongs()

if(not(cliMode)): #make the window
    window = tk.Tk()
    playlistControl = tk.Frame(window)
    searchControl = tk.Frame(window)
    # Create the two lists
    playlist = tk.Listbox(playlistControl)
    playlist.pack(fill="both",expand=True)
    searchResults = tk.Listbox(searchControl)
    searchResults.pack(fill="both",expand=True)

    # Create the search bar
    search_entry = tk.Entry(searchControl)
    search_button = tk.Button(searchControl, text="Search", command=GUIsearch)
    search_entry.pack(fill="x")
    search_entry.bind("<Return>", GUIsearch)
    search_button.pack(fill="x")

    # Create the progress bar
    progress = ttk.Progressbar(playlistControl, mode="determinate", length=10)
    progress.pack(fill="x")

    # Create the buttons
    buttons = tk.Frame(playlistControl)
    pauseButton = tk.Button(buttons, text="⏯", command=togglePause)
    skip = tk.Button(buttons, text="⏭", command=skip)
    shuffleButton = tk.Button(buttons, text="shuffle", command=shuffle)
    clear = tk.Button(buttons, text="clear", command=clear)
    pauseButton.pack(side="left")
    skip.pack(side="left")
    shuffleButton.pack(side="left")
    clear.pack(side="left")
    buttons.pack(fill="x")

    playlistControl.pack(side="left", fill="both",expand=True)
    searchControl.pack(side="right", fill="both",expand=True)
    searchResults.bind("<<ListboxSelect>>", addSong)

    window.mainloop()

else:
    print("queue is empty")
    lessLines = 1
    terminalWidth, terminalHeight = get_terminal_size()
    blankLines(terminalHeight - 2 - lessLines)
    while True: # I think there's a better way, but i don't care
        query = input("use command or search for a song: ")
        if(query[:1] == "/"): # if it's a command
            if(query == "/exit" or query == "/quit"):
                break
            elif(query == "/list"):
                for number, song in enumerate(songs):
                    print(number + 1, song)
                lessLines = len(songs)
            elif(query[:5] == "/skip"):
                if(query == "/skip"):
                    skip()
                    lessLines = 0
                else:
                    try:
                        skip(int(query[5:]))
                        lessLines = 0
                    except:
                        print("usage: /skip <number of song to skip>")
                        lessLines = 1
            elif(query == "/reload"):
                loadsongs()
                lessLines = 1
            elif(query[:7] == "/random"):
                if query == "/random":
                    number = 1
                else:
                    try:
                        number = int(query[7:])
                    except:
                        print("usage: /random <number of songs>")
                        lessLines = 1
            elif(query[:7] == "/volume"):
                if(query == "/volume"):
                    print("volume: " + str(int(mixer.music.get_volume()*100)) + "%")
                    lessLines = 1
                else:
                    try:
                        mixer.music.set_volume(int(query[7:])/100)
                        print("volume: " + str(int(mixer.music.get_volume()*100)) + "%")
                        print("I hate pygame mixer volume control, just don't use it")
                        lessLines = 2
                    except:
                        print("volume must be a number between 0 and 100")
                        lessLines = 1
            elif(query == "/clear"):
                clear()
            elif(query == "/pause"):
                togglePause()
                lessLines = 1
            elif(query == "/play"):
                mixer.music.unpause()
                print("playback resumed")
                paused = False
                lessLines = 1
            elif query[:8] == "/shuffle":
                shuffle(query[9:])
            elif(query == "/help"):
                print("/exit or /quit: clear queue and exit")
                print("/list: list all available songs")
                print("/reload: reloads all songs")
                print("/skip <number>: skips current song, or the specified song in the queue")
                print("/random <number>: adds one or more random songs")
                print("/clear: clear all songs except for the song currently playing")
                print("/volume <0 - 100>: sets volume, use system volume instead")
                print("/help: display this help message")
                lessLines = 8
            else:
                print('unknown command "' + str(query[1:]) + '"')
                lessLines = 1
        else: # if it's not a command, search for it
            numFoundSongs = 0
            matchingsongs = []
            for song in songs: # checks for matching songs and adds them to the list
                if query.lower() in song.lower():
                    numFoundSongs += 1
                    matchingsongs.append(song)
            if numFoundSongs > 0:
                lessLines = 0
                print(numFoundSongs, 'songs found matching query "' + query + '":\n')
                for num, song in enumerate(matchingsongs):
                    print(truncateWidth(str(num + 1) + " " + song))
                print("\n0 add all")
                terminalWidth, terminalHeight = get_terminal_size()
                blankLines(terminalHeight - numFoundSongs - 3)
                selection = input("select a song by the number shown: ")
                try: #makes sure it's a number
                    selection = int(selection)
                    if(selection > 0 and selection <= numFoundSongs):
                        queue.append(matchingsongs[selection-1])
                    elif selection == 0:
                        queue += matchingsongs
                    else:
                        print("💀")
                        lessLines = 1
                except: #if it's not a number
                    print("💀")
                    lessLines = 1
            else:
                print('no songs found matching query "' + query + '"')
                lessLines = 1
            # end of the search part
        terminalWidth, terminalHeight = get_terminal_size()
        if(queue == []):
            print("queue is empty")
        else:
            startPlayer()
            print("queue:")
            for number, song in enumerate(queue):
                print(truncateWidth(str(number + 1) + " " + song))
        blankLines(terminalHeight - len(queue) - 2 - lessLines)

#after /exit command
if shuffling:
    shuffling = False

if(not(queue == [])):
    print("clearing", len(queue), "items from queue")
    queue = []

if (playerRunning):
    print("waiting for player to finish")
    mixer.music.stop()
    paused = False
    playerThread.join()
