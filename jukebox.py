#!/bin/python3

from os import listdir, get_terminal_size, mkdir, path, system, remove
from sys import argv
from threading import Thread
from random import sample, choice
from time import sleep
# horrible code warning! next 30 lines
musicDir = "songs"
for arg in argv:
    if arg[0] == "-":
        if "r" in arg:
            remove("settings.conf")
if not(path.exists("settings.conf")):
    settings = open("settings.conf", "w")
    settings.write("default-mode=" + input("preferred interface (gui/cli):\n") + "\n")
    settings.write("music-dir=" + input("Path to the music folder\n> ") + "\n")
    settings.close()

settings = open("settings.conf")
conf = settings.read()
for line in conf.split("\n"):
    option, value = line.split("=")
    if "default-mode" in option:
        if "gui" in value:
            cliMode = False
    if "default-mode" in option:
        if "cli" in value:
            cliMode = True
    if "music-dir" in option:
        musicDir = value

for arg in argv:
    if arg[0] == "-":
        if "c" in arg:
            cliMode = True
        if "g" in arg:
            cliMode = False

repeating = False
moduleLoaderFail = False
if cliMode:
    print("cli mode")
else:
    print("gui mode")
    try:
        import tkinter as tk
        from tkinter import ttk, Menu
    except:
        print("tkinter not installed, required for use as a gui application")
        moduleLoaderFail = True
    try:
        from mutagen.mp3 import MP3
    except:
        print("mutagen not installed, required for use as a gui application")
        exit()
try:
    from pygame import mixer
except:
    print("pygame not installed, please install it")
    moduleLoaderFail = True
if moduleLoaderFail:
    exit()

if(not(path.exists(musicDir))):
    print("please make sure that you specified the proper path to the music directory. use -r to reset your configuration file")
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
    songs = listdir(musicDir)
    songs.sort()
    print(len(songs), "songs loaded")

def refreshPlaylist():
    if not(cliMode):
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
    refreshPlaylist()

def formatTime(time): # returns string
	m = int(time/60)
	s = int(time%60)
	if s < 10:
		s = f"0{s}"
	return(f"{m}:{s}")

def player(): # goes through the queue and plays each song until the queue is empty, removing songs once finished
    global queue
    global playerRunning
    global currentsong
    global songLength
    playerRunning = True
    while(not(queue == [])):
        currentsong = queue[0]
        try:
            mixer.music.load(musicDir + "/" + currentsong)
            mixer.music.play()
            if not(cliMode):
                songLength = MP3(musicDir + "/" + currentsong)
                songLength = songLength.info.length
                window.title("spotifyn't|" + currentsong)
        except:
            print("error while attempting to play",currentsong)
        if cliMode:
            while(mixer.music.get_busy() or paused):
                sleep(.25)
        else:
            while(mixer.music.get_busy() or paused):
                update_progress()
                sleep(.5)
        if not(queue == []) and queue[0] == currentsong and not(repeating):
            queue.remove(queue[0])
        if shuffling and queue == []:
            queue.append(choice(songs))
        if not(cliMode):
            refreshPlaylist()
    if not(cliMode):
        window.title("spotifyn't")
        update_progress()
        refreshPlaylist()
    playerRunning = False

def startPlayer():
    global playerThread
    if(not(playerRunning)):
        playerThread = Thread(target=player)
        playerThread.start()

def update_progress():
    if playerRunning:
        progress_value = int(mixer.music.get_pos()/1000)
        progress['value'] = progress_value/songLength*100
        timeThingy['text'] = formatTime(progress_value) + "/" + formatTime(songLength)
    else:
        progress['value'] = 0

def truncateWidth(string):
    global terminalWidth
    if len(string) > terminalWidth:
        return(string[:terminalWidth-2] + " >")
    else:
        return(string)

def skip(ID=1):
    if len(queue) > 0:
        queue.pop(ID-1)
    if ID == 1:
        mixer.music.stop()
    if not(cliMode):
        refreshPlaylist()

def restart():
    mixer.music.set_pos(0)

def randomSongs(number=1):
    global queue
    if number > len(songs):
        number = len(songs)
    queue += sample(songs, number)
    startPlayer()
    if not(cliMode):
        refreshPlaylist()

def GUIsearch(arg="none"):
    query = search_entry.get()
    searchResults.delete(0,'end')
    if not(query == ""):
        for match in songs:
            if query.lower() in match.lower():
                searchResults.insert('end',match)

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
        if(not(cliMode)):
            shuffleButton.configure(image=shuffleEnabledIMG)
    else:
        shuffling = False
        print("shuffling disabled")
        if(not(cliMode)):
            shuffleButton.configure(image=shuffleIMG)
    lessLines = 2
    refreshPlaylist()

def repeat(command=""):
    global repeating
    global lessLines
    if repeating == False and not(command == "stop"):
        repeating = True
        print("repeat enabled")
        if(not(cliMode)):
            repeatButton.configure(image=repeatEnabledIMG)
    else:
        repeating = False
        print("repeat disabled")
        if(not(cliMode)):
            repeatButton.configure(image=repeatIMG)
    lessLines = 1

def togglePause():
    global paused
    if not(paused):
        mixer.music.pause()
        print("playback paused")
        paused = True
        if(not(cliMode)):
            pauseButton.configure(image=playIMG)
    else:
        mixer.music.unpause()
        print("playback resumed")
        paused = False
        if(not(cliMode)):
            pauseButton.configure(image=pauseIMG)

def addSong(event="lol"):
    if searchResults.size() > 0:
        queue.append(searchResults.get(searchResults.curselection()))
        startPlayer()
        refreshPlaylist()

