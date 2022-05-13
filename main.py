# CitraBox - A suite of tools for Citra Communications' Large Format department
# DPG Toolbox v3
# Written by John S. Fuchs (www.samoe.me)
# main.py

###########################################################
# REQUIRED IMPORTS ########################################
import os
from sys import maxsize
import webbrowser
from tkinter import *
import tkinter.font as font
from tkinter import filedialog
import time

###########################################################
# DPG TOOLBOX IMPORTS #####################################
import toolbox.GizmoStyle as GizmoStyle
from toolbox.sLog import *
import toolbox.StickerTool2 as Sticker
import toolbox.TileTool2 as Tile
import toolbox.MetalRoundTool2 as MetalRound
import toolbox.SiteFlow as SiteFlow
import toolbox.GraphtecConversion as GraphtecConversion
import toolbox.RollCalculator as RollCalculator
import toolbox.Renamer2 as Renamer
import toolbox.CapTool2 as Cap
import toolbox.Downloader as Downloader
import toolbox.PrintOSAdmin as PrintOS

###########################################################
# REQUIRED TO COMPILE PROJECT TO EXE USING PYINSTALLER ####
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.colors import CMYKColorSep
from pdfrw import PdfReader
from pdfrw.buildxobj import pagexobj
from pdfrw.toreportlab import makerl
from PyPDF2 import PdfFileReader
from decimal import Decimal
import hmac, hashlib, datetime, requests, barcode

###########################################################
# CONSTANTS #---------------------------------------------#

scriptName = 'CITRABOX'
scriptVersion = 'v1.9'
buildDate = '05/01/22'

scriptPath =  os.path.dirname(__file__)
programIcon = scriptPath + '/assets/CitraBox_Logo_720x720.ico'

color_main = "#3D4855"
color_secondary = "#E79F6D"
color_tertiary = '#BF845B'

buttonColors = [
    color_main,
    color_secondary,
    color_tertiary
]

###########################################################
# VARIABLES #---------------------------------------------#

global dirSel
global settingsOpened

dirSel = ''
settingsOpened = False

###########################################################
# INITIALIZE WINDOW #-------------------------------------#

if __name__ == '__main__':

    root = Tk()
    root.title(str(scriptName) + ' - ' + str(scriptVersion) + ' - ' + str(buildDate))
    root.configure(bg = color_main)
    root.minsize(1300, 864)

    root.iconbitmap(programIcon)

    rootFrame = Frame(root, bg = "#FFFFFF", relief = 'flat')
    rootFrame.grid(column = 0, row = 0, sticky = 'NEWS')

    root.grid_rowconfigure(0, weight = 1)
    root.grid_columnconfigure(0, weight = 1)

    slogFrame = Frame(rootFrame, bg = color_main, relief = 'flat')
    slogFrame.grid(column = 2, row = 0, sticky = 'NEWS')

    slogFrame.grid_rowconfigure(0, weight = 1)
    slogFrame.grid_columnconfigure(0, weight = 1)

    fontModuleButton = font.Font(family = 'Avenir', size = 18)
    fontModuleTitle = font.Font(family = 'Avenir Black', size = 20)
    fontModuleVer = font.Font(family = 'Avenir Medium Oblique', size = 12)
    fontModuleDescription = font.Font(family = 'Avenir Medium', size = 12)
    fontSlog = font.Font(family = 'Avenir Light', size = 10)

    rootFrame.grid_columnconfigure(0, weight = 4, minsize = 310)
    rootFrame.grid_columnconfigure(1, weight = 20, minsize = 600)
    rootFrame.grid_columnconfigure(2, weight = 8, minsize = 260)

    rootFrame.grid_rowconfigure(0, weight = 40, minsize = 800)
    rootFrame.grid_rowconfigure(1, weight = 1, minsize = 32)

###########################################################
# PARAMETERS #--------------------------------------------#

    # RENAMER PARAMS
    checkForCutLines = BooleanVar()
    checkForCutLines.set(True)

    # DOWNLOADER PARAMS
    downloadTicketBool = BooleanVar()
    downloadTicketBool.set(False)

    # STICKER SHEET PARAMS
    maxSheetWidth = IntVar()
    maxSheetWidth.set(50)

    maxSheetHeight = IntVar()
    maxSheetHeight.set(32)

    extraStickers = IntVar()
    extraStickers.set(4)

    spaceBetweenStickers = DoubleVar()
    spaceBetweenStickers.set(0.125)

    addCutLineToTicket = BooleanVar()
    addCutLineToTicket.set(True)

    dontIncludeTicketOnSheets = BooleanVar()
    dontIncludeTicketOnSheets.set(False)

    TicketOnlyOnFirstSheet = BooleanVar()
    TicketOnlyOnFirstSheet.set(False)

    archive1UPs = BooleanVar()
    archive1UPs.set(True)

    barcodeConversion = BooleanVar()
    combineRemainders = True
    separatePDFTile = False
    capColorSeparation = True

    # ROLL CALCULATOR PARAMS
    rollLength = IntVar()
    rollLength.set(1580)

###########################################################
# FUNCTION - BROWSE FOR FOLDER #--------------------------#

def BrowseForFolder():
    global dirSel
    dirSel =  filedialog.askdirectory()
    if dirSel != '' :
        slogPrint(' - Location selected: ' + dirSel)
        footerText.config(text = dirSel)
    else :
        slogPrint(' - Directory not set. User cancelled directory selection.')
    return dirSel

###########################################################
# FUNCTIONS - EXECUTE SMART NAME #------------------------#

def RemoteControlRenamer(directory) :
    params = {'Directory' : directory}
    Renamer.ParseFolder(params)

def SelectSmartName():
    smartNameFrameInfo = {
        'name' : 'Smart Name',
        'ver' : 'v1.9',
        'buttonText' : 'Rename Files',
        'description' : 'Smart Name is a tool that takes a folder of PDF files generated by HP PrintOS and renames them with applicable and useful info. Files will only be renamed if they contain a PrintOS barcode in the format "barcode-" followed by a string of numbers and letters. \n\nA file originally named \n\n"TS_4x4 - Batch 29478 -SoftTouchLamMatte Vinyl qty-100 barcode-B6E668419_2.pdf" \n\nwill be renamed to something like \n\n"24557_24586_4x4_qty 100_PRINT.pdf" \n\nOnce a file has been processed by Smart Name, it should be compatible with all the tools in this program.',
        # 'description' : "Smart Name is a tool that takes a folder of PDF files generated by PrintOS and renames them according to their barcode. File names MUST include 'barcode-' followed by a string of numbers and letters. Most other modules in this program will only work on files that have been named using Smart Name.",
        'mainFunc' : ExecuteSmartName,
        'moduleDescriptionTextHeight' : 0,
    }
    ChangeMainContentFrame(smartNameFrameInfo)

def ExecuteSmartName() :
    params = {'Directory' : dirSel}
    Renamer.ParseFolder(params)

###########################################################
# FUNCTIONS - CUT CONVERSION TOOL #-----------------------#

def SelectGraphtecConversion() :
    cutConversionFrameInfo = {
        'name' : 'Graphtec Conversion Tool',
        'ver' : 'v1.1',
        'buttonText' : 'Convert Cut Files',
        'description' : "The Graphtec Conversion Tool takes a folder of XML files that were created specifically for the Graphtec FC8600 and converts them to work with the Graphtec FC9000. This tool assumes that the cut files were generated using the Onyx Cut Server. After converting the XML files, you must place them into the correct folder for your Graphtec FC9000 before they will appear in the Cut Server list.",
        'mainFunc' : ExecuteGraphtecConversion,
        'moduleDescriptionTextHeight' : 4
    }
    ChangeMainContentFrame(cutConversionFrameInfo)

def ExecuteGraphtecConversion() :
    params = {'Directory' : dirSel}

    GraphtecConversion.graphtecConversion8600(params)

