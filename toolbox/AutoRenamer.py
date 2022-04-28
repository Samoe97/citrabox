import json, os, shutil, win32api
from . import SiteFlow
from os.path import exists
from DPGToolbox.sLog import *
import time

import DPGToolbox

# Initialize Variables
global totalBarcodes
global totalItems
global issueStickers
global perfCutErrors
global cutContourErrors
global checkForCutLines
global orderCache
global orderCachePath

global stickerLocation
stickerLocation = 'C:/Users/jfuchs/Dropbox/z_CITRA LF PRINT JOBS TO METRO/TECHSTYLES_CUSTOM SHAPE LABELS/PRINT FILES'

# Assign Variables
orderCachePath = (os.path.dirname(__file__) + '/orderCache.json')
orderCache = []
totalBarcodes = []
totalItems = []
issueStickers = []
perfCutErrors = []
cutContourErrors = []
checkForCutLines = True

class NewItem() :
    barcode = ''
    order = ''
    sku = ''
    type = ''
    width = 0
    height = 0
    quantity = ''
    options = ''

with open(orderCachePath, 'r') as f:
    try:
        orderCache = json.load(f)
        print('Order cache loaded.')
    except: print('Cache empty. Building new cache.')

def ItemBuilderSticker(barcode, orderData, subbatch) :
    skuIndex = 1
    for j in orderData["orderData"]["items"] :
        # if j["components"][0]["_id"] in totalItemIDs :
        if j["components"][0]["_id"] == subbatch['batchedBy']['componentId']:
            
            # CHECK FOR DYNAMIC CANVAS
            if str(j["components"][0]["attributes"]["Catfish_ME_Canvas"][0:7]) == 'Dynamic' :
                width = str(j["components"][0]["attributes"]["Catfish_ME_Canvas"][8:9])
                height = str(j["components"][0]["attributes"]["Catfish_ME_Canvas"][8:9])

            else:
                # PARSE WIDTH
                width = str(j["components"][0]["attributes"]["Catfish_ME_Width"])
                if width[1:4] == '.00':
                    width = (width[0])
                else : width = width[0:2]

                # PARSE HEIGHT
                height = str(j["components"][0]["attributes"]["Catfish_ME_Height"])
                if height[1:4] == '.00':
                    height = (height[0])
                else : height = height[0:2]

            # PARSE SKU
            sku = j["components"][0]["attributes"]["Customer_SKU"]
            if sku == True :
                sku = 'NoSKU'
            elif sku.find('/') != -1 :
                sku = sku.split('/')
                sku = sku[0] + sku[1]

            # PARSE PRODUCT TYPE
            if subbatch['batchedBy']['substrate'] == 'Magnet' :
                productType = 'Magnet'
            else : productType = 'Sticker'

            orderNumber = orderData["orderData"]["sourceOrderId"]
            options = ''
            if j["components"][0]["attributes"]["Options"] != 'SoftTouchLam' :
                options = j["components"][0]["attributes"]["Options"]

            slogPrint(' - Processing sticker: ' + orderNumber + ' | ' + sku + ' (Barcode ' + barcode + ')')
        
            # CREATE ITEM
            item = NewItem()
            item.barcode = barcode
            item.order = orderNumber
            item.sku = sku
            item.type = productType
            item.width = width
            item.height = height
            item.quantity = j["printQuantity"]
            item.options = ''

            for a in totalItems :
                if orderNumber == a.order :
                    if sku == a.sku :
                        slogPrint(' - Duplicate Order/SKU combo found. Adding "-' + str(skuIndex) + '" to SKU number to avoid errors.')
                        item.sku = str(sku) + '-' + str(skuIndex)
                        skuIndex = skuIndex + 1

            return item

