###########################################################
# DPG LARGE FORMAT CAP TOOL V3 ############################


###########################################################
# REQUIRED IMPORTS ########################################
from DPGToolbox import Renamer
from DPGToolbox.sLog import slogPrint
import math, os
from DPGToolbox import Archiver_TS

###########################################################
# IMPORTS FOR PDF CREATION ################################
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.colors import CMYKColorSep
from pdfrw import PdfReader
from pdfrw.buildxobj import pagexobj
from pdfrw.toreportlab import makerl

###########################################################
# INITIALIZE CONSTANTS ####################################
global scriptLocation
global allPrintPDFs
global jsSave
scriptLocation = os.path.dirname(__file__)
assetLocation = scriptLocation.replace('DPGToolbox', 'assets')
jsSave = assetLocation + '/jssavePS.js'

###########################################################
# INITIALIZE VARIABLES ####################################
global sheetIndex
sheetIndex = 1

###########################################################
# CHECK FOR DUPLICATE FILE IN FOLDER ######################
def checkFileDuplicate(sheetsPath) :
        global sheetIndex
        global destination
        found = False
        for file in os.listdir(sheetsPath) :
            if sheetsPath + '/' + file == destination :
                found = True
                if file.__contains__('-') :
                    splitfile = file.split('-')
                    destination = sheetsPath + '/' + splitfile[0] + '-' + str(sheetIndex) + '.pdf'
                    sheetIndex = sheetIndex + 1
                    continue
                else:
                    destination = destination[:-4] + '-' + str(sheetIndex) + '.pdf'
                    sheetIndex = sheetIndex + 1
                    continue
        if found == False:
            return destination
        else :
            checkFileDuplicate(sheetsPath)

###########################################################
# EXECUTE 3UP CAP SHEET GENERATOR #########################
def executeCap3UPSheetGenerator(params) :

    if params['Directory'] == '' :
        slogPrint(' - No directory selected.')
        return
    else :
        directory = params['Directory']

    allPrintPDFs = []
    totalCapColors = []

    for file in os.listdir(directory):
        if file.startswith('CAPS 50up'):
            itemSpecs = Renamer.fileNameParser(file)
            currentColor = itemSpecs['sku']
            if not totalCapColors.__contains__(currentColor) :
                totalCapColors.append(currentColor)
            
            if int(itemSpecs['quantity'])/50 > 3 :
                for a in range(math.ceil(int(itemSpecs['quantity'])/50)) :
                    allPrintPDFs.insert(0,{'color' : currentColor, 'file' : file})
            else:
                for a in range(int(int(itemSpecs['quantity'])/50)) :
                    allPrintPDFs.append({'color' : currentColor, 'file' : file})

    for c in totalCapColors :
        sheetsToPrint = []
        for i in allPrintPDFs :
            if i['color'] == c :
                sheetsToPrint.append(i['file'])

        cap3UPSheetGeneratorPython(directory, sheetsToPrint, params['adjustment'])

    slogPrint(' ---- Bottlecap 3UP sheet generation complete! ---- \n')
    # try:
    if params['archive'] == True :
        Archiver_TS.ProcessFolder(params['Directory'])
    # except:
        # slogPrint(' !!!! Archiver failed. Maybe you aren`t connected to the LF server.')

