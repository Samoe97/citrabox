import os
import math
import shutil
from toolbox.sLog import slogPrint
from toolbox import Renamer
from toolbox import Archiver_TS

from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.colors import CMYKColorSep

from pdfrw import PdfReader
from pdfrw.buildxobj import pagexobj
from pdfrw.toreportlab import makerl

global sheetIndex
sheetIndex = 1

global tilePositions
tilePositions = [
        [59, 382],
        [383, 382],
        [707, 382],
        [1031, 382],
        [59, 58],
        [383, 58],
        [707, 58],
        [1031, 58]]

global remainderArray

def points(inches):
    points = float(inches) * 72
    return float(points)

def executeTileSheetGeneratorPython(params) :

    if params['Directory'] == '' :
        slogPrint(' - No directory selected.')
        return

    global remainderArray

    slogPrint(' ---- Beginning Tile Sheet Generation ---- ')

    allPrintPDFs = []
    allDistressedPDFs = []
    remainderArray = []

    for file in os.listdir(params['Directory']):

        if file.startswith('TILE_'):
            allPrintPDFs.append(file)

        if str.lower(file).__contains__(str.lower('DISTRESSED')):
            allDistressedPDFs.append(file)

    slogPrint('------------------------------------------------------')

    if len(allPrintPDFs) <= 0 and len(allDistressedPDFs) <= 0:
        slogPrint(' - No TILE files found. Make sure to rename the raw files from PrintOS using this tool before running any sheet scripts.')
    
    else:
        for i in allPrintPDFs :
            itemSpecs = Renamer.fileNameParser(i)
            slogPrint(' - Beginning sheet generation for Order: ' + itemSpecs["order"] + ' | SKU: ' + itemSpecs["sku"])
            tileSheetGeneratorPython(i, itemSpecs, params['Directory'])

        if len(remainderArray) >= 1 :
            slogPrint(' - Beginning remainder sheet generation...')
            tileRemainderSheetGeneratorPython(params['Directory'])
        
        remainderArray = []

        slogPrint('------------------------------------------------------')

        for i in allDistressedPDFs :
            itemSpecs = Renamer.fileNameParser(i)
            slogPrint(' - Beginning distressed sheet generation for Order: ' + itemSpecs["order"] + ' | SKU: ' + itemSpecs["sku"])
            tileSheetGeneratorPython(i, itemSpecs, params['Directory'])

        if len(remainderArray) >= 1 :
            slogPrint(' - Beginning distressed remainder sheet generation...')
            tileRemainderSheetGeneratorPython(params['Directory'])

        slogPrint(' ---- Success! Tile sheet generation finished. ---- ')

        try:
            Archiver_TS.ProcessFolder(params['Directory'])
        except:
            slogPrint(' !!!! Archiver failed. Maybe you aren`t connected to the LF server.')


def tileSheetGeneratorPython(printFileName, itemSpecs, directory) :
    
    printFile = PdfReader(directory + '/' + printFileName).pages[0]
    printFile = pagexobj(printFile)

    sheetsPath = directory + '/Sheets'
    if not os.path.isdir(sheetsPath):
        os.mkdir(sheetsPath)

    global sheetIndex

    printQuantity = int(itemSpecs["quantity"])

    canvasWidth = 1369
    canvasHeight = 793

    remainder = 0

    if printQuantity > 8 :
        remainder = math.ceil(printQuantity % 8)
    elif printQuantity < 8 :
        slogPrint(' ---- (!) Qty is less than 8. Adding this item to the remainder list instead.')
        for i in range(printQuantity) :
            remainderArray.append(printFileName)
        return
    sheetsNeeded = math.floor(printQuantity / 8)
    if (sheetsNeeded == 0) :
        sheetsNeeded = 1

    # INITIALIZE THE PDF WE'RE CREATING
    destination = sheetsPath + '/TILE_' + str(itemSpecs["order"]) + '_' + str(itemSpecs["sku"]) + '_qty' + str(printQuantity) + '_PRINT ' + str(sheetsNeeded) + ' SHEETS.pdf'
    canvas = Canvas(destination)    # THIS IS WHERE YOU CHOOSE WHERE THE FILE WILL SAVE TO
    canvas.setPageSize((canvasWidth, canvasHeight))

    loopIndex = 0
    
    for i in range(printQuantity) :

        # OPEN CANVAS TO BE EDITED
        canvas.saveState()
        
        # SET POSITION OF NEW STICKER
        canvas.translate(tilePositions[i][0], tilePositions[i][1])

        # PLACE PRINT FILE
        canvas.doForm(makerl(canvas, printFile))

        # CLOSE CANVAS, SIGNIFYING WE ARE DONE EDITING
        canvas.restoreState()

        loopIndex = loopIndex + 1
        if (loopIndex >= 8) :
            break

    if (remainder > 0) :
        for i in range(remainder) :
            remainderArray.append(printFileName)

    canvas.save()   # SAVE FILE (DESTINATION IS SET WHEN WE INITIALIZED CANVAS)

    #--------------------------------------------------------------------------------------#
    
    slogPrint(' - Success! (' + str(sheetsNeeded) + ' sheets for ' + str(itemSpecs["order"]) + ' | ' + str(itemSpecs['sku']) + ')')
    
    slogPrint('------------------------------------------------------')

    # if params['Archive1UPs'] == True:
    #     oneUpsPath = '//192.168.0.209/Archive/TechStyles Archive/'
        
    #     Archiver_TS.archiveFile(params['Directory'] + '/' + printFileName)
    #     Archiver_TS.archiveFile(params['Directory'] + '/' + ticketFileName)

    # else :
    #     oneUpsPath = params['Directory'] + '/1UPs/'
    #     if not os.path.isdir(oneUpsPath):
    #         os.mkdir(oneUpsPath)
    #     newPrintFilePath = oneUpsPath + printFileName
    #     newTicketFilePath = oneUpsPath + ticketFileName
    #     shutil.move(params['Directory'] + '/' + printFileName, newPrintFilePath)
    #     if params['DontIncludeTicket'] == False:
    #         shutil.move(params['Directory'] + '/' + ticketFileName, newTicketFilePath)

