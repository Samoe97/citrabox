# # # # CERBERUS - THE INFERNAL THREE-HEADED WATCHDOG OF CITRABOX # # # #
#                                                                       #
#                    Watchdog Module for CitraBox v3                    #
#                                                                       #
#               Author: John Sam Fuchs - www.samoe.me/code              #
#                                                                       #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

import atexit
import time
import os
from DPGToolbox import Renamer
import AutoBox

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
 
import tkinter
from PIL import Image, ImageTk

import threading

# --------------------------------------------------------------------- #

def shutDownCerberus() :
    print('SHUTTING DOWN')
    for i in itemArray :
        i.stopWatcher()

# --------------------------------------------------------------------- #

def toggleCerberus() :
    global cerberusStatus
    if cerberusStatus == True:
        for i in itemArray :
            i.stopWatcher()
        cerberusStatus = False
        cerberusStatusVar.set('Cerberus is offline.')
        logoLabel.config(image = Icon_Logo_Red)
        AutoBox.stopAutoBox()
    else :
        for i in itemArray :
            i.startWatcher()
        cerberusStatus = True
        cerberusStatusVar.set('Cerberus is online.')
        logoLabel.config(image = Icon_Logo_Green)
        AutoBox.startAutoBox()

# --------------------------------------------------------------------- #

if __name__ == '__main__' :

    # try:

        # INITIALIZE VARIABLES
        global cerberusStatus
        cerberusStatus = False

        global itemArray
        itemArray = []

        blueBG = '#3D4855'
        orange = '#E79F6D'
        white = '#FFFFFF'
        green = '#2D945E'
        red = '#8D3F40'

        # INITIALIZE GUI
        root = tkinter.Tk()
        rootFrame = tkinter.Frame(root, bg = blueBG)
        contentFrame = tkinter.Frame(rootFrame, bg = blueBG)

        root.configure(bg = blueBG, borderwidth=0)

        root.iconbitmap('L:/Scripting/ALFRD/assets/cerberus/cerberus_logo_icon.ico')
        root.title('Cerberus - Infernal Three-Headed Watchdog for CitraBox')

        # GUI ASSETS
        fontStatus = tkinter.font.Font(family = 'Avenir', size = 14)
        fontDirectory = tkinter.font.Font(family = 'Avenir Light', size = 12)

        Icon_On_Path = 'L:/Scripting/ALFRD/assets/cerberus/cerberus_On.png'
        Icon_On_Img = Image.open(Icon_On_Path)
        Icon_On = ImageTk.PhotoImage(Icon_On_Img)

        Icon_Update_Path = 'L:/Scripting/ALFRD/assets/cerberus/cerberus_Update.png'
        Icon_Update_Img = Image.open(Icon_Update_Path)
        Icon_Update = ImageTk.PhotoImage(Icon_Update_Img)

        Icon_Folder_Path = 'L:/Scripting/ALFRD/assets/cerberus/cerberus_Folder.png'
        Icon_Folder_Img = Image.open(Icon_Folder_Path)
        Icon_Folder = ImageTk.PhotoImage(Icon_Folder_Img)

        Icon_Logo_Red_Path = 'L:/Scripting/ALFRD/assets/cerberus/cerberus_Logo_Red.png'
        Icon_Logo_Red_Img = Image.open(Icon_Logo_Red_Path)
        Icon_Logo_Red = ImageTk.PhotoImage(Icon_Logo_Red_Img)

        Icon_Logo_Green_Path = 'L:/Scripting/ALFRD/assets/cerberus/cerberus_Logo_Green.png'
        Icon_Logo_Green_Img = Image.open(Icon_Logo_Green_Path)
        Icon_Logo_Green = ImageTk.PhotoImage(Icon_Logo_Green_Img)

        Icon_Sticker_Path = 'L:/Scripting/ALFRD/assets/cerberus/cerberus_Sticker.png'
        Icon_Sticker_Img = Image.open(Icon_Sticker_Path)
        Icon_Sticker = ImageTk.PhotoImage(Icon_Sticker_Img)

        Icon_Tile_Path = 'L:/Scripting/ALFRD/assets/cerberus/cerberus_Tile.png'
        Icon_Tile_Img = Image.open(Icon_Tile_Path)
        Icon_Tile = ImageTk.PhotoImage(Icon_Tile_Img)

        Icon_Cap_Path = 'L:/Scripting/ALFRD/assets/cerberus/cerberus_Cap.png'
        Icon_Cap_Img = Image.open(Icon_Cap_Path)
        Icon_Cap = ImageTk.PhotoImage(Icon_Cap_Img)

        Icon_Metal_Path = 'L:/Scripting/ALFRD/assets/cerberus/cerberus_Metal.png'
        Icon_Metal_Img = Image.open(Icon_Metal_Path)
        Icon_Metal = ImageTk.PhotoImage(Icon_Metal_Img)


        # --------------------------------------------------------------------- #

        global cerberusStatusVar
        cerberusStatusVar = tkinter.StringVar()
        cerberusStatusVar.set('Cerberus is offline.')

        headerFrame = tkinter.Frame(contentFrame, bg = blueBG)

        logoLabel = tkinter.Label(headerFrame, image = Icon_Logo_Red, bg = blueBG)
        logoLabel.pack(side = 'left')

        statusLabel = tkinter.Label(headerFrame, textvariable = cerberusStatusVar)
        statusLabel.configure(font = fontStatus, fg = white, bg = blueBG)
        statusLabel.pack(side = 'left', anchor = 'w', padx = 8)

        spacerHeader = tkinter.Frame(headerFrame, width = 432, bg = blueBG)
        spacerHeader.pack(side = 'left', anchor = 'nw')

        buttonPower = tkinter.Button(headerFrame, image = Icon_On, bg = blueBG, relief = 'flat')
        buttonPower.pack(side = 'right', anchor = 'ne')
        buttonPower.config(command = toggleCerberus)

        # buttonPower = tkinter.Button(headerFrame, image = Icon_On, bg = blueBG, relief = 'flat')

        headerFrame.grid(row = 0, pady = 8)

        # --------------------------------------------------------------------- #

        middleFrame = tkinter.Frame(contentFrame, bg = blueBG)

        middleFrame.grid(row = 1)

        # --------------------------------------------------------------------- #

        # footerFrame = tkinter.Frame(contentFrame, bg = blueBG)

        # footerFrame.grid(row = 2)

        # --------------------------------------------------------------------- #

        contentFrame.pack(padx = 16, pady = 16)
        rootFrame.pack()
    
    # except:
        # shutDownCerberus()