###########################################################
# GENERATE 3UP CAP SHEETS #################################
def cap3UPSheetGeneratorPython(directory, allPrintPDFs, adjustment=[]):
    
    positions = [
        (20, -26),
        (677.5, -24),
        (1507, -24)
    ]

    if adjustment != [] :
        newPositions = []
        for i in positions :
            x = i[0] + adjustment[0]
            x = x + adjustment[1]
            y = i[1] + adjustment[2]
            y = y + adjustment[3]
            newPositions.append((x, y))
        positions = newPositions

    sheetsPath = directory + '/Sheets'
    if not os.path.isdir(sheetsPath):
        os.mkdir(sheetsPath)

    batchedOrders = []
    if len(allPrintPDFs) >= 3:
        for i in range(3) :
            itemSpecs = Renamer.fileNameParser(allPrintPDFs[i])
            if not batchedOrders.__contains__(itemSpecs['order']) :
                batchedOrders.append(itemSpecs['order'])
    else :
        for i in range(len(allPrintPDFs)) :
            itemSpecs = Renamer.fileNameParser(allPrintPDFs[i])
            if not batchedOrders.__contains__(itemSpecs['order']) :
                batchedOrders.append(itemSpecs['order'])
    
    orders = ''
    if len(batchedOrders) == 1:
        orders = batchedOrders[0]
    else :
        for i in batchedOrders :
            if i == batchedOrders[len(batchedOrders)-1] :
                orders = orders + i
            else :
                orders = orders + i + ', '

    color = itemSpecs['sku']
    qty = itemSpecs['quantity']

    global sheetIndex
    global destination
    destination = sheetsPath + '/CAPS_3UP_' + str(orders) + '_' + str(color) + '_qty' + str(qty) + '.pdf'

    sheetIndex = 1
    checkFileDuplicate(sheetsPath)

    # INITIALIZE THE PDF WE'RE CREATING
    canvasSize = [2085, 920]
    canvas = Canvas(destination)    # THIS IS WHERE YOU CHOOSE WHERE THE FILE WILL SAVE TO
    canvas.setPageSize((canvasSize[0], canvasSize[1]))

    loopIndex = 0
    for i in allPrintPDFs :

        printFileName = str(directory) + '/' + i
        printFile = PdfReader(printFileName).pages[0]
        printFile = pagexobj(printFile)
        itemSpecs = Renamer.fileNameParser(i)

        # OPEN CANVAS TO BE EDITED
        canvas.saveState()
        
        # SET POSITION OF NEW CAP
        canvas.translate(positions[loopIndex][0], positions[loopIndex][1])

        # PLACE PRINT FILE
        canvas.doForm(makerl(canvas, printFile))

        # CLOSE CANVAS, SIGNIFYING WE ARE DONE EDITING
        canvas.restoreState()

        loopIndex = loopIndex + 1

        if loopIndex >= 3 :
            break

    del allPrintPDFs[:(loopIndex)]

    canvas.save()

    slogPrint(' - Bottlecap 3UP sheet generated for order(s) ' + str(orders))

    if len(allPrintPDFs) > 0 :
        cap3UPSheetGeneratorPython(directory, allPrintPDFs)

###########################################################
# EXECUTE 50UP CAP SHEET GENERATOR ########################
def executeCap50upGenerator(params) :

    if params['Directory'] == '' :
        slogPrint(' - No directory selected.')
        return
    else :
        directory = params['Directory']

    allPrintPDFs = []

    for file in os.listdir(directory):
        if file.startswith('CAP_'):
            # itemSpecs = Renamer.fileNameParser(file)
            allPrintPDFs.append(file)

    capSheetGen50up(directory, allPrintPDFs)

    slogPrint(' ---- Bottlecap 50UP sheet generation complete! ---- \n')

