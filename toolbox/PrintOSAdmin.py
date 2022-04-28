# PRINT OS ADMIN TOOLS
# BUILT FOR CITRABOX
# v1.0 - 02/07/22
# JOHN SAMUEL FUCHS
# www.SAMOE.ME

from toolbox import SiteFlow
from toolbox.sLog import slogPrint
import json

def pushOrderForward (orderNum) :

    if len(orderNum) < 5 :
        slogPrint(' (!) Order number must be 5 digits long.')
        return

    order = SiteFlow.get_order_by_sourceID(orderNum)
    order = json.loads(order.text)

    extraOrderDeets = SiteFlow.get_extra_order_details(order['data'][0]['_id'])
    extraOrderDeets = json.loads(extraOrderDeets.text)

    slogPrint(' - Pushing order ' + str(orderNum) + ' to the next queue.')

    for i in extraOrderDeets['batches'] :
        SiteFlow.push_batch_forward(i['barcode'])
        sendStep = i['currentEvent']['step']
        try:
            slogPrint(' ---- Moved batch ' + str(i['mainBatchNumber']) + ' to ' + i['route'][sendStep]['name'])
        except IndexError:
            slogPrint(' ---- Moved batch ' + str(i['mainBatchNumber']) + ' to SHIPPING.')

    slogPrint(' - Finished pushing order ' + str(orderNum) + ' to the next queue.')