 ######  #### ######## ########     ###    ########   #######  ##     ## 
##    ##  ##     ##    ##     ##   ## ##   ##     ## ##     ##  ##   ##  
##        ##     ##    ##     ##  ##   ##  ##     ## ##     ##   ## ##   
##        ##     ##    ########  ##     ## ########  ##     ##    ###    
##        ##     ##    ##   ##   ######### ##     ## ##     ##   ## ##   
##    ##  ##     ##    ##    ##  ##     ## ##     ## ##     ##  ##   ##  
 ######  ####    ##    ##     ## ##     ## ########   #######  ##     ## 

# --------------------------------------------------------------------- #
# Renamer Module for CitraBox v3
# Module Version: 1.02
# Author: John Sam Fuchs - www.samoe.me/code
# --------------------------------------------------------------------- #

import json, os, shutil
from math import floor
from toolbox import SiteFlow
from os.path import exists
from toolbox.sLog import *
import time

# Initialize Variables
global directory
directory = ''

# Assign Variables
orderCachePath = (os.path.dirname(__file__) + '/orderCache.json')
orderCache = []
totalBarcodes = []
totalItems = []
issueStickers = []
checkForCutLines = True
skuIndex = 1

class NewItem() :
    def __init__(self) :
        self.filePath = str
        self.barcode = str
        self.order = str
        self.sku = str
        self.type = str
        self.width = str
        self.height = str
        self.quantity = str
        self.options = str

with open(orderCachePath, 'r') as f:
    try:
        orderCache = json.load(f)
        print('Order cache loaded.')
    except: print('Cache empty. Building new cache.')

def CheckForSpotColors(item, backLabel) :
    global directory

    issuesPath = directory + '/issuesDetected'

    itemFilePath = item.filePath

    if item.type == 'Sticker' and backLabel == 'PRINT':
 
        s = open(itemFilePath, 'rb').read()
        kissCutCheck = s.__contains__(b'/CutContour')
        thruCutCheck = s.__contains__(b'/PerfCutContour')

        if kissCutCheck == False:
            slogPrint(" --- No CutContour path found in " + str(item.order) + '_' + str(item.sku))

            if not os.path.isdir(issuesPath):
                os.mkdir(issuesPath)

            errorFile = itemFilePath[:-4] + '_NoKissCut.pdf'
            os.rename(itemFilePath, errorFile)
            itemFilePath = shutil.move(errorFile, issuesPath)

        if thruCutCheck == False:
            slogPrint(" --- No PerfCutContour path found in " + str(item.order) + '_' + str(item.sku))

            if not os.path.isdir(issuesPath):
                os.mkdir(issuesPath)

            errorFile = itemFilePath[:-4] + '_NoThruCut.pdf'
            os.rename(itemFilePath, errorFile)

            try:
                shutil.move(errorFile, issuesPath)
            except:
                slogPrint(' --- File is already in the issue folder. File is likely missing both CutContour and PerfCutContour.')

def CheckForDuplicates(item, newFilePath, index, backLabel='') :
    if os.path.exists(directory + '/' + newFilePath) == True:
        if item.type == 'Cap' :
            if index > 1 :
                item.options = item.options[:-2] + '_' + str(index)
            else :
                item.options = item.options + '_' + str(index)
            newFilePath = RenameFile(item, directory, backLabel=backLabel, duplicateCheck=False, rename=False, spotColorCheck=False)
            index += 1
            CheckForDuplicates(item, newFilePath, index)
        else :
            if item.sku.__contains__('-' + str(index - 1)) :
                item.sku = item.sku[:-2] + '-' + str(index)
            else :
                item.sku = item.sku + '-' + str(index)
            newFilePath = RenameFile(item, directory, backLabel=backLabel, duplicateCheck=False, rename=False, spotColorCheck=False)
            index += 1
            CheckForDuplicates(item, newFilePath, index, backLabel)
    else :
        newFilePath = directory + '/' + newFilePath
        
        global newFile
        newFile = newFilePath

        return newFilePath

