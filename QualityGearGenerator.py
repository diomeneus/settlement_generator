from tkinter import *
from tkinter.filedialog import askopenfilename
from tkinter import filedialog

from math import cos, sin, sqrt, radians, floor
import math

import random
import os
import ast

class Main(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.title("Abandoned Gear Generator")

        TYPE = ["Armor", "Light Armor", "Medium Armor", "Heavy Armor", "Weapons", "Simple Weapons", "Martial Weapons", "Melee Weapons","Ranged Weapons"]
        MATERIAL = ["Random", "Common", "Uncommon", "Rare", "Very Rare", "Legendary"]

        lightArmors = [["Padded", 5], ["Leather", 10], ["Studded Leather", 45]]
        mediumArmors = [["Hide", 10], ["Chain Shirt", 50], ["Scale Mail", 50], ["Breastplate", 400], ["Half Plate", 750]]
        heavyArmors = [["Ring Mail", 30], ["Chain Mail", 75], ["Splint", 200], ["Plate", 1500]]
        simpleMeleeWeapons = [["stick", 5]]
        simpleRangedWeapons = [["stick", 5]]
        martialMeleeWeapons = [["stick", 5]]
        martialRangedWeapons = [["stick", 5]]

        var1 = StringVar(self)
        var1.set(TYPE[0])  # default value
        var2 = StringVar(self)
        var2.set(MATERIAL[0])  # default value

        OptionMenu(self, var1, *TYPE).grid(column=0,row=0)
        OptionMenu(self, var2, *MATERIAL).grid(column=1, row=0)
        qty = Entry (self)
        qty.grid(column=2, row=0)
        go = Button (self, text="Generate",command=lambda :generate())
        go.grid(column=3, row=0)

        #setting up our frames
        mainFrame = Frame(self)
        mainFrame.grid(column=0,row=1,columnspan=3)

        # displayFrame = Frame(self)
        # displayFrame.grid(column=1,row=0)

    #probably don't need, but made simple
        def generate():
            print ("\n")
            quantity = int(qty.get())
            items = []
            type_gallery = []
            if var1.get() == "Armor": type_gallery += lightArmors+mediumArmors+heavyArmors
            if var1.get() == "Light Armor": type_gallery += lightArmors
            if var1.get() == "Medium Armor": type_gallery += mediumArmors
            if var1.get() == "Heavy Armor": type_gallery += heavyArmors
            if var1.get() == "Weapons": type_gallery += simpleMeleeWeapons+simpleRangedWeapons+martialMeleeWeapons+martialRangedWeapons
            if var1.get() == "Simple Weapons": type_gallery += simpleMeleeWeapons+simpleRangedWeapons
            if var1.get() == "Martial Weapons": type_gallery += martialMeleeWeapons+martialRangedWeapons
            if var1.get() == "Melee Weapons": type_gallery += simpleMeleeWeapons+martialMeleeWeapons
            if var1.get() == "Ranged Weapons": type_gallery += simpleRangedWeapons+martialRangedWeapons

            for x in range (quantity):
                if var2.get() == "Random":
                    roll = random.randint (1,20)
                    if roll <10: material="Common"
                    elif roll <17: material="Uncommon"
                    elif roll < 20: material = "Rare"
                    else:
                        roll=random.randint (1,8)
                        if roll == 8: material = "Legendary"
                        else: material = "Very Rare"

                # this is stupid. 1-6 ruined, 7-11 shoddy, 12-15 poor, 16-18 standard, 19 superior, 20 reroll for Expectional or Masterwork
                #if var3.get() == True:
                roll = random.randint(1, 20)
                if roll < 7: quality = "Ruined"
                elif roll < 12: quality = "Shoddy"
                elif roll < 16: quality = "Poor"
                elif roll < 19: quality = "Standard"
                elif roll == 19: quality = "Superior"
                else:
                    roll = random.randint(1, 8)
                    if roll == 8: quality = "Masterwork"
                    else: quality = "Exceptional"

                items.append([quality,material,random.randint(1,100)])
            print (type_gallery)

            for x in items:
                type_selection = random.choice (type_gallery)
                material = type_selection[1]
                print (x[0],type_selection[0], str(x[2])+"% of",x[1],"material")




    def popout(self): #makes a popup window with the current settlement and the full description.
        width = 800
        height = 600
        #self.image = self.trim(self.image)
        popup = Toplevel()
        popup.title("Popup")
        popup.geometry("800x600")
        iheight=500
        iwidth=700
        popupbar = Menu(popup)
        popupbar.add_cascade(label="Save", command=lambda: self.save(True))
        popupbar.add_cascade(label="Print", command=lambda: [self.save(False),self.make_print()])
        popupbar.add_cascade(label="Close", command=popup.destroy)
        popup.config(menu=popupbar)
        topframe=Frame(popup,width=width,height=iheight)
        topframe.pack(side=TOP)
        bottomframe=Frame(popup,width=width)
        bottomframe.pack(side=BOTTOM)
        leftframe = Frame(topframe, bd=1, width=iwidth, bg="black")
        leftframe.pack(side=LEFT)
        rightframe = Frame(topframe,width=width-iwidth,height=iheight)#,bg="black",bd=1)
        rightframe.pack(side=RIGHT)

        TextArea = Text(rightframe, height=20, width=60)
        TextArea.insert(END, "Words")
        TextArea.pack(expand=YES, fill=BOTH)
        TextArea.config(font="arial",wrap=WORD)  # ('Arial', 10, 'bold', 'italic'))

        TextArea2 = Text(bottomframe, height=20, width=int(width/9))
        TextArea2.insert(END, "More words")
        TextArea2.pack(expand=YES, fill=BOTH)
        TextArea2.config(font="arial",wrap=WORD,)

        popup.mainloop()


# As far as I can tell this is a pythony secure way to launch the main loop.
if __name__ == "__main__":
    app = Main()
    mainloop()