###########################################################
# FUNCTIONS - ROLL CALCULATOR #---------------------------#

def SelectRollCalculator():
    rollCalcFrameInfo = {
        'name' : 'Roll Splitting Tool',
        'ver' : 'v1.1',
        'buttonText' : 'Split Files by Roll',
        'description' : "The Roll Splitting Tool takes all files in a folder, calculates their length, then splits them into subfolders based on filling up rolls of vinyl. Folders will be named 'ROLL 1', 'ROLL 2', etc. Roll length to use in calculations can be adjusted in the Settings.",
        'mainFunc' : ExecuteRollCalculator,
        'moduleDescriptionTextHeight' : 2

    }
    ChangeMainContentFrame(rollCalcFrameInfo)

def ExecuteRollCalculator() :
    params = {
        'Directory' : dirSel, 
        'maxRollLength' : rollLength.get()
        }

    RollCalculator.processLength(params)

###########################################################
# FUNCTIONS - STICKER TOOL #------------------------------#

def SelectStickerTool():
    stickerFrameInfo = {
        'name' : 'Sticker Tool',
        'ver' : 'v1.4',
        'buttonText' : 'Create Sticker Sheets',
        'description' : 'The Sticker Tool takes a folder of PDF sticker files that have been processed by Smart Name, then creates print-ready sticker sheets using info found in the filenames. A list of parameters can be changed in Settings at the bottom of the left menu, including max sheet length, extra quantities to add, and more. Sticker Tool will create however many sheets it needs to reach the quantity requested, so a sticker with "qty 500" will likely output as 3-4 sheet files.\n\nBy default, Sticker Tool looks for a "TICKET" file for each sticker, and will place a ticket in the first slot of each sticker sheet. The tool also adds a cut line to the ticket so that it cuts out easily when cutting the entire sticker sheet. See the Settings menu to disable ticket processing, disable the cut line addition only, or try other settings like "Only Place Ticket on First Sheet".',
        'mainFunc' : ExecuteStickerTool,
        'moduleDescriptionTextHeight' : 10,
    }
    ChangeMainContentFrame(stickerFrameInfo)

def ExecuteStickerTool() :
    params = {
            'Directory' : dirSel,
            'ExtraStickers' : extraStickers.get(),
            'SpaceBetweenStickers' : spaceBetweenStickers.get(),
            'MaxSheetHeight' : maxSheetHeight.get(),
            'MaxSheetWidth' : maxSheetWidth.get(),
            'DontIncludeTicket' : dontIncludeTicketOnSheets.get(),
            'TicketOnlyOnFirstSheet' : TicketOnlyOnFirstSheet.get(),
            'Archive1UPs' : archive1UPs.get(),
            'addCutLineToTicket' : addCutLineToTicket.get()
        }
    Sticker.executeStickerSheetGenerator(params)

def RemoteExecuteStickerTool(params) :
    Sticker.executeStickerSheetGenerator(params)

###########################################################
# FUNCTIONS - CERAMIC TILE TOOL #-------------------------#

def SelectCeramicTileTool():
    tileFrameInfo = {
        'name' : 'Ceramic Tile Tool',
        'ver' : 'v1.6',
        'buttonText' : 'Create Tile Sheets',
        'description' : 'The Ceramic Tile Tool takes a folder of PDF tile files that have been processed by Smart Name, then creates print-ready PDF jig files based on info found in the filenames. We fit 8 tiles on each print jig, so if a tile was ordered at a quantity that isn`t divisible by 8, the leftover tiles will be added to a "Remainder" group. After all normal tile jigs have been created, the tool will create sheets with all the Remainder tiles. \n\nIf a file is named something like: \n\n"TILE_25487_35980_qty 25_PRINT.pdf" \n\nThen two files will be created, as follows: \n\n"TILE_25487_35980_qty25_PRINT 3 SHEETS.pdf" \n\n"TILE REM - Order 25487 PRINT.pdf" \n\nThe first file will contain 8 tiles, and the name tells the operator to print it 3 times, giving a total of 24 tiles. The other file includes the 1 remainder tile. If other orders/tiles were processed at the same time, all remainders are grouped together on the same jig for efficiency.',
        'mainFunc' : ExecuteCeramicTile,
        'moduleDescriptionTextHeight' : 0,
    }
    ChangeMainContentFrame(tileFrameInfo)

def ExecuteCeramicTile():
    params = {'Directory' : dirSel}
    Tile.executeTileSheetGeneratorPython(params)

def RemoteExecuteCeramicTile(directory) :
    params = {'Directory' : directory}
    Tile.executeTileSheetGeneratorPython(params)

###########################################################
# FUNCTIONS - METAL ROUND TOOL #--------------------------#

def SelectMetalRoundTool():
    metalFrameInfo = {
        'name' : 'Metal Round Tool',
        'ver' : 'v1.1',
        'buttonText' : 'Create Metal Round Sheets',
        'description' : 'The Metal Round Tool takes a folder of PDF tile files that have been processed by Smart Name, then creates print-ready PDF jig files based on info found in the filenames. We fit 4 metal rounds on each print jig, so if a sign was ordered at a quantity that isn`t divisible by 4, the leftover signs will be added to a "Remainder" group. After all normal metal round jigs have been created, the tool will create sheets with all the Remainder signs. \n\nIf a file is named something like: \n\n"ROUND_25487_35980_qty 15_PRINT.pdf" \n\nThen two files will be created, as follows: \n\n"ROUNDS_25487_35980_qty15_PRINT 3 SHEETS.pdf" \n\n"ROUNDS REM - Order 25487 PRINT.pdf" \n\nThe first file will contain 4 round signs, and the name tells the operator to print it 3 times, giving a total of 12 tiles. The other file includes the 1 remainder sign. If other orders/signs were processed at the same time, all remainders are grouped together on the same jig for efficiency.',
        'mainFunc' : ExecuteMetalRoundTool,
        'moduleDescriptionTextHeight' : 0,
    }
    ChangeMainContentFrame(metalFrameInfo)

def ExecuteMetalRoundTool():
    params = {'Directory' : dirSel}
    MetalRound.executeRoundSheetGeneratorPython(params)

def RemoteExecuteMetalRoundTool(directory) :
    params = {'Directory' : directory}
    MetalRound.executeRoundSheetGeneratorPython(params)

###########################################################
# FUNCTIONS - BOTTLECAP TOOL #----------------------------#