def RenameFile(item, directory1, backLabel='', rename = True, duplicateCheck = True, spotColorCheck = True) :

    global directory
    directory = directory1
    
    global newFile

    if item.options != '' :
        options = '_' + item.options
    else :
        options = ''

    if item.type == 'Sticker' :
        newFile = str(item.order) + '_' + str(item.sku) + options + '_' + str(item.width) + 'x' + str(item.height) + '_qty ' + str(item.quantity) + '_' + backLabel + '.pdf'
    elif item.type == 'Tile' :
        newFile = 'TILE_' + str(item.order) + '_' + str(item.sku) + options + '_qty ' + str(item.quantity) + '_' + backLabel + '.pdf'
    elif item.type == 'Tile Distressed' :
        newFile = 'TILE DISTRESSED_' + str(item.order) + '_' + str(item.sku) + '_qty ' + str(item.quantity) + '_' + backLabel + '.pdf'
    elif item.type == 'Magnet' :
        newFile = str(item.order) + '_' + str(item.sku) + options + '_Magnet_' + str(item.width) + 'x' + str(item.height) + '_qty ' + str(item.quantity) + '_' + backLabel + '.pdf'
    elif item.type == 'Cap' :
        newFile = 'CAPS 50up_' + str(item.order) + options + '_qty ' + str(item.quantity) + '_' + backLabel + '.pdf'
    elif item.type == 'MetalRound' :
        newFile = 'ROUND_' + str(item.order) + '_' + str(item.sku) + '_qty ' + str(item.quantity) + '_' + backLabel + '.pdf'
    elif item.type == 'MetalLandscape' :
        newFile = 'METAL_' + str(item.order) + '_' + str(item.sku) + '_qty ' + str(item.quantity) + '_13x11.5_' + backLabel + '.pdf'

    if duplicateCheck == True :
        newFile = CheckForDuplicates(item, newFile, 1, backLabel)

    if rename == True :
        oldFile = directory + '/' + item.filePath
        newFile = RenameFile(item, directory, backLabel, rename=False, duplicateCheck=False, spotColorCheck=False)
        newFile = directory + '/' + newFile
        os.rename(oldFile, newFile)

    if spotColorCheck == True and item.type == 'Sticker' :
        item.filePath = newFile
        CheckForSpotColors(item, backLabel)

    return newFile

###############################################################
def ItemBuilderSticker(barcode, orderData, subbatch, bypassSubbatch = False, itemIndex = 0) :

    if bypassSubbatch == True:
        itemData = orderData['orderData']['items'][itemIndex]

        orderNumber = orderData['orderData']['sourceOrderId']

            # PARSE PRODUCT TYPE
        if itemData['components'][0]['attributes']['substrate'] == 'Magnet' :
                productType = 'Magnet'
        else : productType = 'Sticker'

        sku = itemData['components'][0]['attributes']['Customer_SKU']
        if sku == True :
            sku = 'NoSKU'
        elif sku.find('/') != -1 :
            sku = sku.split('/')
            sku = sku[0] + sku[1]

        # CHECK FOR DYNAMIC CANVAS
        if str(itemData["components"][0]["attributes"]["Catfish_ME_Canvas"][0:7]) == 'Dynamic' :
            width = str(itemData["components"][0]["attributes"]["Catfish_ME_Canvas"][8:9])
            height = str(itemData["components"][0]["attributes"]["Catfish_ME_Canvas"][8:9])

        else:
            # PARSE WIDTH
            width = str(itemData["components"][0]["attributes"]["Catfish_ME_Width"])
            if width[1:4] == '.00': # size always comes through as "4.00"
                width = (width[0])
            else : width = width[0:2] # if it is a fraction, use that

            # PARSE HEIGHT
            height = str(itemData["components"][0]["attributes"]["Catfish_ME_Height"])
            if height[1:4] == '.00':
                height = (height[0])
            else : height = height[0:2]

        # CREATE ITEM
        item = NewItem()
        item.order = orderNumber
        item.sku = sku
        item.type = productType
        item.quantity = itemData["printQuantity"]
        item.options = ''
        item.height = height
        item.width = width

        return item

    for j in orderData["orderData"]["items"] :

        if j["components"][0]["_id"] == subbatch['batchedBy']['componentId']:
            
            global directory
            for file in os.listdir(directory) :
                if file.__contains__(barcode) :
                    filePath = file

            orderNumber = orderData["orderData"]["sourceOrderId"]

            if str(j['components'][0]['attributes']['Catfish_ME_Canvas']) == 'True' :
                
                sku = j['components'][0]['attributes']['Customer_SKU']

                # CREATE ITEM
                item = NewItem()
                item.filePath = filePath
                item.barcode = barcode
                item.order = orderNumber
                item.sku = sku
                item.type = 'Sticker'
                item.width = '1'
                item.height = '1'
                item.quantity = j["printQuantity"]
                item.options = ''

                return item

            # CHECK FOR DYNAMIC CANVAS
            if str(j["components"][0]["attributes"]["Catfish_ME_Canvas"][0:7]) == 'Dynamic' :
                width = str(j["components"][0]["attributes"]["Catfish_ME_Canvas"][8:9])
                height = str(j["components"][0]["attributes"]["Catfish_ME_Canvas"][8:9])

            else:
                # PARSE WIDTH
                width = str(j["components"][0]["attributes"]["Catfish_ME_Width"])
                if width[1:4] == '.00': # size always comes through as "4.00"
                    width = (width[0])
                else : width = width[0:2] # if it is a fraction, use that

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

            options = ''
            if j["components"][0]["attributes"]["Options"] != 'SoftTouchLam' :
                options = j["components"][0]["attributes"]["Options"]

            slogPrint(' - Processing sticker: ' + orderNumber + ' | ' + sku + ' (Barcode ' + barcode + ')')
        
            # CREATE ITEM
            item = NewItem()
            item.filePath = filePath
            item.barcode = barcode
            item.order = orderNumber
            item.sku = sku
            item.type = productType
            item.width = width
            item.height = height
            item.quantity = j["printQuantity"]
            item.options = options

            return item