###########################################################
# GENERATE 50UP CAP SHEETS ################################
def capSheetGen50up(directory, allPrintPDFs) :

    RDG_WHITE = CMYKColorSep(0, 1, 1, 0, 'RDG_WHITE', 1, 1)

    sheetsPath = directory + '/50up Sheets'
    if not os.path.isdir(sheetsPath):
        os.mkdir(sheetsPath)

    positions = [
        (81, 840.5),
        (184.5, 840.5),
        (288, 840.5),
        (391.5, 840.5),
        (495, 840.5),

        (27, 750.5),
        (130.5, 750.5),
        (234, 750.5),
        (337.5, 750.5),
        (441, 750.5),

        (81, 660.5),
        (184.5, 660.5),
        (288, 660.5),
        (391.5, 660.5),
        (495, 660.5),

        (27, 570.5),
        (130.5, 570.5),
        (234, 570.5),
        (337.5, 570.5),
        (441, 570.5),

        (81, 480.5),
        (184.5, 480.5),
        (288, 480.5),
        (391.5, 480.5),
        (495, 480.5),

        (27, 390.5),
        (130.5, 390.5),
        (234, 390.5),
        (337.5, 390.5),
        (441, 390.5),

        (81, 300.5),
        (184.5, 300.5),
        (288, 300.5),
        (391.5, 300.5),
        (495, 300.5),

        (27, 210.5),
        (130.5, 210.5),
        (234, 210.5),
        (337.5, 210.5),
        (441, 210.5),

        (81, 120.5),
        (184.5, 120.5),
        (288, 120.5),
        (391.5, 120.5),
        (495, 120.5),

        (27, 30.5),
        (130.5, 30.5),
        (234, 30.5),
        (337.5, 30.5),
        (441, 30.5),

    ]

    for file in allPrintPDFs :

        global sheetIndex
        global destination

        itemSpecs = Renamer.fileNameParser(file)

        if itemSpecs['sku'] != 'White' :

            app = hookPhotoshop()
            destination = directory + '/' + file

            app.Open(destination)
            app.DoAction("Sample underprint white test 1", "To add White Underprint")

            arguments = [app.ActiveDocument, destination]
            app.DoJavaScriptFile(jsSave, arguments)

        qty = itemSpecs['quantity']

        destination = sheetsPath + '/CAPS 50up_' + str(itemSpecs['order']) + '_' + str(itemSpecs['sku']) + '_qty ' + str(qty) + '.pdf'
        checkFileDuplicate(sheetsPath)

        # INITIALIZE THE PDF WE'RE CREATING
        canvasSize = [608.4, 952.08]
        canvas = Canvas(destination)    # THIS IS WHERE YOU CHOOSE WHERE THE FILE WILL SAVE TO
        canvas.setPageSize((canvasSize[0], canvasSize[1]))

        loopIndex = 0

        for i in range(50) :
            
            # checkFileDuplicate(sheetsPath)

            printFileName = str(directory) + '/' + file
            printFile = PdfReader(printFileName).pages[0]
            printFile = pagexobj(printFile)

            # OPEN CANVAS TO BE EDITED
            canvas.saveState()
            
            xPosition = positions[loopIndex][0]
            yPosition = positions[loopIndex][1]

            canvas.resetTransforms()

            # SET POSITION OF NEW STICKER
            canvas.translate(xPosition, yPosition)

            path = canvas.beginPath()
            # path.circle(xPosition + 40.5, yPosition - 40.5, 36)
            path.circle(40.5, 40.5, 36)

            canvas.clipPath(path, stroke=0, fill=0, fillMode=None)

            # if itemSpecs['sku'] != 'White' :
            #     canvas.setFillColor(RDG_WHITE, alpha=1)
            #     whiteSpot = canvas.circle(40.5, 40.5, 36, stroke=0, fill=1)
            #     canvas.setFillColorCMYK(0, 0, 0, 0, alpha=None)

            # PLACE PRINT FILE
            canvas.doForm(makerl(canvas, printFile))

            # CLOSE CANVAS, SIGNIFYING WE ARE DONE EDITING
            canvas.restoreState()

            loopIndex = loopIndex + 1

            if loopIndex == 50 :
                # canvas.restoreState()
                slogPrint(' - Bottlecap 50UP sheet generated for order ' + itemSpecs['order'])
                break

        canvas.save()

###########################################################
# PHOTOSHOP COM HOOK ######################################
def hookPhotoshop() :
    import win32com.client as client # Hooks into Photoshop
    try:
        app = client.gencache.EnsureDispatch('Photoshop.Application')
        slogPrint(' - Successfully hooked Photoshop.')
        return app
    except AttributeError:
        slogPrint(' - Photoshop hook failed. Clearing app cache and retrying...')
        # Corner case dependencies.
        import re
        import sys
        import shutil
        # Remove cache and try again.
        MODULE_LIST = [m.__name__ for m in sys.modules.values()]
        for module in MODULE_LIST:
            if re.match(r'win32com\.gen_py\..+', module):
                del sys.modules[module]
        shutil.rmtree(os.path.join(os.environ.get('LOCALAPPDATA'), 'Temp', 'gen_py'))
        from win32com import client
        app = client.gencache.EnsureDispatch('Photoshop.Application')
        slogPrint(' - Successfully hooked Photoshop.')
        return app