def SelectBottlecapTool():
    bottlecapFrameInfo = {
        'name' : 'Bottlecap Tool',
        'ver' : 'v1.8',
        'buttonText' : 'Create 3UP Cap Sheets',
        'description' : 'The Bottlecap Tool takes a folder of PDF 50up Bottlecap file that have been processed by Smart Name, then creates print-ready PDF jig files based on info found in the filenames. Our VersaUV LEF-300 printer is set up to print 3 50up sheets at a time. If a cap sheet filename says "qty 150" then the tool will put three files onto one jig. If the qty is 200, it will make one jig with 3 files on it, then another jig with only 1 file on it. \n\nIf you are processing multiple bottlecap sheets at once, the tool will group similar colors together, so that you only print white caps with other white caps, green caps with other green caps, etc.',
        'mainFunc' : Execute3UPBottlecap,
        'moduleDescriptionTextHeight' : 6,
    }
    ChangeMainContentFrame(bottlecapFrameInfo)

    bottlecapFrameInfo2 = {
        'name' : 'Bottlecap Tool (50up)',
        'ver' : 'v1.8',
        'buttonText' : 'Create 50up Cap Sheets',
        'description' : 'The 50up Bottlecap Tool should only be used when you have a 1UP cap file and NO sheet file. This tool will take your 1"x1" cap file and impose 50 of them onto a PDF sheet. That sheet can then be used with the 3UP Bottlecap Tool to create print-ready PDF jigs. Please be aware that if a bottlecap is any color other than white, this tool will also attempt to use Adobe Photoshop to add a white ink layer underneath.',
        'mainFunc' : Execute50UPBottlecap,
        'moduleDescriptionTextHeight' : 4,
        'buffer' : False
    }
    contentFrameTemplate(mainContentFrame, bottlecapFrameInfo2['name'], bottlecapFrameInfo2['ver'], bottlecapFrameInfo2['buttonText'], bottlecapFrameInfo2['description'], bottlecapFrameInfo2['mainFunc'], descriptionTextHeight=bottlecapFrameInfo2['moduleDescriptionTextHeight'], buffer = False)

    # Adjustment Settings Frame
    bottlecapAdjustmentFrame = Frame(mainContentFrame, relief = 'flat', bd = 1, bg = "#FFFFFF")

    global capAdjustment1
    capAdjustment1 = IntVar()
    global capAdjustment2
    capAdjustment2 = IntVar()
    global capAdjustment3
    capAdjustment3 = IntVar()
    global capAdjustment4
    capAdjustment4 = IntVar()
    capAdjustmentEntry1 = Entry(bottlecapAdjustmentFrame, font = fontModuleDescription, textvariable=capAdjustment1, width = 3, )
    capAdjustmentEntry1.pack(side = 'left', ipady = 2)
    capAdjustmentEntry2 = Entry(bottlecapAdjustmentFrame, font = fontModuleDescription, textvariable=capAdjustment2, width = 3)
    capAdjustmentEntry2.pack(side = 'right', ipady = 2)
    capAdjustmentEntry3 = Entry(bottlecapAdjustmentFrame, font = fontModuleDescription, textvariable=capAdjustment3, width = 3)
    capAdjustmentEntry3.pack(side = 'top', ipady = 2)
    capAdjustmentEntry4 = Entry(bottlecapAdjustmentFrame, font = fontModuleDescription, textvariable=capAdjustment4, width = 3)
    capAdjustmentEntry4.pack(side = 'bottom', ipady = 2)

    bottlecapAdjustmentFrame.grid()

def Execute3UPBottlecap():

    adjustments = [
        capAdjustment1.get(),
        capAdjustment2.get(),
        capAdjustment3.get(),
        capAdjustment4.get()
    ]

    params = {
        'Directory' : dirSel,
        'adjustment' : adjustments,
        'archive' : False,
    }
    Cap.executeCap3UPSheetGenerator(params)

def RemoteExecute3UPBottlecap(directory) :
    params = {
        'Directory' : directory,
        'adjustment' : [0, 0, 0, 0],
        'archive' : False
    }
    Cap.executeCap3UPSheetGenerator(params)

def Execute50UPBottlecap():
    params = {'Directory' : dirSel}
    Cap.executeCap50upGenerator(params)

###########################################################
# FUNCTIONS - DOWNLOADER TOOL #---------------------------#

def SelectDownloader():

    # INITIALIZE FILE DOWNLOADER FRAME - CUSTOM FRAME TO INSERT INTO THE MAIN CONTENT TEMPLATE
    global downloadOrderText
    global downloadSkuText

    fileDownloaderFrame = Frame(mainContentFrame, relief = 'flat', bd = 1, bg = "#FFFFFF")

    downloadOrderLabel = Label(fileDownloaderFrame, font=fontModuleDescription, text='Order: ', justify='right', bg = "#FFFFFF")
    downloadOrderText = Entry(fileDownloaderFrame, width = 9, font=fontModuleDescription, justify='center')

    downloadSkuLabel = Label(fileDownloaderFrame, font=fontModuleDescription, text='Sku: ', justify='right', bg = "#FFFFFF")
    downloadSkuText = Entry(fileDownloaderFrame, width = 9, font=fontModuleDescription, justify='center')

    # Convenient settings for download panel - bind "ENTER" to dowload and set the text cursor to active in the order field
    root.bind('<Return>',lambda event:ExecuteDownloadSticker())
    downloadOrderText.focus_set()

    downloadTicketCheckbox = Checkbutton(fileDownloaderFrame, text="Download Ticket", fg=color_main, bg="#FFFFFF", selectcolor="#FFFFFF", onvalue=True, offvalue=False, variable=downloadTicketBool)

    downloadOrderLabel.pack(pady=8, padx=4, side=LEFT)
    downloadOrderText.pack(pady=8, padx=4, side=LEFT, ipadx=8, ipady=4)

    downloadSkuLabel.pack(pady=8, padx=4, side=LEFT, ipadx=8)
    downloadSkuText.pack(pady=8, padx=4, side=LEFT, ipadx=8, ipady=4)

    downloadTicketCheckbox.pack(pady=8, padx=4, side=LEFT, ipadx=8, ipady=4)


    global customQuantityBool
    global customDownloadQty

    customQuantityBool = BooleanVar()
    def toggleQtyCheckbox() :
        if customQuantityBool.get() == True :
            downloadQtyText.config(state = 'normal')
        else :
            downloadQtyText.config(state = 'disabled')

    downloadQtyCheckbox = Checkbutton(fileDownloaderFrame, text="Custom Quantity: ", fg=color_main, bg="#FFFFFF", selectcolor="#FFFFFF", onvalue=True, offvalue=False, variable=customQuantityBool, command = toggleQtyCheckbox)
    downloadQtyCheckbox.pack(padx = 4, pady = 8, side = LEFT, ipadx = 8, ipady = 4)

    customDownloadQty = StringVar()
    downloadQtyText = Entry(fileDownloaderFrame, width = 6, font=fontModuleDescription, justify='center', state = 'disabled', textvariable = customDownloadQty)
    downloadQtyText.pack(padx = 4, pady = 8, side = 'left', ipadx = 8, ipady = 4)

    #BY ADDING THE "customFrame" ATTRIBUTE TO THIS OBJECT, OUR FRAME WE JUST CREATED ABOVE WILL BE PACKED INTO THE MAIN CONTENT AREA BEFORE THE MAIN CONTENT TEMPLATE
    downloaderFrameInfo = {
        'customFrame' : fileDownloaderFrame,
        'name' : 'File Downloader',
        'ver' : 'v2.0',
        'buttonText' : 'Download Files',
        'description' : 'The File Downloader allows you to download print files directly from the HP PrintOS server. If you need to quickly reprint a sticker, or accidentally misplaced print files, you can use this tool. \n\nStart by typing in the order number, then type in the SKU for the item you want to download. If you want to download all files from an order for a certain product type, just type that product type. For instance, you can type "stickers" (case insensitive) to download all stickers from an order. \n\nOther product types include "caps", "tiles", and "metal".',
        'mainFunc' : ExecuteDownloadSticker,
        'moduleDescriptionTextHeight' : 4,
    }
    newDownloaderFrame = ChangeMainContentFrame(downloaderFrameInfo)

    fileDownloaderFrame.master(newDownloaderFrame)

def ExecuteDownloadSticker():
    global customQuantityBool
    global customDownloadQty

    if customQuantityBool.get() == True :
        customQty = customDownloadQty.get()
    else :
        customQty = None
    Downloader.downloadSticker(dirSel, downloadOrderText, downloadSkuText, downloadTicketBool, customQty = customQty)

###########################################################
# FUNCTIONS - PRINTOS TOOL #------------------------------#

