# Custom Console Log
# Written by Samoe (John S Fuchs)
# 11/1/21

import tkinter.font as Font
from tkinter import *

def initSlog (frame, bg, fg, font) :

    global rootFrame   
    global slog

    slog = Text(frame, bg=bg, fg=fg, font=font, state='disabled', relief='flat', wrap='word')

    rootFrame = frame

    return slog

def slogPrint(message):
    try:
        slog.config(state='normal')

        print(message)
        slog.insert('end', message + '\n')

        slog.see('end')

        slog.configure(state='disabled')

        rootFrame.update()
    except:
        print(message)

# root.mainloop()