# GRAPHTEC CONVERSION
# FC8600 -> FC9000
# PYTHON

from DPGToolbox.sLog import slogPrint
import os

def graphtecConversion8600(params):

    if params['Directory'] == '' :
        slogPrint(' - No directory selected.')
        return

    dirCheck = params['Directory']
    xmlIndex = 0
    for file in os.listdir(dirCheck):
        if file.endswith('.xml'):
            with open(dirCheck + '/' + file, 'r') as XML:
                XMLdata = XML.read()

            XMLdata = XMLdata.replace('<cut-option name="MarkPattern" value="2"/>', '<cut-option name="MarkPattern" value="3"/>')
            XMLdata = XMLdata.replace('device="Graphtec Cutter"', 'device="Graphtec FC9000 Cutter"')
            XMLdata = XMLdata.replace('instance="graphtecmark"', 'instance="graphtecfc9000mark"')
            with open(dirCheck + '/' + file, 'w') as XML:
                XML.write(XMLdata)
            xmlIndex = xmlIndex + 1
        else:
            slogPrint(file + " experienced an error.")
    slogPrint('------------------------------------------------------')
    slogPrint(' - Success! ' + str(xmlIndex) + ' XML files have been converted.')