def SelectPrintOSAdmin():

    # INITIALIZE FILE DOWNLOADER FRAME - CUSTOM FRAME TO INSERT INTO THE MAIN CONTENT TEMPLATE
    global orderPrintOS
    global itemSku

    printOSAdminFrame = Frame(mainContentFrame, relief = 'flat', bg = "#FFFFFF")

    orderPrintOSLabel = Label(printOSAdminFrame, font=fontModuleDescription, text='Order: ', justify='right', bg = "#FFFFFF")
    orderPrintOS = Entry(printOSAdminFrame, width = 9, font=fontModuleDescription, justify='center')

    # itemSkuLabel = Label(printOSAdminFrame, font=fontModuleDescription, text='Sku: ', justify='right', bg = "#FFFFFF")
    # itemSku = Entry(printOSAdminFrame, width = 9, font=fontModuleDescription, justify='center')

    # Convenient settings for download panel - bind "ENTER" to dowload and set the text cursor to active in the order field
    root.bind('<Return>',lambda event:executePushOrderForward())
    orderPrintOS.focus_set()

    orderPrintOSLabel.pack(pady=8, padx=4, side=LEFT)
    orderPrintOS.pack(pady=8, padx=4, side=LEFT, ipadx=8, ipady=4)

    # itemSkuLabel.pack(pady = 8, padx = 4, side = LEFT)
    # itemSku.pack(pady = 8, padx = 4, side = LEFT, ipadx = 8, ipady = 4)

    #BY ADDING THE "customFrame" ATTRIBUTE TO THIS OBJECT, OUR FRAME WE JUST CREATED ABOVE WILL BE PACKED INTO THE MAIN CONTENT AREA BEFORE THE MAIN CONTENT TEMPLATE
    printOSFrameInfo = {
        'customFrame' : printOSAdminFrame,
        'name' : 'PrintOS Admin Tools',
        'ver' : 'v1.0',
        'buttonText' : 'Push Order Forward',
        'description' : 'The PrintOS Admin Tools allow you to quickly and efficiently complete tasks that would normally take longer inside of HP`s own website. Type in an order and press ENTER to move it forward in the Production Queue. \n\ni.e.: If an order is currently in LF PRINT and you have queued it up to print, type in the order number and press ENTER. All batches inside of the order will be moved forward to the next production step, likely LF SHRINKWRAP.',
        'mainFunc' : executePushOrderForward,
        'moduleDescriptionTextHeight' : 4,
    }
    ChangeMainContentFrame(printOSFrameInfo)

def downloadInfotech() :
    orderNum = orderPrintOS.get()
    sku = itemSku.get()
    PrintOS.downloadInfotech(orderNum, sku)

def executePushOrderForward() :
    orderNum = orderPrintOS.get()
    PrintOS.pushOrderForward(orderNum)

def OpenPrintOS():
    slogPrint(' - Opening PrintOS Siteflow')
    webbrowser.open('https://ofui.www.printos.com/#/', new = 0, autoraise = True)

###########################################################

######################################################################################################################
# INITIALIZE GUI ASSETS ##############################################################################################
######################################################################################################################

###########################################################
# CUSTOM BUTTON CLASS #-----------------------------------#

class HoverButton(Label) :

    def on_hover(self, event):
        if self.selected == False :
            if self.images :
                if self.images.hovered[0] != None :
                    self.config(image = self.images.hovered)
            if self.colors :
                self.config(bg = self.colors[1])

    def on_unhover(self, event):
        if self.selected == False :
            if self.images :
                self.config(image = self.images.idle)
            if self.colors :            
                self.config(bg = self.colors[0])
            
    def on_clicked(self, event):
        if self.images :
            if self.images.clicked[0] != None :
                self.config(image = self.images.clicked)
        if self.colors :        
            self.config(self, bg = self.colors[2])
        
        root.update()

        if self.menuButton == True :
            menuButtons = menuFrame.winfo_children()

            for i in menuButtons :
                if i != event.widget :
                    i['image'] = i.images.idle
                    i.config(bg = i.colors[0])
                    i.selected = False

            # time.sleep(0.05)

        if self.command != None :
            self.command()

        if self.selectable == False :
            self.selected = False
            root.after(100, self.on_hover(self))
        else :
            self.selected = True
            if self.images.selected != None :
                self.config(image = self.images.selected)
            if self.colors :
                root.after(50, self.config(bg = self.colors[1]))

    def __init__(self, master, text = None, command = None, colors = buttonColors, images = None, menuButton = False) :
        super(HoverButton, self).__init__(master)
        Label.config(self, text = text, highlightthickness = 0, bd = 0, relief = 'flat', bg = colors[0])

        self.colors = colors
        self.images = images

        if self.images :
            self['image'] = self.images.idle

        self.selectable = False
        self.selected = False
        self.menuButton = menuButton

        self.command = command

        self.bind("<Enter>", self.on_hover)
        self.bind("<Leave>", self.on_unhover)
        self.bind("<Button-1>", self.on_clicked)

def remove(event):
    event.grid_remove()

###########################################################
# CUSTOM FRAME CLASS #------------------------------------#

class moduleFrame(Frame):
    def __init__(self, master, moduleName='', moduleVer='', button1Text='', moduleDescription='', mainFunc=BrowseForFolder, moduleDescriptionTextHeight=8, customFrame=None, **kw):

        self.moduleRootFrame = Frame(master, bg = "#FFFFFF", relief = 'flat', bd = 0)

        self.button1 = Button(self.moduleRootFrame, image = blankButtonImg, bg = "#FFFFFF", relief = 'flat', compound = 'center', font = fontModuleButton, fg = "#FFFFFF")
        self.button1.config(text = button1Text)
        self.button1.grid(pady = 8, ipady = 10, row = 0)
        self.button1.config(command = mainFunc)
        root.bind('<Return>',lambda event:mainFunc())

        if customFrame != None :
            customFrame.grid(pady=4)

        self.moduleTitleFrame = Frame(self.moduleRootFrame, relief = 'flat', bg = "#FFFFFF")
        
        self.moduleTitleText = Label(self.moduleTitleFrame, font = fontModuleTitle, fg = color_main, bg = "#FFFFFF")
        self.moduleTitleText.config(text = moduleName)
        self.moduleTitleText.grid(column = 0, row = 0, sticky = 'sw')

        self.moduleVerText = Label(self.moduleTitleFrame, font=fontModuleVer, fg = color_secondary, bg = "#FFFFFF")
        self.moduleVerText.config(text = moduleVer)
        self.moduleVerText.grid(column = 1, row = 0, sticky = 'se', pady = 8)

        self.moduleHorLine = Frame(self.moduleTitleFrame, bg = color_secondary, height = 2, bd = 0)
        self.moduleHorLine.grid(column = 0, columnspan = 3, row = 1, sticky = 'NWE')

        self.moduleDescriptionText = Text(self.moduleTitleFrame, fg = color_main, bg = "#FFFFFF", font = fontModuleDescription, relief = 'flat', wrap = 'word')
        self.moduleDescriptionText.insert('end', moduleDescription)
        self.moduleDescriptionText.config(height = moduleDescriptionTextHeight, state = 'disabled')
        self.moduleDescriptionText.grid(column = 0, columnspan = 3, row = 2, pady = 8)

        self.moduleTitleFrame.grid(row = 1, padx = 32)

        self.moduleRootFrame.grid(pady=8)