# --------------------------------------------------------------------- #

class CerberusDirectory():

    def __init__(self, masterFrame, directory, id) :

        self.directoryVar = tkinter.StringVar()
        self.directoryVar.set(directory)

        self.directory = directory

        self.id = id

        self.frame = tkinter.Frame(masterFrame, bg = blueBG)

        if id == 'Stickers' :
            buttonStickers = tkinter.Button(self.frame, image = Icon_Sticker, bg = blueBG, relief = 'flat')

            # buttonStickers.pack(padx = 8, side = 'left', anchor = 'w', pady = 8)
            buttonStickers.grid(column = 0, row = 0, columnspan = 2, rowspan = 2, padx = 4)

            buttonStickers.config(command = AutoBox.remoteExecuteStickerSheets)

        elif id == 'Ceramic Tiles' :
            buttonTile = tkinter.Button(self.frame, image = Icon_Tile, bg = blueBG, relief = 'flat')

            # buttonTile.pack(padx = 8, side = 'left', anchor = 'w', pady = 8)
            buttonTile.grid(column = 0, row = 0, columnspan = 2, rowspan = 2, padx = 4)

            buttonTile.config(command = AutoBox.remoteExecuteTileSheets)

        elif id == 'Bottlecaps' :
            buttonCap = tkinter.Button(self.frame, image = Icon_Cap, bg = blueBG, relief = 'flat')

            # buttonCap.pack(padx = 8, side = 'left', anchor = 'w', pady = 8)
            buttonCap.grid(column = 0, row = 0, columnspan = 2, rowspan = 2, padx = 4)

            buttonCap.config(command = AutoBox.remoteExecuteCapSheets)

        elif id == 'Metal Round Signs' :
            buttonMetal = tkinter.Button(self.frame, image = Icon_Metal, bg = blueBG, relief = 'flat')

            # buttonMetal.pack(padx = 8, side = 'left', anchor = 'w', pady = 8)
            buttonMetal.grid(column = 0, row = 0, columnspan = 2, rowspan = 2, padx = 4)

            buttonMetal.config(command = AutoBox.remoteExecuteMetalSheets)

        self.label = tkinter.Label(self.frame, text = str(id), font = fontDirectory, bg = blueBG, fg = white, justify = 'left')
        # self.label.pack(side = 'top', anchor = 'nw', ipadx = 4)
        self.label.grid(column = 2, row = 0, columnspan = 8, sticky = 'nw', padx = 8)

        self.entry = tkinter.Entry(self.frame, font = fontDirectory, width = 72, textvariable = self.directory)
        # self.entry.pack(side = 'left', ipady = 2, padx = 6)
        self.entry.grid(column = 2, row = 1, columnspan = 8, padx = 8)
        self.entry.insert(0, self.directory)

        self.updateButton = tkinter.Button(self.frame, image = Icon_Update, bg = blueBG, relief = 'flat')
        # self.updateButton.pack(side = 'left', padx = 7, pady = 0)
        self.updateButton.grid(column = 10, row = 1, padx = 4)

        self.openButton = tkinter.Button(self.frame, image = Icon_Folder, bg = blueBG, relief = 'flat')
        # self.openButton.pack(side = 'left', padx = 0, pady = 0)
        self.openButton.config(command = self.openFolder)
        self.openButton.grid(column = 11, row = 1, padx = 4)


        self.frame.pack(pady = 8)

        if cerberusStatus == True :
            self.w = Watcher()
            self.w.start(self.directory)

    def updateDirectory(self) :
        self.directory = self.directoryVar.get()

    def startWatcher(self) :
        self.w = Watcher()
        self.w.start(self.directory)

    def stopWatcher(self) :
        try:
            self.w.stop()
        except:
            print('No thread to shut down. Thread #' + str(self.id))

    def openFolder(self) :
        os.startfile(self.directory)

