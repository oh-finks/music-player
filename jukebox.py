#!/bin/python3

# have fun trying to read my code, there are like 3 useful comments
from os import listdir, get_terminal_size, mkdir, path, system
from threading import Thread
from random import sample, choice
from time import sleep
print("add these for the gui bit ⏹⏯⏭")
print("loading pygame")
try:
    from pygame import mixer
except:
    print("pygame not installed, installing")
    system("pip3 install pygame")
    from pygame import mixer
if(not(path.exists("songs"))):
    mkdir("songs")
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

def blankLines(lines):
    print("\n"*(lines - 1))

def player(): # goes through the queue and plays each song until the queue is empty, removing songs once finished
    global queue
    global playerRunning
    global currentsong
    playerRunning = True
    while(not(queue == [])):
        currentsong = queue[0]
        try:
            mixer.music.load("songs/" + currentsong)
            mixer.music.play()
        except:
            print("error while attempting to play",currentsong)
        while(mixer.music.get_busy() or paused):
            sleep(.25)
        if(not(queue == [])):
            if(queue[0] == currentsong):
                queue.remove(queue[0])
        if shuffling and queue == []:
            queue.append(choice(songs))
    playerRunning = False

def startPlayer():
    global playerThread
    if(not(playerRunning)):
        playerThread = Thread(target=player)
        playerThread.start()

def truncateWidth(string):
    global terminalWidth
    if len(string) > terminalWidth:
        return(string[:terminalWidth-1] + ">")
    else:
        return(string)

def skip(ID):
    if len(queue) == 1 and shuffling:
        queue.append(choice(songs))
    queue.remove(queue[ID-1])
    if ID == 1:
        mixer.music.stop()

def shuffle(command):
    global shuffling
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

loadsongs()
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
                skip(1)
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
            if(query == "/random"):
                queue.append(choice(songs))
                lessLines = 0
            else:
                try:
                    for song in sample(songs, int(query[7:])):
                        queue.append(song)
                        lessLines = 0
                except:
                    print("usage: /random <number of songs>")
                    lessLines = 1
        elif(query[:7] == "/volume"):
            if(query == "/volume"):
                print("volume: ", int(mixer.music.get_volume()*100), "%")
                lessLines = 1
            else:
                try:
                    mixer.music.set_volume(int(query[7:])/100)
                except:
                    print("error message, temporary")
                    lessLines = 1
        elif(query == "/clear"):
            if(len(queue) == 0):
                print("cannot skip, queue is already empty")
                lessLines = 1
            elif(len(queue) == 1):
                print("only one song in queue")
                lessLines = 1
            else:
                queue = [queue[0]]
                lessLines = 0
        elif(query == "/pause"):
            if not(paused):
                mixer.music.pause()
                print("playback paused")
                paused = True
            else:
                mixer.music.unpause()
                print("playback resumed")
                paused = False
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