class contentFrameTemplate(Frame):

    def __init__(self, 
        masterFrame,
        moduleName = '',
        moduleVer = '', 
        button1Text = '', 
        moduleDescription = '', 
        mainFunc = '', 
        descriptionTextHeight = 0, 
        customFrame = None,
        buffer = True,
        **kw):

        self.moduleRootFrame = Frame(masterFrame, bg = "#FFFFFF", relief = 'flat', bd = 0)

        self.moduleRootFrame.grid_rowconfigure(0, weight = 1)
        self.moduleRootFrame.grid_rowconfigure(1, weight = 1)
        self.moduleRootFrame.grid_rowconfigure(2, weight = 1)
        self.moduleRootFrame.grid_rowconfigure(3, weight = 1)

        self.moduleRootFrame.grid_columnconfigure(0, weight = 1)

        ##############################################################

        if buffer == True :
            self.titleBuffer = Frame(self.moduleRootFrame, bg = "#FFFFFF", height = 16)
            self.titleBuffer.grid(row = 0)

        ##############################################################

        self.titleFrame = Frame(self.moduleRootFrame, bg = "#FFFFFF")
        self.titleFrame.grid(row = 1, column = 0, pady = 8)

        self.titleFrame.grid_columnconfigure(0, weight = 1)

        self.titleText = Label(self.titleFrame, font = fontModuleTitle, fg = color_main, bg = "white")
        self.titleText.config(text = moduleName)
        self.titleText.grid(column = 0, row = 0, sticky = 'NEW', pady = 4)

        self.horizontalLine = Frame(self.titleFrame, bg = color_secondary, height = 2, bd = 0)
        self.horizontalLine.grid(column = 0, row = 1, sticky = 'NEWS', ipadx = 64)

        ##############################################################

        self.middleFrame = Frame(self.moduleRootFrame, bg = "#FFFFFF")
        self.middleFrame.grid(row = 2, column = 0, sticky = 'NEWS')

        self.middleFrame.grid_columnconfigure(0, weight = 1)
        self.middleFrame.grid_rowconfigure(0, weight = 1)

        self.descriptionText = Text(self.middleFrame, fg = color_main, bg = "#FFFFFF", font = fontModuleDescription, relief = 'flat', wrap = 'word')
        self.descriptionText.pack(fill = "both", expand = True, padx = 32, pady = 8)
        # self.descriptionText.grid(row = 0, padx = 32, pady = 8)
        self.descriptionText.insert('end', moduleDescription)

        newHeight = int(self.descriptionText.index('end-1c').split('.')[0]) + int(descriptionTextHeight)

        # self.descriptionText.bind("<Configure>", resize)

        self.descriptionText.config(height = newHeight, state = 'disabled')

        self.mainButton = Button(self.middleFrame, image = blankButtonImg, bg = "#FFFFFF", relief = 'flat', compound = 'center', font = fontModuleButton, fg = "#FFFFFF")
        self.mainButton.config(text = button1Text)
        # self.mainButton.grid(row = 1)
        self.mainButton.pack()

        self.mainButton.config(command = mainFunc)
        root.bind('<Return>',lambda event:mainFunc())

        ##############################################################

        self.moduleRootFrame.grid(pady = 8, sticky = 'NEWS')

        if customFrame != None :
            # customFrame.config(self.moduleRootFrame)
            customFrame.grid(pady = 4, row = 3)

###########################################################
# images CLASS #-------------------------------------------#

class images() :
        idle = None,
        hovered = None,
        clicked = None,
        selected = None

###########################################################
# INITIALIZE BUTTON IMAGES #------------------------------#

if __name__ == '__main__' :

    images_SelectFolder = images()
    images_SelectFolder.idle = PhotoImage(file = scriptPath + '/assets/Buttons3/button_menu_Browse_idle.png')
    # images_SelectFolder.hovered = PhotoImage(file = scriptPath + '/assets/Buttons3/button_menu_Browse_hovered.png')
    # images_SelectFolder.clicked = PhotoImage(file = scriptPath + '/assets/Buttons3/button_menu_Browse_clicked.png')
    # images_SelectFolder.selected = PhotoImage(file = scriptPath + '/assets/Buttons3/button_menu_Browse_selected.png')

    images_SmartName = images()
    images_SmartName.idle = PhotoImage(file = scriptPath + '/assets/Buttons3/button_menu_SmartName_idle.png')
    # images_SmartName.hovered = PhotoImage(file = scriptPath + '/assets/Buttons3/button_menu_SmartName_hovered.png')
    # images_SmartName.clicked = PhotoImage(file = scriptPath + '/assets/Buttons3/button_menu_SmartName_clicked.png')
    # images_SmartName.selected = PhotoImage(file = scriptPath + '/assets/Buttons3/button_menu_SmartName_selected.png')

    images_convertCutFiles = images()
    images_convertCutFiles.idle = PhotoImage(file = scriptPath + '/assets/Buttons3/button_menu_ConvertCut_idle.png')
    # images_convertCutFiles.hovered = PhotoImage(file = scriptPath + '/assets/Buttons3/button_menu_ConvertCut_hovered.png')
    # images_convertCutFiles.clicked = PhotoImage(file = scriptPath + '/assets/Buttons3/button_menu_ConvertCut_clicked.png')
    # images_convertCutFiles.selected = PhotoImage(file = scriptPath + '/assets/Buttons3/button_menu_ConvertCut_selected.png')

    images_Stickers = images()
    images_Stickers.idle = PhotoImage(file = scriptPath + '/assets/Buttons3/button_menu_Stickers_idle.png')
    # images_Stickers.hovered = PhotoImage(file = scriptPath + '/assets/Buttons3/button_menu_Stickers_hovered.png')
    # images_Stickers.clicked = PhotoImage(file = scriptPath + '/assets/Buttons3/button_menu_Stickers_clicked.png')
    # images_Stickers.selected = PhotoImage(file = scriptPath + '/assets/Buttons3/button_menu_Stickers_selected.png')

    images_CeramicTiles = images()
    images_CeramicTiles.idle = PhotoImage(file = scriptPath + '/assets/Buttons3/button_menu_CeramicTile_idle.png')
    # images_CeramicTiles.hovered = PhotoImage(file = scriptPath + '/assets/Buttons3/button_menu_CeramicTile_hovered.png')
    # images_CeramicTiles.clicked = PhotoImage(file = scriptPath + '/assets/Buttons3/button_menu_CeramicTile_clicked.png')
    # images_CeramicTiles.selected = PhotoImage(file = scriptPath + '/assets/Buttons3/button_menu_CeramicTile_selected.png')

    images_MetalSigns = images()
    images_MetalSigns.idle = PhotoImage(file = scriptPath + '/assets/Buttons3/button_menu_MetalSigns_idle.png')
    # images_MetalSigns.hovered = PhotoImage(file = scriptPath + '/assets/Buttons3/button_menu_MetalSigns_hovered.png')
    # images_MetalSigns.clicked = PhotoImage(file = scriptPath + '/assets/Buttons3/button_menu_MetalSigns_clicked.png')
    # images_MetalSigns.selected = PhotoImage(file = scriptPath + '/assets/Buttons3/button_menu_MetalSigns_selected.png')

    images_SplitFiles = images()
    images_SplitFiles.idle = PhotoImage(file = scriptPath + '/assets/Buttons3/button_menu_SplitFiles_idle.png')
    # images_SplitFiles.hovered = PhotoImage(file = scriptPath + '/assets/Buttons3/button_menu_SplitFiles_hovered.png')
    # images_SplitFiles.clicked = PhotoImage(file = scriptPath + '/assets/Buttons3/button_menu_SplitFiles_clicked.png')
    # images_SplitFiles.selected = PhotoImage(file = scriptPath + '/assets/Buttons3/button_menu_SplitFiles_selected.png')

    images_Bottlecaps = images()
    images_Bottlecaps.idle = PhotoImage(file = scriptPath + '/assets/Buttons3/button_menu_Bottlecaps_idle.png')
    # images_Bottlecaps.hovered = PhotoImage(file = scriptPath + '/assets/Buttons3/button_menu_Bottlecaps_hovered.png')
    # images_Bottlecaps.clicked = PhotoImage(file = scriptPath + '/assets/Buttons3/button_menu_Bottlecaps_clicked.png')
    # images_Bottlecaps.selected = PhotoImage(file = scriptPath + '/assets/Buttons3/button_menu_Bottlecaps_selected.png')

    images_printOS = images()
    images_printOS.idle = PhotoImage(file = scriptPath + '/assets/Buttons3/button_menu_OpenPrintOS_idle.png')
    # images_printOS.hovered = PhotoImage(file = scriptPath + '/assets/Buttons3/button_menu_OpenPrintOS_hovered.png')
    # images_printOS.clicked = PhotoImage(file = scriptPath + '/assets/Buttons3/button_menu_OpenPrintOS_clicked.png')
    # images_printOS.selected = PhotoImage(file = scriptPath + '/assets/Buttons3/button_menu_OpenPrintOS_selected.png')

    images_Settings = images()
    images_Settings.idle = PhotoImage(file = scriptPath + '/assets/Buttons3/button_menu_Settings_idle.png')
    # images_Settings.hovered = PhotoImage(file = scriptPath + '/assets/Buttons3/button_menu_Settings_hovered.png')
    # images_Settings.clicked = PhotoImage(file = scriptPath + '/assets/Buttons3/button_menu_Settings_clicked.png')
    # images_Settings.selected = PhotoImage(file = scriptPath + '/assets/Buttons3/button_menu_Settings_selected.png')

    images_Downloader = images()
    images_Downloader.idle = PhotoImage(file = scriptPath + '/assets/Buttons3/button_menu_DownloadFiles_idle.png')
    # images_Downloader.hovered = PhotoImage(file = scriptPath + '/assets/Buttons3/button_menu_DownloadFiles_hovered.png')
    # images_Downloader.clicked = PhotoImage(file = scriptPath + '/assets/Buttons3/button_menu_DownloadFiles_clicked.png')
    # images_Downloader.selected = PhotoImage(file = scriptPath + '/assets/Buttons3/button_menu_DownloadFiles_selected.png')


    headerImageRef = PhotoImage(file = scriptPath + '/assets/Buttons3/header_Citrabox.png')

    images_Header = images()
    images_Header.idle = PhotoImage(file = scriptPath + '/assets/Buttons3/header_Citrabox.png')
    # images_Header.hovered = PhotoImage(file = scriptPath + '/assets/Buttons3/header_Citrabox_hovered.png')
    # images_Header.clicked = PhotoImage(file = scriptPath + '/assets/Buttons3/header_Citrabox_hovered.png')
    # images_Header.selected = PhotoImage(file = scriptPath + '/assets/Buttons3/header_Citrabox.png')

    blankButtonImg = PhotoImage(file = scriptPath + '/assets/Buttons3/button_MainFunc_BlankOrange.png')