def ItemBuilderTile(barcode, orderData, subbatch) :

    for j in orderData["orderData"]["items"] :

        if j["components"][0]["_id"] == subbatch['batchedBy']['componentId']:
            
            global directory
            for file in os.listdir(directory) :
                if file.__contains__(barcode) :
                    filePath = file

            orderNumber = orderData["orderData"]["sourceOrderId"]
            productType = 'Tile'

            # PARSE SKU
            if j["sku"][0:4] != 'GROG' :
                sku = j["components"][0]["attributes"]["Customer_SKU"]
                if sku == True :
                    sku = 'NoSKU'
                elif sku.find('/') != -1 :
                    sku = sku.split('/')
                    sku = sku[0] + sku[1]
            else : sku = 'GROG'
            
            if sku == 'GROG' :
                if j["components"][0]["attributes"]["Options"].__contains__('Distressed') :
                    productType = 'Tile Distressed'

            slogPrint(' - Processing Tile: ' + orderNumber + ' | ' + sku + ' (Barcode ' + barcode + ')')

            # CREATE ITEM
            item = NewItem()
            item.filePath = filePath
            item.barcode = barcode
            item.order = orderNumber
            item.sku = sku
            item.type = productType
            item.quantity = j["printQuantity"]
            item.options = ''

            return item

