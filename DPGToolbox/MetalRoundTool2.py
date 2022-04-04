import os
import math
import shutil
from DPGToolbox.sLog import slogPrint
from DPGToolbox import Renamer
from DPGToolbox import Archiver_TS

from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.colors import CMYKColorSep

from pdfrw import PdfReader
from pdfrw.buildxobj import pagexobj
from pdfrw.toreportlab import makerl

global sheetIndex
sheetIndex = 1

global metalPositions
metalPositions = [
        [53, 835],
        [917, 835],
        [53, -29],
        [917, -29]]

global remainderArray

def points(inches):
    points = float(inches) * 72
    return float(points)

def executeRoundSheetGeneratorPython(params) :

    if params['Directory'] == '' :
        slogPrint(' - No directory selected.')
        return

    global remainderArray

    slogPrint(' ---- Beginning Metal Round Sheet Generation ---- ')

    allPrintPDFs = []
    allDistressedPDFs = []
    remainderArray = []

    for file in os.listdir(params['Directory']):

        if file.startswith('ROUND_'):
            allPrintPDFs.append(file)

    slogPrint('------------------------------------------------------')

    if len(allPrintPDFs) <= 0 :
        slogPrint(' - No ROUND files found. Make sure to rename the raw files from PrintOS using this tool before running any sheet scripts.')
    
    else:
        for i in allPrintPDFs :
            itemSpecs = Renamer.fileNameParser(i)
            slogPrint(' - Beginning sheet generation for Order: ' + itemSpecs["order"] + ' | SKU: ' + itemSpecs["sku"])
            roundSheetGeneratorPython(i, itemSpecs, params['Directory'])

        if len(remainderArray) >= 1 :
            slogPrint(' - Beginning remainder sheet generation...')
            roundRemainderSheetGeneratorPython(params['Directory'])
        
        remainderArray = []

        slogPrint('------------------------------------------------------')

        slogPrint(' ---- Success! Metal Round sheet generation finished. ---- ')

        try:
            Archiver_TS.ProcessFolder(params['Directory'])
        except:
            slogPrint(' !!!! Archiver failed. Maybe you aren`t connected to the LF server.')

def roundSheetGeneratorPython(printFileName, itemSpecs, directory) :
    
    printFile = PdfReader(directory + '/' + printFileName).pages[0]
    printFile = pagexobj(printFile)

    sheetsPath = directory + '/Sheets'
    if not os.path.isdir(sheetsPath):
        os.mkdir(sheetsPath)

    global sheetIndex

    printQuantity = int(itemSpecs["quantity"])

    canvasWidth = 1800.72
    canvasHeight = 1800.72

    remainder = 0

    if printQuantity > 4 :
        remainder = math.ceil(printQuantity % 4)
    elif printQuantity < 4 :
        slogPrint(' ---- (!) Qty is less than 4. Adding this item to the remainder list instead.')
        for i in range(printQuantity) :
            remainderArray.append(printFileName)
        return
    sheetsNeeded = math.floor(printQuantity / 4)
    if (sheetsNeeded == 0) :
        sheetsNeeded = 1

    # INITIALIZE THE PDF WE'RE CREATING
    destination = sheetsPath + '/ROUNDS_' + str(itemSpecs["order"]) + '_' + str(itemSpecs["sku"]) + '_qty' + str(printQuantity) + '_PRINT ' + str(sheetsNeeded) + ' SHEETS.pdf'
    canvas = Canvas(destination)    # THIS IS WHERE YOU CHOOSE WHERE THE FILE WILL SAVE TO
    canvas.setPageSize((canvasWidth, canvasHeight))

    loopIndex = 0
    
    for i in range(printQuantity) :

        # OPEN CANVAS TO BE EDITED
        canvas.saveState()
        
        # SET POSITION OF NEW STICKER
        canvas.translate(metalPositions[i][0], metalPositions[i][1])

        # PLACE PRINT FILE
        canvas.doForm(makerl(canvas, printFile))

        # CLOSE CANVAS, SIGNIFYING WE ARE DONE EDITING
        canvas.restoreState()

        loopIndex = loopIndex + 1
        if (loopIndex >= 4) :
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

def roundRemainderSheetGeneratorPython(directory) :

    global sheetIndex

    remainderOrders = []
    remainderSkus = []

    sheetsPath = directory + '/Sheets'
    if not os.path.isdir(sheetsPath):
        os.mkdir(sheetsPath)

    remainingQty = len(remainderArray)

    # -------------------------------------------------------------------------------- #

    if remainingQty >= 4:
        for i in range(4) :
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
        destination = sheetsPath + '/ROUNDS_Orders ' + remainderOrdersFinal
        destination = destination[:-2] + ' PRINT.pdf'
        for file in os.listdir(directory + '/Sheets') :
            if directory + '/Sheets/' + file == destination :
                destination = destination[:-4] + '_' + str(sheetIndex) + '.pdf'
    else:
        remainderOrdersFinal = ''
        remainderOrdersText = str(remainderOrders)
        remainderOrdersText = remainderOrdersText.split("'")
        remainderOrdersFinal = remainderOrdersFinal + (remainderOrdersText[1])
        destination = sheetsPath + '/ROUNDS_Order ' + remainderOrdersFinal
        destination = destination + ' PRINT.pdf'
        for file in os.listdir(directory + '/Sheets') :
            if directory + '/Sheets/' + file == destination :
                destination = destination[:-4] + '_' + str(sheetIndex) + '.pdf'

    # -------------------------------------------------------------------------------- #

    loopIndex = 0

    canvasWidth = 1800.72
    canvasHeight = 1800.72

    remainder = 0



    # INITIALIZE THE PDF WE'RE CREATING
    canvas = Canvas(destination)    # THIS IS WHERE YOU CHOOSE WHERE THE FILE WILL SAVE TO
    canvas.setPageSize((canvasWidth, canvasHeight))

    if len(remainderArray) < 4 :
        loopRange = len(remainderArray)
    else: loopRange = 4

    for x in range(loopRange):
        itemSpecs = Renamer.fileNameParser(remainderArray[x])
        printFileName = remainderArray[x]

        printFile = PdfReader(directory + '/' + printFileName).pages[0]
        printFile = pagexobj(printFile)
        
        # OPEN CANVAS TO BE EDITED
        canvas.saveState()
        
        # SET POSITION OF NEW STICKER
        canvas.translate(metalPositions[x][0], metalPositions[x][1])

        # PLACE PRINT FILE
        canvas.doForm(makerl(canvas, printFile))

        # CLOSE CANVAS, SIGNIFYING WE ARE DONE EDITING
        canvas.restoreState()

        loopIndex = loopIndex + 1

        if (loopIndex >= 4) :
            break

    canvas.save()

    for l in range(loopIndex) :
        remainderArray.pop(0)
        
    if len(remainderArray) >= 1 :
        sheetIndex = sheetIndex + 1
        roundRemainderSheetGeneratorPython(directory)