###########################################################
# LOAD WINDOW CONTENT #-----------------------------------#

def LoadWindow() :

    # LEFT FRAME

    leftFrame = Frame(rootFrame, bg = color_main)
    leftFrame.grid(column = 0, row = 0, sticky = 'NEWS')
    
    leftFrame.grid_rowconfigure(0, weight = 1)
    leftFrame.grid_rowconfigure(1, weight = 3)
    leftFrame.grid_columnconfigure(0, weight = 1)

    # headerImage = Label(headerFrame, bg = color_main, image=headerImageRef, bd=0)
    # headerImage.grid(column=0, row=0, sticky='nw')

    headerImage = HoverButton(leftFrame, images = images_Header, text = None)
    headerImage.grid(column = 0, row = 0, sticky = 'NEWS')
    headerImage.selectable = False

    # MENU FRAME

    global menuFrame
    menuFrame = Frame(leftFrame, relief = 'flat', bg = color_main)
    menuFrame.grid(column = 0, row = 1, sticky = 'NEWS')

    buttonSelectFolder = HoverButton(menuFrame, images = images_SelectFolder, command = BrowseForFolder, menuButton = True, colors = ['#E6E7E8', '#F1F2F2', '#BCBEC0'])
    buttonSelectFolder.pack(fill = 'both', expand = 'yes')
    buttonSelectFolder.selectable = False

    buttonSmartName = HoverButton(menuFrame, images = images_SmartName, command = SelectSmartName, menuButton = True)
    buttonSmartName.pack(fill = 'both', expand = 'yes')
    buttonSmartName.selectable = True

    buttonStickers = HoverButton(menuFrame, images = images_Stickers, command = SelectStickerTool, menuButton = True)
    buttonStickers.pack(fill = 'both', expand = 'yes')
    buttonStickers.selectable = True

    buttonTiles = HoverButton(menuFrame, images = images_CeramicTiles, command = SelectCeramicTileTool, menuButton = True)
    buttonTiles.pack(fill = 'both', expand = 'yes')
    buttonTiles.selectable = True

    buttonMetal = HoverButton(menuFrame, images = images_MetalSigns, command = SelectMetalRoundTool, menuButton = True)
    buttonMetal.pack(fill = 'both', expand = 'yes')
    buttonMetal.selectable = True

    buttonCaps = HoverButton(menuFrame, images = images_Bottlecaps, command = SelectBottlecapTool, menuButton = True)
    buttonCaps.pack(fill = 'both', expand = 'yes')
    buttonCaps.selectable = True

    buttonSplitFiles = HoverButton(menuFrame, images = images_SplitFiles, command = SelectRollCalculator, menuButton = True)
    buttonSplitFiles.pack(fill = 'both', expand = 'yes')
    buttonSplitFiles.selectable = True

    # buttonConvertCutFiles = HoverButton(menuFrame, images = images_convertCutFiles, relief = 'flat', command = SelectGraphtecConversion)
    # buttonConvertCutFiles.pack()

    buttonDownloader = HoverButton(menuFrame, images = images_Downloader, command = SelectDownloader, menuButton = True)
    buttonDownloader.pack(fill = 'both', expand = 'yes')
    buttonDownloader.selectable = True

    buttonOpenPrintOS = HoverButton(menuFrame, images = images_printOS, command = SelectPrintOSAdmin, menuButton = True)
    buttonOpenPrintOS.pack(fill = 'both', expand = 'yes')
    buttonOpenPrintOS.selectable = True
    # buttonOpenPrintOS.selectable = False

    buttonSettings = HoverButton(menuFrame, images = images_Settings, command = OpenSettings, menuButton = True)
    buttonSettings.pack(fill = 'both', expand = 'yes')
    buttonSettings.selectable = True

    # MAIN CONTENT FRAME

    global mainContentFrame
    mainContentFrame = Frame(rootFrame, bg = "#FFFFFF", relief = 'flat', bd = 0)
    mainContentFrame.grid(column = 1, row = 0, sticky = 'NEW', ipady = 32)

    mainContentFrame.grid_columnconfigure(0, weight = 1, minsize = 800)
    mainContentFrame.grid_rowconfigure(0, weight = 1)
    # mainContentFrame.config(width = 500, height = 846)

    # MAIN FRAME CONTENTS (START UP PAGE)
    
    stickerFrame = contentFrameTemplate(
        mainContentFrame, 
        scriptName, 
        scriptVersion, 
        'Choose a Folder', 
        "Begin by clicking 'Select Folder' on the left, then choose the folder containing files you'd like to work on. Next, choose a module from the list on the left.",
        mainFunc = BrowseForFolder, 
        descriptionTextHeight = 1
    )

    # FOOTER

    footerFrame = Frame(rootFrame, bg = color_secondary, relief = 'flat')
    footerFrame.grid(column = 0, row = 1, columnspan = 3, sticky = 'NEWS')
    
    footerFrame.grid_columnconfigure(0, weight = 1)
    footerFrame.grid_rowconfigure(0, weight = 1)

    global footerText
    footerText = Label(footerFrame, bg = color_secondary, fg = color_main, font = fontModuleDescription, justify = 'center')
    global dirSel
    footerText.config(text = "No folder currently selected.")
    footerText.grid(column = 0, row = 0, sticky = 'NEWS')

    # CONSOLE LOG FRAME

    global slog
    slog = initSlog(slogFrame, color_main, color_secondary, fontSlog)
    slog.configure(width = 56)
    slog.grid(column = 0, row = 0, padx = 16, pady = 16, sticky = 'NEWS')

###########################################################
# FUNCTION - CHANGE MAIN CONTENT #------------------------#

