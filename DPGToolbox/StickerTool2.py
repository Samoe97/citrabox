import os
import math
import shutil
from DPGToolbox import sLog
from DPGToolbox import Renamer
from DPGToolbox import Archiver_TS
from DPGToolbox import SiteFlow
import json
import time

from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.colors import CMYKColorSep

from pdfrw import PdfReader
from pdfrw.buildxobj import pagexobj
from pdfrw.toreportlab import makerl

from barcode import Code128

global sheetIndex
sheetIndex = 1

moduleName = 'asdf'

barcodePath = os.path.dirname(__file__)
barcodePath = os.path.split(barcodePath)[0]
barcodePath = barcodePath + '/assets/barcode'

print(barcodePath)


def points(inches):
    points = float(inches) * 72
    return float(points)

def executeStickerSheetGenerator(params) :

    if params['Directory'] == '' :
        sLog.slogPrint(' - No directory selected.')
        return

    global startTime
    startTime = time.time()

    sLog.slogPrint(' ---- Beginning Sticker Sheet Generation ---- ')
    
    allPrintPDFs = []
    allInfoPDFs = []
    allBarcodes = []

    createBarcode = True

    for file in os.listdir(params['Directory']):
        if file.endswith('PRINT.pdf') and not file.__contains__('TILE'):
            allPrintPDFs.append(file)

        elif file.endswith('TICKET.pdf') and not file.__contains__('TILE'):
            if params['DontIncludeTicket'] == False :
                allInfoPDFs.append(file)

    if params['addCutLineToTicket'] == True:
        for i in allInfoPDFs :
            itemSpecs = Renamer.fileNameParser(i)

            filepath = params['Directory'] + '/' + i
            pythonInfoCut(filepath, itemSpecs)

            sLog.slogPrint(' - Added cut line to infotech for order ' + itemSpecs["order"] + ' | SKU ' + itemSpecs["sku"] + ' succesfully.')

            # if createBarcode == True :
                
            #     orderInfo = SiteFlow.get_order_by_sourceID(itemSpecs['order'])
            #     orderInfo = json.loads(orderInfo.text)

            #     orderInfo = SiteFlow.get_extra_order_details(orderInfo['data'][0]['_id'])
            #     orderInfo = json.loads(orderInfo.text)

            #     index = 0
            #     for a in orderInfo['jobs'] :
            #         if a['attributes']['Customer_SKU'] == itemSpecs['sku'] :
            #             if a['attributes']['Catfish_ME_Height'][0] == itemSpecs['height'] and a['attributes']['Catfish_ME_Width'][0] == itemSpecs['width'] :

            #                 barcode = orderInfo['batches'][index]['barcode']
            #                 barcodeObj = Code128(barcode)
            #                 barcodeObj.save(barcodePath)
            #                 sLog.slogPrint(' - Created Barcode file for ' + itemSpecs["order"] + ' | SKU ' + itemSpecs["sku"])




            #                 break

            #         else : index = index + 1

    # Create Sticker Sheets
    for i in allPrintPDFs :
        index = allPrintPDFs.index(i)
        itemSpecs = Renamer.fileNameParser(i)
        sLog.slogPrint(' - Beginning sheet generation for order ' + itemSpecs["order"] + ' | SKU ' + itemSpecs["sku"])
        if params['DontIncludeTicket'] == True:
            infotech = ''
        else :
            try:
                infotech = allInfoPDFs[index]
            except:
                sLog.slogPrint(' - No Infotech found for ' + itemSpecs["order"] + ' | SKU ' + itemSpecs["sku"])

        pythonSheetGenerator(i, infotech, itemSpecs, params)

    endTime = time.time()
    timerResult = round(endTime - startTime, 2)
    sLog.slogPrint(' - Execution took ' + str(timerResult) + ' seconds.')
    sLog.slogPrint(' ---- Sticker sheet generation complete! ---- \n')
    try:
        Archiver_TS.ProcessFolder(params['Directory'])
    except:
        sLog.slogPrint(' !!!! Archiver failed. Maybe you aren`t connected to the LF server.')
    

def pythonInfoCut(infotech, itemSpecs):

    ticketFile = PdfReader(infotech).pages[0]
    ticketFile = pagexobj(ticketFile)

    width = points(itemSpecs["width"][0]),
    height = points(itemSpecs["height"][0]),

    width = float(width[0])
    height = float(height[0])

    canvas = Canvas(infotech)
    canvas.setPageSize((width, height))

    canvas.doForm(makerl(canvas, ticketFile))

    width = width - points(0.2)
    height = height - points(0.2)
    positionX = points(0.1)
    positionY = points(0.1)

    perfCut = CMYKColorSep(1, 0, 1, 0, 'PerfCutContour', 1, 1)

    canvas.setStrokeColor(perfCut)

    canvas.rect(positionX, positionY, width, height, stroke=1, fill=0)

    canvas.save()

