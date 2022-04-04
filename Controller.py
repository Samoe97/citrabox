#DPG Toolbox Controller

import main

global stickerLocation
stickerLocation = 'C:/Users/jfuchs/Dropbox/z_CITRA LF PRINT JOBS TO METRO/TECHSTYLES_CUSTOM SHAPE LABELS/PRINT FILES'

def renameStickers() :
    main.remoteControlRenamer(stickerLocation)