def tileRemainderSheetGeneratorPython(directory) :

    global sheetIndex

    remainderOrders = []
    remainderSkus = []

    sheetsPath = directory + '/Sheets'
    if not os.path.isdir(sheetsPath):
        os.mkdir(sheetsPath)

    remainingQty = len(remainderArray)

    # -------------------------------------------------------------------------------- #

    if remainingQty >= 8:
        for i in range(8) :
            itemSpecs = Renamer.fileNameParser(remainderArray[i])
            if not remainderOrders.__contains__(itemSpecs['order']) :
                remainderOrders.append(itemSpecs['order'])
            if not remainderSkus.__contains__(itemSpecs['sku']) :
                remainderSkus.append(itemSpecs['sku'])
    else :
        for i in range(remainingQty) :
            itemSpecs = Renamer.fileNameParser(remainderArray[i])
            if not remainderOrders.__contains__(itemSpecs['order']) :
                remainderOrders.append(itemSpecs['order'])
            if not remainderSkus.__contains__(itemSpecs['sku']) :
                remainderSkus.append(itemSpecs['sku'])

    if len(remainderOrders) > 1:
        remainderIndex = 1
        remainderOrdersFinal = ''
        remainderOrdersText = str(remainderOrders)
        remainderOrdersText = remainderOrdersText.split("'")
        for h in remainderOrders :
            remainderOrdersFinal = remainderOrdersFinal + (remainderOrdersText[remainderIndex] + ', ')
            remainderIndex = remainderIndex + 2
        destination = sheetsPath + '/TILE REM - Orders ' + remainderOrdersFinal
        destination = destination[:-2] + ' PRINT.pdf'
        for file in os.listdir(directory + '/Sheets') :
            if directory + '/Sheets/' + file == destination :
                destination = destination[:-4] + '_' + str(sheetIndex) + '.pdf'
    else:
        remainderOrdersFinal = ''
        remainderOrdersText = str(remainderOrders)
        remainderOrdersText = remainderOrdersText.split("'")
        remainderOrdersFinal = remainderOrdersFinal + (remainderOrdersText[1])
        destination = sheetsPath + '/TILE REM - Order ' + remainderOrdersFinal
        destination = destination + ' PRINT.pdf'
        for file in os.listdir(directory + '/Sheets') :
            if directory + '/Sheets/' + file == destination :
                destination = destination[:-4] + '_' + str(sheetIndex) + '.pdf'

    # -------------------------------------------------------------------------------- #

    loopIndex = 0

    canvasWidth = 1369
    canvasHeight = 793

    remainder = 0

    # INITIALIZE THE PDF WE'RE CREATING
    canvas = Canvas(destination)    # THIS IS WHERE YOU CHOOSE WHERE THE FILE WILL SAVE TO
    canvas.setPageSize((canvasWidth, canvasHeight))

    if len(remainderArray) < 8 :
        loopRange = len(remainderArray)
    else: loopRange = 8

    for x in range(loopRange):
        itemSpecs = Renamer.fileNameParser(remainderArray[x])
        printFileName = remainderArray[x]

        printFile = PdfReader(directory + '/' + printFileName).pages[0]
        printFile = pagexobj(printFile)
        
        # OPEN CANVAS TO BE EDITED
        canvas.saveState()
        
        # SET POSITION OF NEW STICKER
        canvas.translate(tilePositions[x][0], tilePositions[x][1])

        # PLACE PRINT FILE
        canvas.doForm(makerl(canvas, printFile))

        # CLOSE CANVAS, SIGNIFYING WE ARE DONE EDITING
        canvas.restoreState()

        loopIndex = loopIndex + 1

        if (loopIndex >= 8) :
            break

    canvas.save()

    for l in range(loopIndex) :
        remainderArray.pop(0)
        
    if len(remainderArray) >= 1 :
        sheetIndex = sheetIndex + 1
        tileRemainderSheetGeneratorPython(directory)