def pythonSheetGenerator(printFileName, ticketFileName, itemSpecs, params) :
    
    printFile = PdfReader(params['Directory'] + '/' + printFileName).pages[0]
    printFile = pagexobj(printFile)

    if ticketFileName != '' :
        ticketFile = PdfReader(params['Directory'] + '/' + ticketFileName).pages[0]
        ticketFile = pagexobj(ticketFile)
    else : ticketFile = printFile

    sheetsPath = params['Directory'] + '/Sheets'
    if not os.path.isdir(sheetsPath):
        os.mkdir(sheetsPath)

    global sheetIndex
    global spaceBetweenStickers

    width = points(itemSpecs["width"])
    height = points(itemSpecs["height"])
    space = points(params['SpaceBetweenStickers'])

    printQuantity = int(itemSpecs["quantity"]) + int(params['ExtraStickers'])

    rows = math.ceil(points(params['MaxSheetHeight']) / (height + space))
    columns = math.floor(points(params['MaxSheetWidth']) / (width + space))

    canvasWidth = (width + space) * columns
    canvasHeight = (height + space) * rows

    qtyPerSheet = rows * columns

    if qtyPerSheet >= printQuantity :
        qtyPerSheet = printQuantity

    sheetsNeeded = math.ceil(printQuantity / qtyPerSheet)


    # MAIN SHEET CREATION LOOP
    for i in range(sheetsNeeded) :

        sLog.slogPrint(' ---- Creating sheet ' + str(sheetIndex) + ' of ' + str(sheetsNeeded) + ' for order ' + str(itemSpecs["order"]) + ' | SKU ' + str(itemSpecs["sku"]))
       
        # RECALCULATE SHEET HEIGHT IF THIS IS THE LAST SHEET
        if i + 1 == sheetsNeeded :
            rows = math.ceil(printQuantity / columns)
            canvasHeight = (height + space) * rows

        # INITIALIZE THE PDF WE'RE CREATING
        destination = sheetsPath + '/' + printFileName[:-4] + '_Sheet' + str(sheetIndex) + '.pdf'
        canvas = Canvas(destination)    # THIS IS WHERE YOU CHOOSE WHERE THE FILE WILL SAVE TO
        canvas.setPageSize((canvasWidth, canvasHeight))

        # INITIAL STICKER POSITION (USUALLY THE INFOTECH SLOT)
        Xposition = 0
        Yposition = canvasHeight - (height)

        # LOOP THAT PUTS STICKERS ONTO SHEET
        for f in range(qtyPerSheet) :

            # OPEN CANVAS TO BE EDITED
            canvas.saveState()

            # IF WE REACH THE LAST COLUMN, MOVE TO THE NEXT ROW
            if f % columns == 0 and f != 0 :
                Xposition = 0
                Yposition = Yposition - (height + space)
            
            # SET POSITION OF NEW STICKER
            canvas.translate(Xposition, Yposition)
            Xposition = Xposition + (width + space)

            # PLACE TICKET OR PRINT FILE
            if params['TicketOnlyOnFirstSheet'] == True:     # THIS IS FOR THE OPTION OF ONLY HAVING THE TICKET ON THE FIRST SHEET
                if sheetIndex == 1:
                    canvas.doForm(makerl(canvas, ticketFile))
                    printQuantity = printQuantity + 1
                else:
                    canvas.doForm(makerl(canvas, printFile))

            else :
                if f == 0:  # IF THIS IS THE FIRST SLOT ON THE SHEET, PLACE A TICKET
                    if params['DontIncludeTicket'] == False:
                        canvas.doForm(makerl(canvas, ticketFile))
                        printQuantity = printQuantity + 1
                    else: 
                        canvas.doForm(makerl(canvas, printFile))    # IF THE USER CHOOSES TO NOT INCLUDE TICKETS, PLACE A PRINT FILE INSTEAD
                
                # PLACE A PRINT FILE
                else:
                    canvas.doForm(makerl(canvas, printFile))

            # CLOSE CANVAS, SIGNIFYING WE ARE DONE EDITING
            canvas.restoreState()

 
        printQuantity = printQuantity - qtyPerSheet     # PROCESS QUANTITY
        canvas.save()   # SAVE FILE (DESTINATION IS SET WHEN WE INITIALIZED CANVAS)
        sheetIndex = sheetIndex + 1     # ADD 1 TO THE SHEET COUNT, LOOP BACK TO BEGINNING IF NEEDED
    
    sLog.slogPrint(' - Success! (' + str(sheetsNeeded) + ' sheets for ' + str(itemSpecs["order"]) + ' | ' + str(itemSpecs['sku']) + ')')
    
    sLog.slogPrint('------------------------------------------------------')

    sheetIndex = 1

    if params['Archive1UPs'] == True:
        oneUpsPath = 'L:/Archive/TechStyles Archive/'
        
        Archiver_TS.archiveFile(params['Directory'] + '/' + printFileName)
        Archiver_TS.archiveFile(params['Directory'] + '/' + ticketFileName)

    else :
        oneUpsPath = params['Directory'] + '/1UPs/'
        if not os.path.isdir(oneUpsPath):
            os.mkdir(oneUpsPath)
        newPrintFilePath = oneUpsPath + printFileName
        newTicketFilePath = oneUpsPath + ticketFileName
        shutil.move(params['Directory'] + '/' + printFileName, newPrintFilePath)
        if params['DontIncludeTicket'] == False:
            shutil.move(params['Directory'] + '/' + ticketFileName, newTicketFilePath)