def GUIskip(event="don't even ask"):
    if playlist.size() > 0:
        skip(playlist.curselection()[0] + 1)

loadsongs()
if(not(cliMode)): #make the window
    window = tk.Tk()
    playlistControl = tk.Frame(window)
    searchControl = tk.Frame(window)
    # create the two lists
    playlist = tk.Listbox(playlistControl)
    playlist.pack(fill="both",expand=True)

    # create the search pane
    search_entry = tk.Entry(searchControl)
    searchResults = tk.Listbox(searchControl)
    search_entry.pack(fill="x")
    searchResults.pack(fill="both",expand=True)
    search_entry.bind("<KeyRelease>", GUIsearch)

    # create the time thingy (don't know the right name)
    timeThingy = tk.Label(playlistControl, text="0:00/0:00")
    timeThingy.pack(fill="x")

    # create the progress bar
    progress = ttk.Progressbar(playlistControl, mode="determinate")
    progress.pack(fill="x")

    # define images for buttons
    playIMG = tk.PhotoImage(file="assets/play.png")
    pauseIMG = tk.PhotoImage(file="assets/pause.png")
    restartIMG = tk.PhotoImage(file="assets/restart.png")
    skipIMG = tk.PhotoImage(file="assets/skip.png")
    shuffleIMG = tk.PhotoImage(file="assets/shuffle.png")
    shuffleEnabledIMG = tk.PhotoImage(file="assets/shuffle enabled.png")
    repeatIMG = tk.PhotoImage(file="assets/repeat.png")
    repeatEnabledIMG = tk.PhotoImage(file="assets/repeat enabled.png")
    clearIMG = tk.PhotoImage(file="assets/clear.png")
    # create the buttons
    buttons = tk.Frame(playlistControl)
    pauseButton = tk.Button(buttons, image=pauseIMG, command=togglePause)
    restartButton = tk.Button(buttons, image=restartIMG, command=restart)
    skipButton = tk.Button(buttons, image=skipIMG, command=skip)
    shuffleButton = tk.Button(buttons, image=shuffleIMG, command=shuffle)
    repeatButton = tk.Button(buttons, image=repeatIMG, command=repeat)
    clearButton = tk.Button(buttons, image=clearIMG, command=clear)
    #pack buttons
    pauseButton.pack(side="left")
    restartButton.pack(side="left")
    skipButton.pack(side="left")
    shuffleButton.pack(side="left")
    repeatButton.pack(side="left")
    clearButton.pack(side="left")
    buttons.pack(fill="x")

    playlistControl.pack(side="left", fill="both",expand=True)
    searchControl.pack(side="right", fill="both",expand=True)
    playlistControl.pack_propagate(False)
    searchControl.pack_propagate(False)
    searchResults.bind("<<ListboxSelect>>", addSong)
    playlist.bind("<<ListboxSelect>>", GUIskip)

    window.title("spotifyn't")
    logo = tk.PhotoImage(file="assets/icon.png")
    window.iconphoto(True, logo)
    window.geometry("500x300")

    #menu stuff
    menubar = Menu(window)
    window.config(menu=menubar)

    file_menu = Menu(menubar, tearoff=False)
    file_menu.add_command(label='Exit', command=window.destroy)
    file_menu.add_command(label='Reload songs', command=loadsongs)
    menubar.add_cascade(label="File", menu=file_menu)

    random_menu = Menu(menubar, tearoff=False)
    # tried to DRY this out, but it didn't work. don't touch.
    random_menu.add_command(label='1', command=lambda: randomSongs(1))
    random_menu.add_command(label='5', command=lambda: randomSongs(5))
    random_menu.add_command(label='10', command=lambda: randomSongs(10))
    random_menu.add_command(label='20', command=lambda: randomSongs(20))
    random_menu.add_command(label='50', command=lambda: randomSongs(50))
    menubar.add_cascade(label="Random", menu=random_menu)

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
                randomSongs(number)
                lessLines = 0
            elif(query[:7] == "/volume"): # DON'T USE pygame mixer volume
                if(query == "/volume"):
                    print("volume: " + str(int(mixer.music.get_volume()*100)) + "%")
                    lessLines = 1
                else:
                    try:
                        mixer.music.set_volume(int(query[7:])/100)
                        print("volume: " + str(int(mixer.music.get_volume()*100)) + "%")
                        lessLines = 2
                    except:
                        print("volume must be a number between 0 and 100")
                        lessLines = 1
            elif(query == "/clear"):
                clear()
                lessLines = 1
                print("queue cleared")
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
            elif query[:7] == "/repeat":
                repeat(query[8:])
            elif query == "/restart":
                restart()
            elif(query == "/help"):
                print("/exit or /quit: clear queue and exit")
                print("/pause: pause or unpause the song")
                print("/play: unpause the current song")
                print("/restart: restart the current song")
                print("/skip <number>: skips current song, or the specified song in the queue")
                print("/random <number>: adds one or more random songs")
                print("/repeat: toggle repeating the current song")
                print("/shuffle (stop): enables/disables shuffling")
                print("/clear: clear all songs except for the song currently playing")
                print("/volume <0 - 100>: sets volume, use system volume instead")
                print("/list: list all available songs")
                print("/reload: reloads all songs")
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
                    if selection != "":
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

#after exiting
if shuffling:
    shuffling = False

if(not(queue == [])):
    print("clearing", len(queue), "items from queue")
    queue = []

if(playerRunning):
    print("waiting for player to finish")
    skip()