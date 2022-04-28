#---------------------------------------------------#
#
# HP PrintOS SiteFlow API Module for DPG Toolbox v3
#
#---------------------------------------------------#

import hmac, hashlib, datetime, requests
from toolbox import keyringDPG

#---------------------------------------------------#

# API ACCESS CREDENTIALS
baseUrl = "https://pro-api.oneflowcloud.com"
key = keyringDPG.HPSiteFlow.key
secret = keyringDPG.HPSiteFlow.secret

#---------------------------------------------------#

params = ''

def create_headers(method, path, timestamp):
    string_to_sign = method + " " + path + " " + timestamp
    local_secret = secret.encode('utf-8')
    string_to_sign = string_to_sign.encode('utf-8')
    signature = hmac.new(local_secret, string_to_sign, hashlib.sha1).hexdigest()
    auth = key + ':' + signature
    return {
		'x-oneflow-authorization': auth,
		'x-oneflow-date': timestamp,
        'content-type':'application/json',
	}

##### GET REQUESTS #####

def get_all_orders():
	return request_get('/api/order/')

def get_all_orders_TechStyles(page, resultsPerPage):
    return request_get('/api/order/', params={'page' : page, 'pagesize' : resultsPerPage, 'sort' : 'source'})

def get_barcode_details(barcodeID):
    return request_get('/api/barcode/details' + barcodeID)

def get_batch(batchID):
    return request_get('/api/batch/' + batchID)

def get_subbatch_by_barcode(barcode):
    return request_get('/api/subbatch/status/live/barcode/' + barcode)

def get_extra_subbatch_info():
    return request_get('/api/subbatch/extra/')

def get_subbatch_by_barcodeALT(barcode):
    return request_get('/api/subbatch/barcode/' + barcode)

def get_subbatch_by_id(subbatchID):
    return request_get('/api/subbatch/' + subbatchID)

def get_order(order_id):
	return request_get('/api/order/' + order_id)

def get_order_by_sourceID(order_id):
    order_id = str(order_id)
    return request_get('/api/order/bysourceid/' + order_id)

def get_file_by_id(file_id):
    file_id = str(file_id)
    return request_get('/api/file/' + file_id)

def get_item_by_id(item_id):
    item_id = str(item_id)
    return request_get('/api/item/' + item_id)
            
def download_file(fileId) :
    return request_get('/api/file/download/' + fileId)

def get_greensheet_by_batchID(batchID) :
    return request_get('/api/subbatch/greensheet/' + batchID)

def get_imposition_by_ID(impositionID) :
    return request_get('/api/imposition/' + impositionID)

def get_imposition_jobs(page, resultsPerPage) :
    return request_get('/api/impositionJob', params={'page' : page, 'pagesize' : resultsPerPage, 'sort' : '_id', 'direction' : -1})

def get_jobs_by_order(orderID) :
    return request_get('/api/job/byorder/' + orderID)

def get_subbatch_by_order(orderID) :
    return request_get('/api/order/' + orderID + '/productionstatus')

def get_extra_order_details(orderID) :
    return request_get('/api/order/details/' + orderID)

def get_live_subbatches():
    return request_get('/api/subbatch/status/live')

def get_files_for_order(orderID):
    return request_get('/api/file/order/' + orderID)

def get_product_list():
    return request_get('/api/product/unallocated')

def get_product(productId):
    return request_get('/api/product/' + productId)

def get_sku_list(page, resultsPerPage):
    return request_get('/api/sku/', params={'page' : page, 'pagesize' : resultsPerPage})

def get_sku(skuId):
    return request_get('/api/sku/' + skuId)

##### POST REQUESTS #####

def push_batch_forward(barcode) :
    return request_post('/api/batch/scan/barcode/' + barcode)    

##### PUT REQUESTS #####

def edit_product(productId, data) :
    return request_put('/api/product/' + productId, json = data)

def edit_sku(skuId, data) :
    return request_put('/api/sku/' + skuId, json = data)

#---------------------------------------------------#

def request_get(path, params=''):
    timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    url = baseUrl + path
    headers = create_headers("GET", path, timestamp)
    if params != '':
        result = requests.get(url, params=params, headers=headers)
    else :
        result = requests.get(url, headers=headers)

    params = ''

    return result

#---------------------------------------------------#

def request_post(path, params='') :
    timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    url = baseUrl + path
    headers = create_headers("POST", path, timestamp)
    if params != '':
        result = requests.post(url, params=params, headers=headers)
    else :
        result = requests.post(url, headers=headers)
    params = ''

    return result

#---------------------------------------------------#

def request_put(path, params='', json='') :
    timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    url = baseUrl + path
    headers = create_headers("PUT", path, timestamp)
    if params != '':
        result = requests.put(url, json = json, params = params, headers = headers)
    else :
        result = requests.put(url, data = json, headers = headers)
    params = ''

    return result

#---------------------------------------------------#
