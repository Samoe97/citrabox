import time
from tkinter import Button

class HoverButton(Button) :

    def __init__(self, master, imageIdle, imageHovered, imageClicked, imageSelected, **kw):
        Button.__init__(self, master = master, highlightthickness = 0, bd = 0, **kw)
        Button.config(self, relief = 'flat')

        self.selectable = True
        self.selected = False

        self.image_idle = imageIdle
        self.image_hovered = imageHovered
        self.image_clicked = imageClicked
        self.image_selected = imageSelected

        self['image'] = self.defaultImage

        self.bind("<Enter>", self.on_hover)
        self.bind("<Leave>", self.on_unhover)
        self.bind("<Button-1>", self.on_clicked)

        def on_hover(self):
            if self.selected == False :
                self.config(image = self.image_hovered)

        def on_unhover(self):
            if self.selected == False :
                self.config(image = self.image_idle)

        def on_clicked(event):
            event.widget['image'] = event.widget.clickedImage
            # root.update()

            # menuButtons = menuFrame.winfo_children()

            # for i in menuButtons :
            #     if i != event.widget :
            #         i['image'] = i.defaultImage
            #         i.selected = False
                
            # if event.widget.selectable == True:
            #     event.widget.selected = True
            #     event.widget['image'] = event.widget.selectedImage
            #     root.update()
            # else :
            event.widget.selected = False
            time.sleep(0.1)
            self.on_hover()
        
        # def remove(event):
            # event.grid_remove()