def ItemBuilderMetal(barcode, orderData, subbatch, bypassSubbatch=False, itemIndex=0) :

    if bypassSubbatch == True:
        itemData = orderData['orderData']['items'][itemIndex]

        orderNumber = orderData['orderData']['sourceOrderId']
        if itemData['productDescription'].__contains__('Landscape') :
            productType = 'MetalLandscape'
        elif itemData['productDescription'].__contains__('Round') :
            productType = 'MetalRound'

        sku = itemData['components'][0]['attributes']['Customer_SKU']
        if sku == True :
            sku = 'NoSKU'
        elif sku.find('/') != -1 :
            sku = sku.split('/')
            sku = sku[0] + sku[1]

        # CREATE ITEM
        item = NewItem()
        item.order = orderNumber
        item.sku = sku
        item.type = productType
        item.quantity = itemData["printQuantity"]
        item.options = ''

        return item

    # if subbatch["productName"].__contains__("Landscape") :
    #     for j in orderData["orderData"]["items"] :
            # if j["productId"] == subbatch['productId']:
            
            # if j['components'][0]['_id'] == subbatch['batchedBy']['componentId'] :
                
            #     global directory
            #     for file in os.listdir(directory) :
            #         if file.__contains__(barcode) :
            #             filePath = file

            #     orderNumber = orderData["orderData"]["sourceOrderId"]
            #     productType = 'MetalLandscape'

            #     sku = j["components"][0]["attributes"]["Customer_SKU"]
            #     if sku == True :
            #         sku = 'NoSKU'
            #     elif sku.find('/') != -1 :
            #         sku = sku.split('/')
            #         sku = sku[0] + sku[1]

            #     slogPrint(' - Processing Metal Sign: ' + orderNumber + ' | ' + sku + ' (Barcode ' + barcode + ')')

            #     # CREATE ITEM
            #     item = NewItem()
            #     item.filePath = filePath
            #     item.barcode = barcode
            #     item.order = orderNumber
            #     item.sku = sku
            #     item.type = productType
            #     item.quantity = j["printQuantity"]
            #     item.options = ''

            #     return item

    if subbatch['productName'].__contains__('SIGN_001') :

        orderSubbatches = SiteFlow.get_subbatch_by_order(orderData['_id'])
        orderSubbatches = json.loads(orderSubbatches.text)

        for j in orderData["orderData"]["items"] :
            if j["productId"] == subbatch['productId']:
            # if j['components'][0]['_id'] == subbatch['batchedBy']['componentId'] :
                
                for file in os.listdir(directory) :
                    if file.__contains__(barcode) :
                        filePath = file

                orderNumber = orderData["orderData"]["sourceOrderId"]
                productType = 'MetalLandscape'

                try :
                    sku = j["components"][0]["attributes"]["Customer_SKU"]
                except : sku = 'GROG'
                if sku == True :
                    sku = 'NoSKU'
                elif sku.find('/') != -1 :
                    sku = sku.split('/')
                    sku = sku[0] + sku[1]

                slogPrint(' - Processing Metal Sign: ' + orderNumber + ' | ' + sku + ' (Barcode ' + barcode + ')')

                # CREATE ITEM
                item = NewItem()
                item.filePath = filePath
                item.barcode = barcode
                item.order = orderNumber
                item.sku = sku
                item.type = productType
                item.quantity = j["printQuantity"]
                item.options = ''

                return item

    elif subbatch["productName"].__contains__("Round") :
        for j in orderData["orderData"]["items"] :
            
            try:
                if j["components"][0]["_id"] == subbatch['batchedBy']['componentId']:

                    for file in os.listdir(directory) :
                        if file.__contains__(barcode) :
                            filePath = file

                    orderNumber = orderData["orderData"]["sourceOrderId"]
                    productType = 'MetalRound'

                    # PARSE SKU
                    try :
                        sku = j["components"][0]["attributes"]["Customer_SKU"]
                        if sku == True :
                            sku = 'NoSKU'
                        elif sku.find('/') != -1 :
                            sku = sku.split('/')
                            sku = sku[0] + sku[1]
                    except : sku = 'GROG'
                    

                    slogPrint(' - Processing Metal Sign: ' + orderNumber + ' | ' + sku + ' (Barcode ' + barcode + ')')

                    # CREATE ITEM
                    item = NewItem()
                    item.filePath = filePath
                    item.barcode = barcode
                    item.order = orderNumber
                    item.sku = sku
                    item.type = productType
                    item.quantity = j["printQuantity"]
                    item.options = ''

                    return item
            
            except:
                print('Key error')
                continue

