#DPG Toolbox Controller

import main
import sys
import os

if sys.argv[2] == 'smartname' :
    main.RemoteControlRenamer(os.path.dirname(sys.argv[1]))

if sys.argv[2] == 'stickers' :
    params = {
            'Directory' : os.path.dirname(sys.argv[1]),
            'ExtraStickers' : 4,
            'SpaceBetweenStickers' : 0.125,
            'MaxSheetHeight' : 32,
            'MaxSheetWidth' : 50,
            'DontIncludeTicket' : False,
            'TicketOnlyOnFirstSheet' : False,
            'Archive1UPs' : True,
            'addCutLineToTicket' : True
        }
    main.RemoteExecuteStickerTool(params)

if sys.argv[2] == 'tiles' :
    main.RemoteExecuteCeramicTile(os.path.dirname(sys.argv[1]))

if sys.argv[2] == 'metal' :
    main.RemoteExecuteMetalRoundTool(os.path.dirname(sys.argv[1]))

if sys.argv[2] == 'caps' :
    main.RemoteExecute3UPBottlecap(os.path.dirname(sys.argv[1]))