def ItemBuilderTile(barcode, orderData, subbatch) :
    skuIndex = 1
    for j in orderData["orderData"]["items"] :
        if j["components"][0]["_id"] == subbatch['batchedBy']['componentId']:
            # PARSE SKU
            if j["sku"][0:4] != 'GROG' :
                sku = j["components"][0]["attributes"]["Customer_SKU"]
                if sku == True :
                    sku = 'NoSKU'
                elif sku.find('/') != -1 :
                    sku = sku.split('/')
                    sku = sku[0] + sku[1]
            else : sku = 'GROG'

            productType = 'Tile'
            orderNumber = orderData["orderData"]["sourceOrderId"]
            options = ''
            if sku == 'GROG' :
                if j["components"][0]["attributes"]["Options"].__contains__('Distressed') :
                    options = 'Distressed'

            slogPrint(' - Processing Tile: ' + orderNumber + ' | ' + sku + ' (Barcode ' + barcode + ')')

            # CREATE ITEM
            item = NewItem()
            item.barcode = barcode
            item.order = orderNumber
            item.sku = sku
            item.type = productType
            item.quantity = j["printQuantity"]
            item.options = options

            for a in totalItems :
                if orderNumber == a.order :
                    if sku == a.sku :
                        slogPrint(' - Duplicate Order/SKU combo found. Adding "-' + str(skuIndex) + '" to SKU number to avoid errors.')
                        item.sku = str(sku) + '-' + str(skuIndex)
                        skuIndex = skuIndex + 1

            return item

def ItemBuilderMetal(barcode, orderData, subbatch) :
    skuIndex = 1
    for j in orderData["orderData"]["items"] :
        if j["components"][0]["_id"] == subbatch['batchedBy']['componentId']:
            # PARSE SKU
            if j["sku"].__contains__('Round') :
                frontLabel = 'Round'
                productType = 'MetalRound'
            elif j["sku"].__contains__('Landscape') :
                frontLabel = 'Metal'
                productType = 'MetalLandscape'
            
            sku = j["components"][0]["attributes"]["Customer_SKU"]
            if sku == 'True' :
                sku = 'NoSKU'
            elif sku.find('/') != -1 :
                sku = sku.split('/')
                sku = sku[0] + sku[1]
            # else : sku = 'GROG'

            
            orderNumber = orderData["orderData"]["sourceOrderId"]
            options = ''

            slogPrint(' - Processing Metal Sign: ' + orderNumber + ' | ' + sku + ' (Barcode ' + barcode + ')')

            # CREATE ITEM
            item = NewItem()
            item.barcode = barcode
            item.order = orderNumber
            item.sku = sku
            item.type = productType
            item.quantity = j["printQuantity"]
            item.options = options

            for a in totalItems :
                if orderNumber == a.order :
                    if sku == a.sku :
                        slogPrint(' - Duplicate Order/SKU combo found. Adding "-' + str(skuIndex) + '" to SKU number to avoid errors.')
                        item.sku = str(sku) + '-' + str(skuIndex)
                        skuIndex = skuIndex + 1

            return item

def ItemBuilderCap(barcode, orderData, subbatch) :
    skuIndex = 1
    for j in orderData["orderData"]["items"] :
        # if j["components"][0]["_id"] == subbatch['batchedBy']['componentId']:
        if subbatch['thumbnailUrl'].find(j["components"][0]["fileId"]) != -1 :
            # PARSE SKU
            options = j["components"][0]["attributes"]["Options"]
            options = options.split(' ')[0]

            productType = 'Cap'
            orderNumber = orderData["orderData"]["sourceOrderId"]

            slogPrint(' - Processing Bottlecap: ' + orderNumber + ' | ' + options + ' (Barcode ' + barcode + ')')

            # CREATE ITEM
            item = NewItem()
            item.barcode = barcode
            item.order = orderNumber
            item.type = productType
            item.quantity = j["printQuantity"]
            item.options = options

            for a in totalItems :
                if orderNumber == a.order :
                    if options == a.options :
                        slogPrint(' - Multiple caps of the same color found in the same order. Adding "-' + str(skuIndex) + '" to SKU number to avoid errors.')
                        item.options = str(options) + '-' + str(skuIndex)
                        skuIndex = skuIndex + 1

            return item