# --------------------------------------------------------------------- #

class Watcher():

    def __init__(self) :
        self.observer = Observer()

    def start(self, directory) :
        self.thread = threading.Thread(target=self.run, args=(directory, ))
        self.thread.start()

    def run(self, directory) :
        eventHandler = Handler(directory)
        self.observer.schedule(eventHandler, directory, recursive=True)
        self.observer.start()

        try:
            while True :
                time.sleep(5)
        except:
            self.observer.stop()
            print('Error')
        
        self.observer.join()

    def stop(self) :
        self.observer.stop()
        self.thread.stop()
        print('Stopped ' + str(self))

# --------------------------------------------------------------------- #

class Handler(FileSystemEventHandler) :

    def __init__(self, directory) :
        self.directory = directory

    # @staticmethod
    def on_any_event(self, event):
        if event.is_directory:
            return None
        
        elif event.event_type == 'created' :
            if event.src_path.__contains__('barcode-') :
                # main.RemoteControlRenamer(self.directory)
                Renamer.ParseFolder(params={'Directory' : self.directory})

            # Take any action here when a file is created
            print('Received create event. - %s' % event.src_path)

# --------------------------------------------------------------------- #

if __name__ == '__main__':

    try:

        item1 = CerberusDirectory(middleFrame, 'C:/Users/jfuchs/Dropbox/z_CITRA LF PRINT JOBS TO METRO/TECHSTYLES_CUSTOM SHAPE LABELS/PRINT FILES', 'Stickers')
        itemArray.append(item1)

        item2 = CerberusDirectory(middleFrame, 'C:/Users/jfuchs/Dropbox/z_CITRA LF PRINT JOBS TO METRO/TILE COASTERS/PRINT', 'Ceramic Tiles')
        itemArray.append(item2)

        item3 = CerberusDirectory(middleFrame, 'C:/Users/jfuchs/Dropbox/z_CITRA LF PRINT JOBS TO METRO/METAL SIGNS/SIGN PRINT FILES', 'Metal Round Signs')
        itemArray.append(item3)

        item4 = CerberusDirectory(middleFrame, 'C:/Users/jfuchs/Dropbox/z_CITRA LF PRINT JOBS TO METRO/CAPS TICKETS FILES/DAILY CAP PRINT FILES', 'Bottlecaps')
        itemArray.append(item4)

        atexit.register(shutDownCerberus)

        root.mainloop()
    
    except:
        
        shutDownCerberus()