def ChangeMainContentFrame(newFrameInfo) :

    global newFrame

    if settingsOpened == True:
        CloseSettings()

    children = mainContentFrame.winfo_children()
    for i in children :
        # i.pack_forget()
        i.grid_forget()

    try:
        name = newFrameInfo['name']
    except: name = ''
    try:
        ver = newFrameInfo['ver']
    except: ver = ''
    try:
        buttonText = newFrameInfo['buttonText']
    except: buttonText = ''
    try:
        description = newFrameInfo['description']
    except: description = ''
    try:
        mainFunc = newFrameInfo['mainFunc']
    except: mainFunc = ''
    try:
        textHeight = newFrameInfo['moduleDescriptionTextHeight']
    except: textHeight = 0 #default height for description text box if none is specified
    try:
        customFrame = newFrameInfo['customFrame']
    except: customFrame = None

    # topSpacer = Frame(mainContentFrame, height = 16, bg = "#FFFFFF").grid(row = 0, column = 0)

    newFrame = contentFrameTemplate(mainContentFrame, name, ver, buttonText, description, mainFunc, textHeight, customFrame)

    return newFrame

###########################################################
# FUNCTION - OPEN SETTINGS #------------------------------#

def OpenSettings() :

    fontParameterHeader = font.Font(family='Avenir Black', size=13)
    fontParameterTitle = font.Font(family='Avenir Medium Oblique', size=11)
    fontParameterBody = font.Font(family='Avenir Medium', size=11)

    children = mainContentFrame.winfo_children()
    for i in children :
        # i.pack_forget()
        i.grid_forget()

    global settingsOpened

    global entry_Parameter_ExtraStickers
    global entry_Parameter_MaxSheetHeight
    global entry_Parameter_MaxSheetWidth
    global entry_Parameter_SpaceBetween
    global entry_Parameter_RollLength

    # global noTicketOnSheets
    # global infotechProcessing
    # global singleTicketOnSheets
    # global checkbox_NoTicketOnSheets
    # global checkbox_DontProcessTickets
    # global checkbox_barcodeConversion

    root_Settings = Frame(mainContentFrame, bg = "#FFFFFF", relief = 'flat', width=400)

    frame_Settings = Frame(root_Settings, relief = 'flat', bg = "#FFFFFF")

    root_Settings.grid(pady = 16)

    settingsOpened = True

    label_ParametersTitle = Label(
        frame_Settings, 
        fg = color_main, 
        bg = "#FFFFFF", 
        font = fontParameterHeader, 
        text = 'SETTINGS')

    label_Parameter_FileRenamer = Label(frame_Settings, fg = color_main, bg = "#FFFFFF", font = fontParameterTitle, text = 'SMART NAME')
    checkbox_CheckForCutLines = Checkbutton(frame_Settings, text = "Check for cut lines", fg = color_main, bg = "#FFFFFF", font = fontParameterBody, selectcolor = "#FFFFFF", onvalue = True, offvalue = False, variable = checkForCutLines)

    ###
    separator_Parameter_1 = Frame(frame_Settings, bg = color_main, height = 2, bd = 0)
    ###

    label_Parameter_StickerDownloader = Label(frame_Settings, fg = color_main, bg = "#FFFFFF", font = fontParameterTitle, text = 'STICKER DOWNLOADER')
    checkbox_DownloadTicket = Checkbutton(frame_Settings, text = "Download Infotech ticket", fg = color_main, bg = "#FFFFFF", font = fontParameterBody, selectcolor = "#FFFFFF", onvalue = True, offvalue = False, variable = downloadTicketBool)

    ###
    separator_Parameter_2 = Frame(frame_Settings, bg = color_main, height = 2, bd = 0)
    ###

    ### STICKER SETTINGS ###

    label_Parameter_StickerSheets = Label(frame_Settings, fg = color_main, bg = "#FFFFFF", font = fontParameterTitle, text = 'STICKER TOOL')
    checkbox_FirstSheetTicketOnly = Checkbutton(frame_Settings, text = "Only include Infotech on first sheet", fg = color_main, bg = "#FFFFFF", font = fontParameterBody, selectcolor = "#FFFFFF", variable = TicketOnlyOnFirstSheet)

    checkbox_NoTicketOnSheets = Checkbutton(frame_Settings, text = "Do not include Infotech on sticker sheets", fg = color_main, bg = "#FFFFFF", font = fontParameterBody, selectcolor = "#FFFFFF", variable = dontIncludeTicketOnSheets)
    checkbox_DontProcessTickets = Checkbutton(frame_Settings, text = "Add cut line to Infotechs", fg = color_main, bg = "#FFFFFF", font = fontParameterBody, selectcolor = "#FFFFFF", onvalue = True, offvalue = False, variable = addCutLineToTicket)
    checkbox_barcodeConversion = Checkbutton(frame_Settings, text = "Convert barcode on Infotechs", fg = color_main, bg = "#FFFFFF", font = fontParameterBody, selectcolor = "#FFFFFF", onvalue = True, offvalue = False, variable = barcodeConversion)

    checkbox_archive1UPs = Checkbutton(frame_Settings, text = "Archive 1UPs after sheet is created", fg = color_main, bg = "#FFFFFF", font = fontParameterBody, selectcolor = "#FFFFFF", variable = archive1UPs)

    ##

    frame_spaceBetween = Frame(frame_Settings, relief = 'flat', bg = "#FFFFFF")
    entry_Parameter_SpaceBetween = Entry(frame_spaceBetween, fg = color_main, bg = "#FFFFFF", font = fontParameterBody, width = 6, relief = 'solid', justify = 'center')
    entry_Parameter_SpaceBetween.insert(0, spaceBetweenStickers.get())
    label_SpaceBetween = Label(frame_spaceBetween, fg = color_main, bg = "#FFFFFF", font = fontParameterBody, text = 'Space Between Stickers')

    entry_Parameter_SpaceBetween.pack(side = 'left')
    label_SpaceBetween.pack(side = 'left', padx = 8)

    ##

    frame_MaxSheetHeight = Frame(frame_Settings, relief = 'flat', bg = "#FFFFFF")
    entry_Parameter_MaxSheetHeight = Entry(frame_MaxSheetHeight, fg = color_main, bg = "#FFFFFF", font = fontParameterBody, width = 6, relief = 'solid', justify = 'center')
    entry_Parameter_MaxSheetHeight.insert(0, maxSheetHeight.get())
    label_MaxSheetHeight = Label(frame_MaxSheetHeight, fg = color_main, bg = "#FFFFFF", font = fontParameterBody, text = 'Max Sheet Height')

    entry_Parameter_MaxSheetHeight.pack(side = 'left')
    label_MaxSheetHeight.pack(side = 'left', padx = 8)

    ##

    frame_MaxSheetWidth = Frame(frame_Settings, relief = 'flat', bg = "#FFFFFF")
    entry_Parameter_MaxSheetWidth = Entry(frame_MaxSheetWidth, fg = color_main, bg = "#FFFFFF", font = fontParameterBody, width = 6, relief = 'solid', justify = 'center')
    entry_Parameter_MaxSheetWidth.insert(0, maxSheetWidth.get())
    label_MaxSheetWidth = Label(frame_MaxSheetWidth, fg = color_main, bg = "#FFFFFF", font = fontParameterBody, text = 'Max Sheet Width')

    entry_Parameter_MaxSheetWidth.pack(side = 'left')
    label_MaxSheetWidth.pack(side = 'left', padx = 8)

    ##

    frame_ExtraStickers = Frame(frame_Settings, relief = 'flat', bg = "#FFFFFF")
    entry_Parameter_ExtraStickers = Entry(frame_ExtraStickers, fg = color_main, bg = "#FFFFFF", font = fontParameterBody, width = 6, relief = 'solid', justify = 'center')
    entry_Parameter_ExtraStickers.insert(0, extraStickers.get())
    label_ExtraStickers = Label(frame_ExtraStickers, fg = color_main, bg = "#FFFFFF", font = fontParameterBody, text = 'Extra Stickers')

    entry_Parameter_ExtraStickers.pack(side = 'left')
    label_ExtraStickers.pack(side = 'left', padx = 8)

    ###
    separator_Parameter_3 = Frame(frame_Settings, bg = color_main, height = 2, bd = 0)
    ###

    ### CERAMIC TILE SETTINGS ###

    label_Parameter_TileSheets = Label(frame_Settings, fg = color_main, bg = "#FFFFFF", font = fontParameterTitle, text = 'CERAMIC TILE TOOL')
    checkbox_CombineTileRemainders = Checkbutton(frame_Settings, text = "Combine remainders (DISABLED)", fg = color_main, bg = "#FFFFFF", font = fontParameterBody, selectcolor = "#FFFFFF", onvalue = True, offvalue = False)
    checkbox_MultiPDFTile = Checkbutton(frame_Settings, text = "Create PDF for each sheet (DISABLED)", fg = color_main, bg = "#FFFFFF", font = fontParameterBody, selectcolor = "#FFFFFF", onvalue = True, offvalue = False)

    ###
    separator_Parameter_4 = Frame(frame_Settings, bg = color_main, height = 2, bd = 0)
    ###

    ### BOTTLECAP SETTINGS ###

    label_Parameter_CapSheets = Label(frame_Settings, fg = color_main, bg = "#FFFFFF", font = fontParameterTitle, text = 'BOTTLECAP TOOL')
    checkbox_CapColorSeparation = Checkbutton(frame_Settings, text = "Don't separate by color (DISABLED)", fg = color_main, bg = "#FFFFFF", font = fontParameterBody, selectcolor = "#FFFFFF", onvalue = True, offvalue = False)

    ###
    separator_Parameter_5 = Frame(frame_Settings, bg = color_main, height = 2, bd = 0)
    ###

    ### ROLL CALCULATOR SETTINGS ###

    label_Parameter_RollCalculator = Label(frame_Settings, fg = color_main, bg = "#FFFFFF", font = fontParameterTitle, text = 'ROLL CALCULATOR')

    frame_RollCalculator = Frame(frame_Settings, relief = 'flat', bg = "#FFFFFF")

    entry_Parameter_RollLength = Entry(frame_RollCalculator, fg = color_main, bg = "#FFFFFF", font = fontParameterBody, width = 6, relief = 'solid', justify = 'center')
    entry_Parameter_RollLength.insert(0, rollLength.get())

    label_RollLength = Label(frame_RollCalculator, fg = color_main, bg = "#FFFFFF", font = fontParameterBody, text = 'Roll Length')

    entry_Parameter_RollLength.pack(side = 'left')
    label_RollLength.pack(side = 'left', padx = 8)

    ###########################################################
    # PACK SETTINGS #-----------------------------------------#

    label_ParametersTitle.pack(anchor = 'w', padx = 24, ipady = 4)

    label_Parameter_FileRenamer.pack(anchor = 'w', padx = 24, pady = 2)
    checkbox_CheckForCutLines.pack(anchor = 'w', padx = 50, pady = 2)

    separator_Parameter_1.pack(padx = 24, fill = 'x', pady = 4)

    label_Parameter_StickerDownloader.pack(anchor = 'w', padx = 24, pady = 2)
    checkbox_DownloadTicket.pack(anchor = 'w', padx = 50, pady = 2)

    separator_Parameter_2.pack(padx = 24, fill = 'x', pady = 4)

    label_Parameter_StickerSheets.pack(anchor = 'w', padx = 24, pady = 2)
    checkbox_FirstSheetTicketOnly.pack(anchor = 'w', padx = 50, pady = 2)
    checkbox_NoTicketOnSheets.pack(anchor = 'w', padx = 50, pady = 2)
    checkbox_DontProcessTickets.pack(anchor = 'w', padx = 50, pady = 2)
    checkbox_barcodeConversion.pack(anchor = 'w', padx = 50, pady = 2)
    checkbox_archive1UPs.pack(anchor = 'w', padx = 50, pady = 2)
    frame_spaceBetween.pack(anchor = 'w', padx = 50, pady = 2)
    frame_MaxSheetHeight.pack(anchor = 'w', padx = 50, pady = 2)
    frame_MaxSheetWidth.pack(anchor = 'w', padx = 50, pady = 2)
    frame_ExtraStickers.pack(anchor = 'w', padx = 50, pady = 2)

    separator_Parameter_3.pack(padx = 24, fill = 'x', pady = 4)

    label_Parameter_TileSheets.pack(anchor = 'w', padx = 24, pady = 2)
    checkbox_CombineTileRemainders.pack(anchor = 'w', padx = 50, pady = 2)
    checkbox_MultiPDFTile.pack(anchor = 'w', padx = 50, pady = 2)

    separator_Parameter_4.pack(padx = 24, fill = 'x', pady = 4)

    label_Parameter_CapSheets.pack(anchor = 'w', padx = 24, pady = 2)
    checkbox_CapColorSeparation.pack(anchor = 'w', padx = 50, pady = 2)

    separator_Parameter_5.pack(padx = 24, fill = 'x', pady = 4)

    label_Parameter_RollCalculator.pack(anchor = 'w', padx = 24, pady = 2)
    frame_RollCalculator.pack(anchor = 'w', padx = 50, pady = 2)
    # entry_Parameter_RollLength.pack(anchor = 'w', padx = 50, pady = 2)

    frame_Settings.pack(fill = 'y')
    root_Settings_Instance = root_Settings
    frame_Settings_Instance = frame_Settings