def ItemBuilderFileID(fileID) :
    currentItem = SiteFlow.get_file_by_id(fileID)
    currentItem = json.loads(currentItem.text)
    currentItemID = currentItem["componentId"]

    cacheFound = False
    # GET ORDER INFO SO WE CAN CHECK EACH ITEM
    for o in orderCache :
        if o['_id'] == currentItem['orderId'] :
            orderData = o
            cacheFound = True
    if cacheFound == False:
        orderData = currentItem["orderId"] # GET ITEM ORDER ID
        orderData = SiteFlow.get_order(orderData)
        orderData = json.loads(orderData.text)
        orderCache.append(orderData)

    skuIndex = 1
    for j in orderData["orderData"]["items"] :
        # if j["components"][0]["_id"] in totalItemIDs :
        if j["components"][0]["_id"] == currentItem['componentId']:
            
            # CHECK FOR DYNAMIC CANVAS
            if str(j["components"][0]["attributes"]["Catfish_ME_Canvas"][0:7]) == 'Dynamic' :
                width = str(j["components"][0]["attributes"]["Catfish_ME_Canvas"][8:9])
                height = str(j["components"][0]["attributes"]["Catfish_ME_Canvas"][8:9])

            else:
                # PARSE WIDTH
                width = str(j["components"][0]["attributes"]["Catfish_ME_Width"])
                if width[1:4] == '.00':
                    width = (width[0])
                else : width = width[0:2]

                # PARSE HEIGHT
                height = str(j["components"][0]["attributes"]["Catfish_ME_Height"])
                if height[1:4] == '.00':
                    height = (height[0])
                else : height = height[0:2]

            # PARSE SKU
            if j["productDescription"] == 'Bottle Caps' :
                sku = j["components"][0]["attributes"]["Options"].split(' ')[0]
            else :
                sku = j["components"][0]["attributes"]["Customer_SKU"]
           
            if sku == True :
                if j["components"][0]["attributes"]["Catfish_ME_Canvas"].startswith("William Jessup") :
                    sku = 'WJU'
                else :
                    sku = 'NoSKU'
            elif sku.find('/') != -1 :
                sku = sku.split('/')
                sku = sku[0] + sku[1]

            # PARSE PRODUCT TYPE
            if j['components'][0]['attributes']['substrate'] == 'Magnet' :
                productType = 'Magnet'
            else : productType = 'Sticker'

            orderNumber = orderData["orderData"]["sourceOrderId"]
            options = ''
            if j["productDescription"].find('Tile') == -1:
                if j["components"][0]["attributes"]["Options"] != 'SoftTouchLam' :
                    options = j["components"][0]["attributes"]["Options"]

            slogPrint(' - Processing sticker: ' + orderNumber + ' | ' + sku + ' (File ID: ' + fileID + ')')
        
            # CREATE ITEM
            item = NewItem()
            item.barcode = fileID
            item.order = orderNumber
            item.sku = sku
            item.type = productType
            item.width = width
            item.height = height
            item.quantity = j["printQuantity"]
            item.options = ''

            for a in totalItems :
                if orderNumber == a.order :
                    if sku == a.sku :
                        slogPrint(' - Duplicate Order/SKU combo found. Adding "-' + str(skuIndex) + '" to SKU number to avoid errors.')
                        item.sku = str(sku) + '-' + str(skuIndex)
                        skuIndex = skuIndex + 1

            return item

def MakeNameFromItem(item, backLabel):
    if item.options != '' :
        options = '_' + item.options
    else :
        options = ''
    newFile = str(item.order) + '_' + str(item.sku) + options + '_' + str(item.width) + 'x' + str(item.height) + '_qty ' + str(item.quantity) + '_' + backLabel + '.pdf'
    return newFile

def fileNameParser(filename):
    width = 0
    height = 0
    filename = str(filename).split('/')[0]
    if filename.startswith('TILE') :
        orderNumber = filename[5:10]
        skuNumber = filename[11:16]
        if skuNumber.__contains__('-') :
            skuNumber = filename[11:17]
        if skuNumber.__contains__('_') :
            skuNumber = skuNumber.split('_')[0]
    elif filename.startswith('CAP') and not filename.startswith('CAPS') :
        orderNumber = filename.split('_')[1]
        skuNumber = filename.split('_')[2]
    elif filename.startswith('ROUND') :
        orderNumber = filename.split('_')[1]
        skuNumber = filename.split('_')[2]
    else:
        orderNumber = filename[0:5]
        skuNumber = filename[6:12]
        skuNumber = skuNumber.split('_')[0]
        size = str(filename).split('x')
        width = size[0][-1]
        height = size[1].split('_')[0]
    quantityfile = str(filename).split('_qty ')[1]
    quantityfile = str(quantityfile).split('_')[0]

    itemSpecs = {
        'order' : orderNumber,
        'sku' : skuNumber,
        'width' : width,
        'height' : height,
        'quantity' : quantityfile
    }
    return itemSpecs

