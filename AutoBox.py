# AUTOBOX
# Run CitraBox functions on set intervals

import os
import threading
from DPGToolbox import StickerTool2 as Sticker
from DPGToolbox import TileTool2 as Tile
from DPGToolbox import CapTool2 as Cap
from DPGToolbox import MetalRoundTool2 as Metal

interval = 120.0

stickerDir = 'C:/Users/jfuchs/Dropbox/z_CITRA LF PRINT JOBS TO METRO/TECHSTYLES_CUSTOM SHAPE LABELS/PRINT FILES'
tileDir = 'C:/Users/jfuchs/Dropbox/z_CITRA LF PRINT JOBS TO METRO/TILE COASTERS/PRINT'
metalDir = 'C:/Users/jfuchs/Dropbox/z_CITRA LF PRINT JOBS TO METRO/METAL SIGNS/SIGN PRINT FILES'
capDir = 'C:/Users/jfuchs/Dropbox/z_CITRA LF PRINT JOBS TO METRO/CAPS TICKETS FILES/DAILY CAP PRINT FILES'

# --------------------------------------------------------------------- #

def executeAllGenerators() :

    for file in os.listdir(stickerDir) :
        if file.__contains__('PRINT') or file.__contains__('TICKET') :
            remoteExecuteStickerSheets()
            break

    for file in os.listdir(tileDir) :
        if file.__contains__('PRINT') :
            remoteExecuteTileSheets()
            break
    
    for file in os.listdir(capDir) :
        if file.__contains__('50up') :
            remoteExecuteCapSheets()
            break

    for file in os.listdir(metalDir) :
        if file.__contains__('ROUND') :    
            remoteExecuteMetalSheets()

    print('Executed all generators.')

# --------------------------------------------------------------------- #

def remoteExecuteStickerSheets() :

    params = {
        'Directory' : stickerDir,
        'ExtraStickers' : 4,
        'SpaceBetweenStickers' : 0.125,
        'MaxSheetHeight' : 32,
        'MaxSheetWidth' : 50,
        'DontIncludeTicket' : False,
        'TicketOnlyOnFirstSheet' : False,
        'Archive1UPs' : True,
        'addCutLineToTicket' : True
    }

    Sticker.executeStickerSheetGenerator(params)

def remoteExecuteTileSheets() :

    params = { 'Directory' : tileDir }
    
    Tile.executeTileSheetGeneratorPython(params)

def remoteExecuteCapSheets() :
    
    params = { 'Directory' : capDir }

    Cap.executeCap3UPSheetGenerator(params)

def remoteExecuteMetalSheets() :

    params = { 'Directory' : metalDir }

    Metal.executeRoundSheetGeneratorPython(params)

# --------------------------------------------------------------------- #

def startAutoBox():
    global t
    t = threading.Timer(interval, startAutoBox)
    t.start()
    executeAllGenerators()

def stopAutoBox() :
    global t
    t.cancel()

