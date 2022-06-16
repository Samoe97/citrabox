# ROLL ORGANIZER
# Calculate length of files in directory
# Split the files into separate folders based on material usage

from toolbox import Renamer2
from toolbox.sLog import slogPrint
import os, shutil
from PyPDF2 import PdfFileReader
from decimal import Decimal # CALCULATES ROLL LENGTH

global rollIndex
rollIndex = 1

global totalLength
totalLength = 0

# FUNCTIONS - UNIT CONVERSIONS

def points(inches):
    points = float(inches) * 72
    return float(points)

def inches(points):
    inches = float(points) / 72
    return float(inches)

# FUNCTIONS - ORGANIZE FILES BY ROLL

def processLength(params):
    global rollIndex
    global totalLength

    if params['Directory'] == '' :
        slogPrint(' - No directory selected.')
        return
        
    dirCheck = params['Directory']
    slogPrint(' ---- Separating print files into rolls ---- ')
    for file in os.listdir(dirCheck):
        if file.endswith('.pdf'):
            f = open(dirCheck + '/' + file, 'rb')
            pdf = PdfFileReader(f)
            mediaBox = pdf.getPage(0).mediaBox
            length = inches(mediaBox.getHeight())
            f.close()
            splitRolls(dirCheck, length, file, params['maxRollLength'])
            
    slogPrint(' ---- Success! ' + str(rollIndex) + ' rolls are ready to print. ----')
    rollIndex = 1
    totalLength = 0

def splitRolls(dirSel, length, file, maxRollLength):
    global totalLength
    global rollIndex
    spaceBetweenSheets = 3
    
    if not os.path.isdir(dirSel + '/' + 'ROLL ' + str(rollIndex)):
        os.mkdir(dirSel + '/' + 'ROLL ' + str(rollIndex))

    oldPath = dirSel + '/' + file
    newPath = dirSel + '/ROLL ' + str(rollIndex) + '/' + file
    oldPath = str(oldPath)
    newPath = str(newPath)
    shutil.move(oldPath, newPath)
    
    length = Decimal(length)
    totalLength = totalLength + length + spaceBetweenSheets
    if totalLength > maxRollLength:
        rollIndex = rollIndex + 1
        totalLength = 0