###########################################################
# FUNCTION - CLOSE SETTINGS #-----------------------------#

def CloseSettings() :

    spaceBetweenStickers.set(entry_Parameter_SpaceBetween.get())
    maxSheetWidth.set(entry_Parameter_MaxSheetWidth.get())
    maxSheetHeight.set(entry_Parameter_MaxSheetHeight.get())
    extraStickers.set(entry_Parameter_ExtraStickers.get())

    rollLength.set(entry_Parameter_RollLength.get())

    settingsOpened = False

###########################################################

# DOWNLOAD STICKER FRAME
# if __name__ == '__main__' :

#     downloadOrder = ''
#     downloadSku = ''

#     fileDownloaderFrame = Frame(rootFrame, relief = 'flat', bd = 1, bg = "#FFFFFF")

#     downloadOrderText = Entry(fileDownloaderFrame, width = 9, font=fontSmallBold, textvariable=downloadOrder, justify='center')
#     downloadSkuText = Entry(fileDownloaderFrame, width = 9, font=fontSmallBold, textvariable=downloadSku, justify='center')

#     downloadStickerButton = Button(
#         fileDownloaderFrame,
#         image = button_Yellow_Small,
#         text = 'Download Sticker',
#         compound = 'center',
#         fg = GizmoStyle.bg_blue,
#         bg = "#FFFFFF",
#         font = fontSmall,
#         borderwidth = 0,
#         highlightthickness = 0,
#         command = lambda:executeDownloadSticker(),
#         relief = 'flat')

#     root.bind('<Return>',lambda event:executeDownloadSticker())
#     downloadTicketCheckbox = Checkbutton(fileDownloaderFrame, text="Download Ticket", fg='white', bg=GizmoStyle.bg_blue, selectcolor='#1A283A', onvalue=True, offvalue=False, variable=downloadTicketBool)

#     downloadOrderText.focus_set()

#     downloadOrderText.pack(pady=8, padx=8, side=LEFT, ipady=4, ipadx=8)
#     downloadSkuText.pack(pady=8, padx=8, side=LEFT, ipady=4, ipadx=8)
#     downloadStickerButton.pack(pady=8, padx=8, side=LEFT)
#     downloadTicketCheckbox.pack(pady=8, padx=2, side=LEFT)

#     fileDownloaderFrame.grid(column=1, columnspan=4, row=downloaderRow, padx=8, pady=8)

###########################################################

# MAIN EXECUTION
if __name__ == '__main__' :
    LoadWindow()
    root.mainloop()

###########################################################