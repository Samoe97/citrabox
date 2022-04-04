import os, shutil

archive = 'L:/Archive/TechStyles Archive/'
alreadyCreatedFolders = []

def ProcessFolder(directory):
    
    fileList = os.listdir(directory)

    for file in fileList :

        if not file.startswith('TILE') and not file.startswith('ROUND') and not file.startswith('CAPS') and file.__contains__('PRINT') or file.__contains__('TICKET') :

            order = file.split('_')[0]
        
            orderGroup = str(order[0:2]) + '000 - ' + str(order[0:2]) + '999'

            archiveGeneric(file, orderGroup, order, directory)

        elif file.__contains__('TILE') :

            orderGroup = 'TILE'

            order = file.split('_')[1]

            archiveGeneric(file, orderGroup, order, directory)

        elif file.__contains__('ROUND') :

            orderGroup = 'ROUND'

            order = file.split('_')[1]

            archiveGeneric(file, orderGroup, order, directory)

        elif file.__contains__('CAPS 50up') :

            orderGroup = 'CAPS'

            order = file.split('_')[1]

            archiveGeneric(file, orderGroup, order, directory)

        else : continue

def archiveGeneric(file, orderGroup, order, directory):

    if orderGroup == 'CAPS' :
        archive = 'L:/Archive/Caps Archive/'
        if os.path.exists(archive + '/' + order) == False :
            os.mkdir(archive + '/' + order)
        if os.path.isdir(archive + '/' + order) :
            try:
                shutil.move(directory+'/'+file, archive+'/'+order)
            except:
                print('File already archived. Deleting ' + file)
                os.remove(archive+file)

    else : 
        archive = 'L:/Archive/TechStyles Archive/'
        if os.path.exists(archive+orderGroup+'/'+order) == False:
            os.mkdir(archive+orderGroup+'/'+order)
                
        if os.path.isdir(archive+orderGroup+'/'+order) :
            try:
                shutil.move(directory+'/'+file, archive+orderGroup+'/'+order)
            except:
                print('File already archived. Deleting ' + file)
                os.remove(archive+file)

def archiveFile(filepath):
    file = filepath.split('/')
    file = file[len(file)-1]
    order = file.split('_')[0]

    orderGroup = str(order[0:2]) + '000 - ' + str(order[0:2]) + '999/'

    if os.path.exists(archive+orderGroup) == False:
        os.mkdir(archive+orderGroup)

    if os.path.exists(archive+orderGroup+order) == False:
        os.mkdir(archive+orderGroup+order)
        
    if os.path.isdir(archive+orderGroup+order) :
        try:
            shutil.move(filepath, archive+orderGroup+order)
        except:
            print('File already archived. Deleting ' + file)
            os.remove(filepath)