############################################################

def ParseFolder() :

    params = {'Directory' : stickerLocation}

    if params['Directory'] == '' :
        slogPrint(' - No directory selected.')
        return

    global startTime
    startTime = time.time()

    directory = params['Directory']
    totalBarcodes = []
    totalFileIDs = []
    for file in os.listdir(directory):
        if file.find('barcode-') != -1:
            barcode = (file.split('barcode-')[1])[0:9]
            if barcode not in totalBarcodes :
                totalBarcodes.append(barcode)
        else :
            if len(file) == 28 :
                fileID = file[:-4]
                if fileID not in totalFileIDs :
                    totalFileIDs.append(fileID)

    slogPrint('\n - Searching through ' + directory + ' for files to rename.')
    totalItems = []
    # FOR EACH BARCODE FOUND IN FOLDER
    for i in totalBarcodes:
        # GET SUBBATCH SO WE CAN GET ORDER INFO
        subbatch = SiteFlow.get_subbatch_by_barcode(i)
        if subbatch.status_code == 204:
            slogPrint(' ---- Barcode ' + barcode + ' is no longer connected to PrintOS. This item was likely already moved forward through PrintOS or is from a reprint batch. Cannot rename this item.')
            issueStickers.append(i)
            continue
        subbatch = json.loads(subbatch.text)

        cacheFound = False
        # GET ORDER INFO SO WE CAN CHECK EACH ITEM
        for o in orderCache :
            if o['_id'] == subbatch['orderId'] :
                orderData = o
                cacheFound = True
        if cacheFound == False:
            orderData = subbatch["orderId"] # GET ITEM ORDER ID
            orderData = SiteFlow.get_order(orderData)
            orderData = json.loads(orderData.text)
            orderCache.append(orderData)

        ######## ITEM BUILDER #########
        if subbatch['productName'].__contains__('Vinyl') :
            item = ItemBuilderSticker(i, orderData, subbatch)
            totalItems.append(item)
        elif subbatch['productName'].__contains__('Tile') :
            item = ItemBuilderTile(i, orderData, subbatch)
            totalItems.append(item)
        elif subbatch['productName'].__contains__('Caps') :
            item = ItemBuilderCap(i, orderData, subbatch)
            totalItems.append(item)
        elif subbatch['productName'].__contains__('Metal') :
            item = ItemBuilderMetal(i, orderData, subbatch)
            totalItems.append(item)
        elif subbatch['batchedBy']['substrate'].__contains__('Magnet') :
            item = ItemBuilderSticker(i, orderData, subbatch)
            totalItems.append(item)
        # elif subbatch['productName'].__contains__('Round') :
            # item = ItemBuilderMetal(i, orderData, subbatch)
            # totalItems.append(item)
    for i in totalFileIDs:
        item = ItemBuilderFileID(i)
        totalItems.append(item)

    duplicateIndex = 1
    for x in totalItems :
        for i in totalItems :
            if i.order == x.order and i.sku == x.sku and i != x :
                i.sku = str(i.sku) + '-' + str(duplicateIndex)
                duplicateIndex = duplicateIndex + 1

    for i in totalItems :
        for file in os.listdir(directory):
            if file.endswith('.pdf') :
                if file.find(i.barcode) != -1 :
                    backLabel = ''
                    if len(file) == 28 :
                        backLabel = 'PRINT'
                    elif file.endswith('1.pdf') or file.endswith('TICKET.pdf'):
                        backLabel = 'TICKET'
                    elif file.endswith('2.pdf') or file.endswith('PRINT.pdf'):
                        backLabel = 'PRINT'
                    elif file.startswith('CAP') :
                        backLabel = 'PRINT'
                    
                    if i.options != '' :
                        options = '_' + i.options
                    else :
                        options = ''

                    oldFile = directory + '/' + file
                    if i.type == 'Sticker' :
                        newFile = directory + '/' + str(i.order) + '_' + str(i.sku) + options + '_' + str(i.width) + 'x' + str(i.height) + '_qty ' + str(i.quantity) + '_' + backLabel + '.pdf'
                    elif i.type == 'Tile' :
                        newFile = directory + '/TILE_' + str(i.order) + '_' + str(i.sku) + options + '_qty ' + str(i.quantity) + '_' + backLabel + '.pdf'
                    elif i.type == 'Magnet' :
                        newFile = directory + '/' + str(i.order) + '_' + str(i.sku) + options + '_Magnet' + '_' + str(i.width) + 'x' + str(i.height) + '_qty ' + str(i.quantity) + '_' + backLabel + '.pdf'
                    elif i.type == 'Cap' :
                        newFile = directory + '/CAP_' + str(i.order) + options + '_qty ' + str(i.quantity) + '_' + backLabel + '.pdf'
                    elif i.type == 'MetalRound' :
                        newFile = directory + '/ROUND_' + str(i.order) + '_' + str(i.sku) + '_qty ' + str(i.quantity) + '_' + backLabel + '.pdf'
                    elif i.type == 'MetalLandscape' :
                        newFile = directory + '/METAL_' + str(i.order) + '_' + str(i.sku) + '_qty ' + str(i.quantity) + '_13x11.5_' + backLabel + '.pdf'

                    if os.path.exists(newFile) == True:
                        os.remove(newFile)
                    os.rename(oldFile, newFile)
                    oldFile = newFile

                    # CHECK FOR MISSING CUT LINES
                    if checkForCutLines == True:
                        issuesPath = directory + '/issuesDetected'
                        if i.type == 'Sticker' and backLabel == 'PRINT':
                            s = open(newFile, 'rb').read()
                            kissCutCheck = s.__contains__(b'CutContour')
                            thruCutCheck = s.__contains__(b'PerfCutContour')
                            # kissCutCheck = s.find(b'/Separation /CutContour')
                            # thruCutCheck = s.find(b'/Separation /PerfCutContour')

                            if kissCutCheck == False:
                                slogPrint(" --- No CutContour path found in " + str(i.order) + '_' + str(i.sku))
                                if not os.path.isdir(issuesPath):
                                    os.mkdir(issuesPath)
                                errorFile = newFile[:-4] + '_NoKissCut.pdf'
                                os.rename(newFile, errorFile)
                                newFile = shutil.move(errorFile, issuesPath)
                                cutContourErrors.append(errorFile)

                            if thruCutCheck == False:
                                slogPrint(" --- No PerfCutContour path found in " + str(i.order) + '_' + str(i.sku))
                                if not os.path.isdir(issuesPath):
                                    os.mkdir(issuesPath)
                                errorFile = newFile[:-4] + '_NoThruCut.pdf'
                                os.rename(newFile, errorFile)
                                perfCutErrors.append(errorFile)
                                try: shutil.move(errorFile, issuesPath)
                                except: slogPrint(' --- File is already in the issue folder. File is likely missing both CutContour and PerfCutContour.')
                                ticketFile = oldFile[:-9] + 'TICKET.pdf'
                                shutil.move(ticketFile, issuesPath)

    errorString = ''

    # if len(perfCutErrors) == 1:
    #     perfFilesText = 'file'
    # else : perfFilesText = 'files'
    # if len(cutContourErrors) == 1:
    #     cutFilesText = 'file'
    # else : cutFilesText = 'files'
    # if len(issueStickers) == 1:
    #     issuesText = 'barcode'
    # else: issuesText = 'barcodes'

    # perfError = str(len(perfCutErrors)) + ' print ' + perfFilesText + ' missing PerfCutContour.\n'
    # cutContourError = str(len(cutContourErrors)) + ' print ' + cutFilesText + ' files missing kiss cut.\n'
    # dataError = str(len(issueStickers)) + ' ' + issuesText + ' could not be found in PrintOS.\n'

    # if len(perfCutErrors) > 0: errorString = errorString + perfError
    # if len(cutContourErrors) > 0: errorString = errorString + cutContourError
    # if len(issueStickers) > 0: errorString = errorString + dataError

    if errorString != '':
        win32api.MessageBox(0, errorString, 'DPG Toolbox', 0x00001000)
    else :
        slogPrint(' - (' + str(len(totalItems)) + ') items renamed in ' + directory)
        endTime = time.time()
        timerResult = round(endTime - startTime, 2)
        slogPrint(' - Execution took ' + str(timerResult) + ' seconds.')

        with open(orderCachePath, 'w', encoding='utf-8') as f:
            json.dump(orderCache, f, ensure_ascii=False, indent=4)
    
ParseFolder()