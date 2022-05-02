from tkinter.filedialog import Directory
import win32api, json, urllib
import toolbox.SiteFlow as SiteFlow
import toolbox.Renamer as Renamer
import toolbox.Renamer2 as Renamer2
from toolbox.sLog import slogPrint
# import toolboxGUI2 as GUI

def downloadSticker(directory, downloadOrderText, downloadSkuText, downloadTicketBool, customQty = None):

    if directory == '' :
        slogPrint(' - ERROR: No download location selected.')
        return

    order = downloadOrderText.get()
    if len(str(order)) != 5 :
        slogPrint(' - ERROR: Invalid order number. Must be 5 digits.')
        return

    sku = downloadSkuText.get()
    # if len(str(sku)) < 5 :
    #     print('ERROR: Invalid SKU number. Must be 5 or more digits.')
    #     win32api.MessageBox(0, 'Invalid SKU number. Must be 5 or more digits.')
    #     return

    slogPrint(' - Starting download. Please wait...')
    get_item_by_Order_and_SKU(directory, order, sku, downloadSkuText, downloadTicketBool, customQty = customQty)

def get_item_by_Order_and_SKU(directory, order, sku, downloadSkuText, downloadTicketBool, customQty = None):
    downloadSkuText.delete(0, len(downloadSkuText.get()))
    index = 0
    downloadQueue = []

    orderData = SiteFlow.get_order_by_sourceID(order)
    
    if orderData.status_code != 200 : # Error catching for incorrect PrintOS data
        slogPrint(' - ERROR: Order not found in PrintOS.')
        return

    orderData = json.loads(orderData.text)

    orderData = SiteFlow.get_order(orderData["data"][0]["_id"])
    orderData = json.loads(orderData.text)

    if len(sku) == 6 and sku.startswith('21'): # Is the operator renaming a charles products sticker with a weird SKU but they forgot the slash? Add that baby back in there.
        sku0 = str(sku)[0:2]
        sku1 = str(sku)[2:6]
        sku = sku0 + '/' + sku1
        slogPrint(" - Charles Products SKU detected but operator didn't include the slash. Adding '/' after the first two digits of the SKU.")

    if str.lower(sku) == 'caps':
        slogPrint(' - Downloading all Bottlecap files from order ' + orderData['orderData']['sourceOrderId'])
        for s in orderData["orderData"]["items"] :
            if s['productDescription'] == 'Bottle Caps' :
                fileID = (s["components"][0]["fileId"])
                for n in orderData["files"] :
                    if n == fileID :
                        newFileID = n
                        downloadQueue.append(n)
                        
                newFile = SiteFlow.download_file(newFileID)
                infotechIndex = orderData["files"].index(newFileID) - 1
                newFileName = Renamer.ItemBuilderFileID(newFileID)

                if customQty != None :
                    newFileName.quantity = customQty
                        
                newFileName = Renamer.MakeNameFromItem(newFileName, 'PRINT')
                saveDest = directory + '/' + newFileName
                content = urllib.request.urlopen(newFile.text)

                if index >= 1 :
                    saveDest = saveDest[:-4] + '-' + str(index) + '.pdf'

                f = open(saveDest, 'wb')
                f.write(content.read())
                f.close()
                slogPrint(' - Success! File saved to ' + saveDest )

                index = index + 1

    elif str.lower(sku) == 'stickers' or str.lower(sku) == 'sticker':
        slogPrint(' - Downloading all Sticker files from order ' + orderData['orderData']['sourceOrderId'])
        for s in orderData["orderData"]["items"] :
            if s['productDescription'].__contains__('Vinyl') :
                fileID = (s["components"][0]["fileId"])
                for n in orderData["files"] :
                    if n == fileID :
                        newFileID = n
                        downloadQueue.append(n)

        for d in downloadQueue :
                        newFile = SiteFlow.download_file(d)
                        newFileName = Renamer2.ItemBuilderFileID(d)

                        if customQty != None :
                            newFileName.quantity = customQty
                            
                        newFileName = Renamer2.MakeNameFromItem(newFileName, directory, 'PRINT')

                        saveDest = newFileName
                        content = urllib.request.urlopen(newFile.text)

                        if index >= 1 :
                            saveDest = saveDest[:-4] + '-' + str(index) + '.pdf'

                        f = open(saveDest, 'wb')
                        f.write(content.read())
                        f.close()
                        slogPrint(' - Success! File saved to ' + saveDest)

                        index = index + 1

                        infotechIndex = orderData["files"].index(d) - 1
                        if downloadTicketBool.get() == 1 :
                            newFile = SiteFlow.download_file(orderData["files"][infotechIndex])
                            newFileName = newFileName[:-10] + '_TICKET.pdf'
                            saveDest = directory + '/' + newFileName
                            content = urllib.request.urlopen(newFile.text)
                            f = open(saveDest, 'wb')
                            f.write(content.read())
                            f.close()
                            slogPrint(' - Success! Ticket saved to ' + saveDest + ' ---\n')
    
    elif str.lower(sku) == 'metals' or str.lower(sku) == 'metal':
        slogPrint(' - Downloading all Metal Sign files from order ' + orderData['orderData']['sourceOrderId'])
        for s in orderData["orderData"]["items"] :
            if s['productDescription'].__contains__('Metal') :
                fileID = (s["components"][0]["fileId"])
                for n in orderData["files"] :
                    if n == fileID :
                        newFileID = n
                        downloadQueue.append(n)

                        newFile = SiteFlow.download_file(newFileID)
                        newFileName = Renamer2.ItemBuilderFileID(newFileID)

                        if customQty != None :
                            newFileName.quantity = customQty

                        newFileName = Renamer2.MakeNameFromItem(newFileName, directory, 'PRINT')

                        saveDest = newFileName
                        content = urllib.request.urlopen(newFile.text)

                        if index >= 1 :
                            saveDest = saveDest[:-4] + '-' + str(index) + '.pdf'

                        f = open(saveDest, 'wb')
                        f.write(content.read())
                        f.close()
                        slogPrint(' - Success! File saved to ' + saveDest)

                        index = index + 1

                

    else: 
        for s in orderData["orderData"]["items"] :
            if sku == s["components"][0]["attributes"]["Customer_SKU"] :
                fileID = (s["components"][0]["fileId"])
                for n in orderData["files"] :
                    if n == fileID :
                        newFileID = n
                newFile = SiteFlow.download_file(newFileID)
                infotechIndex = orderData["files"].index(newFileID) - 1
                newFileName = Renamer.ItemBuilderFileID(newFileID)

                if customQty != None :
                    newFileName.quantity = customQty

                newFileName = Renamer.MakeNameFromItem(newFileName, 'PRINT')
                saveDest = directory + '/' + newFileName
                content = urllib.request.urlopen(newFile.text)

                f = open(saveDest, 'wb')
                f.write(content.read())
                f.close()
                slogPrint(' - Success! File saved to ' + saveDest )

                if downloadTicketBool.get() == 1 :
                    newFile = SiteFlow.download_file(orderData["files"][infotechIndex])
                    newFileName = newFileName[:-10] + '_TICKET.pdf'
                    saveDest = directory + '/' + newFileName
                    content = urllib.request.urlopen(newFile.text)
                    f = open(saveDest, 'wb')
                    f.write(content.read())
                    f.close()
                    slogPrint(' - Success! Ticket saved to ' + saveDest + ' ---\n')

                # Catch instances where one order might contain multiple files that use the same SKU. Downloads all of them.
                if index >= 1 :
                    slogPrint('\n - Multiple items with the same SKU number found. All sticker files sharing SKU ' + str(sku) + ' will be downloaded.\n - Delete whichever files you do not need.')
                index = index + 1