def ItemBuilderCap(barcode, orderData, subbatch) :

    for j in orderData["orderData"]["items"] :

        if subbatch['thumbnailUrl'].find(j["components"][0]["fileId"]) != -1 :

            global directory
            for file in os.listdir(directory) :
                if file.__contains__(barcode) :
                    filePath = file

            # PARSE SKU
            options = j["components"][0]["attributes"]["Options"]
            options = options.split(' ')[0]

            productType = 'Cap'
            orderNumber = orderData["orderData"]["sourceOrderId"]

            slogPrint(' - Processing Bottlecap: ' + orderNumber + ' | ' + options + ' (Barcode ' + barcode + ')')

            # CREATE ITEM
            item = NewItem()
            item.filePath = filePath
            item.barcode = barcode
            item.order = orderNumber
            item.type = productType
            item.quantity = j["printQuantity"]
            item.options = options
            
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

    itemIndex = floor(orderData["files"].index(fileID) / 2)
    itemDesc = orderData['orderData']['items'][itemIndex]['productDescription']

    barcode = ''
    subbatch = ''

    if itemDesc.__contains__('Vinyl') :
        item = ItemBuilderSticker(barcode, orderData, subbatch, bypassSubbatch=True, itemIndex=itemIndex)
    elif itemDesc.__contains__('Tile') :
        item = ItemBuilderTile(barcode, orderData, subbatch)
    elif itemDesc.__contains__('Caps') :
        item = ItemBuilderCap(barcode, orderData, subbatch)
    elif itemDesc.__contains__('Metal') :
        item = ItemBuilderMetal(barcode, orderData, subbatch, bypassSubbatch=True, itemIndex=itemIndex)
    
    return item

def MakeNameFromItem(item, directory, backLabel):
    item.options = ''
    return RenameFile(item, directory, backLabel, spotColorCheck=False, rename=False)



    # if item.type == 'Cap' :
    #     newFile = 'CAP_' + str(item.order) + '_' + str(item.sku) + '_qty ' + str(item.quantity) + '_' + backLabel + '.pdf'

    # else:
    #     newFile = str(item.order) + '_' + str(item.sku) + options + '_' + str(item.width) + 'x' + str(item.height) + '_qty ' + str(item.quantity) + '_' + backLabel + '.pdf'
    # return newFile

def fileNameParser(filename):
    width = 0
    height = 0
    filename = str(filename).split('/')[0]
    if filename.startswith('TILE') :
        orderNumber = filename.split('_')[1]
        skuNumber = filename.split('_')[2]
        if skuNumber.__contains__('-') :
            skuNumber.replace('-', '')
    elif filename.startswith('CAP') and not filename.startswith('CAPS') :
        orderNumber = filename.split('_')[1]
        skuNumber = filename.split('_')[2]
    elif filename.startswith('CAPS 50up') :
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

    if quantityfile.__contains__('.pdf') :
        quantityfile = quantityfile[:-4]

    itemSpecs = {
        'order' : orderNumber,
        'sku' : skuNumber,
        'width' : width,
        'height' : height,
        'quantity' : quantityfile
    }
    return itemSpecs

############################################################

def ParseFolder(params) :

    if params['Directory'] == '' :
        slogPrint(' - No directory selected.')
        return

    global startTime
    startTime = time.time()

    global directory
    directory = params['Directory']
    totalBarcodes = []
    totalFileIDs = []

    for file in os.listdir(directory):
        if file.find('barcode-') != -1:
            barcode = (file.split('barcode-')[1])[0:10]
            if barcode not in totalBarcodes :
                totalBarcodes.append(barcode)
        else :
            if len(file) == 28 :
                fileID = file[:-4]
                if fileID not in totalFileIDs :
                    totalFileIDs.append(fileID)

    slogPrint('\n - Searching ' + directory + ' for files to rename.')

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

    for i in totalFileIDs:
        item = ItemBuilderFileID(i)
        totalItems.append(item)
    
    for i in totalItems :
        for file in os.listdir(directory) :
            if file.__contains__(i.barcode) :

                if file.endswith('1.pdf') or file.endswith('TICKET.pdf') :
                        i.filePath = file
                        RenameFile(i, directory, backLabel='TICKET')

                elif file.endswith('2.pdf') or file.endswith('PRINT.pdf') :
                        i.filePath = file
                        RenameFile(i, directory, backLabel='PRINT')

    slogPrint(' - (' + str(len(totalItems)) + ') items renamed in ' + directory)
    endTime = time.time()
    timerResult = round(endTime - startTime, 2)
    slogPrint(' - Execution took ' + str(timerResult) + ' seconds.')

    with open(orderCachePath, 'w', encoding='utf-8') as f:
        json.dump(orderCache, f, ensure_ascii=False, indent=4)