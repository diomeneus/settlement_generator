from tkinter import *
from tkinter.filedialog import askopenfilename
from tkinter import filedialog

from math import cos, sin, sqrt, radians, floor
import math

import random
import os
import ast

#class Controls_GearGen(Frame):



class Main(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.title("Abandoned Gear Generator")
        """OK, here is the plan... I'm going to injest
        This quality gear generator with...
        Magic Item Generator...
        Crafting tracker...
        
        Player version that tracks crafting progress?
        DM version for generating gear
        
        you need a system for how the 'minor quirks' are adjusted based on YOU making the item.
        """
        TYPE = ["Armor", "Light Armor", "Medium Armor", "Heavy Armor", "Weapons", "Simple Weapons", "Martial Weapons", "Melee Weapons","Ranged Weapons"]
        MATERIAL = ["Random", "Common", "Uncommon", "Rare", "Very Rare", "Legendary"]

        lightArmors = [["Padded", 5], ["Leather", 10], ["Studded Leather", 45]]
        mediumArmors = [["Hide", 10], ["Chain Shirt", 50], ["Scale Mail", 50], ["Breastplate", 400], ["Half Plate", 750]]
        heavyArmors = [["Ring Mail", 30], ["Chain Mail", 75], ["Splint", 200], ["Plate", 1500]]
        simpleMeleeWeapons = [["Club", 1],["Dagger", 2],["Greatclub", 1],["Handaxe", 5],["Javelin", 1],["Light Hammer", 2],["Mace", 5],["Quarterstaff", 2],["Sickle", 1],["Spear", 1],["Saber",15],["Smithing Hammer",3]]
        simpleRangedWeapons = [["Light Crossbow", 25],["Dart", 1],["Shortbow", 25],["Sling", 1]]
        martialMeleeWeapons = [["Battleaxe", 10],["Flail", 10],["Glaive", 20],["Greataxe", 30],["Greatsword", 50],["Halberd", 20],["Lance", 10],["Longsword", 15],["Maul", 10],["Morningstar", 15],["Pike", 5],["Rapier", 25],["Scimitar", 25],["Shortsword", 10],["Trident", 5],["War Pick", 5],["Warhammer", 15],["Whip", 2],["Harpoon",5],["Boar Spear",5],["Heavy Flail",10],["Falchion",25],["Tonfa",2],["Bludgeoning Star",15],["Lantern Shield",50]]
        martialRangedWeapons = [["Blowgun", 10],["Hand Crossbow", 75],["Heavy Crossbow", 50],["Longbow", 50],["Net",1],["Boomerang",2]]

        var1 = StringVar(self)
        var1.set(TYPE[0])  # default value
        var2 = StringVar(self)
        var2.set(MATERIAL[0])  # default value

        OptionMenu(self, var1, *TYPE).grid(column=0,row=0)
        OptionMenu(self, var2, *MATERIAL).grid(column=0, row=1)
        qty = Entry (self)
        qty.grid(column=0, row=2)
        qty.insert(END, '10')
        go = Button (self, text="Go",command=lambda :generate())
        go.grid(column=0, row=3)

        #setting up our frames
        mainFrame = Frame(self)
        mainFrame.grid(column=1,row=0)

        # self.frames = {}
        # for F in (Controls_Editor, Controls_Generator):
        #     page_name = F.__name__
        #     frame = F(parent=mainFrame, controller=self)
        #     self.frames[page_name] = frame
        #     frame.grid(row=0, column=0, sticky="nsew")
        # self.show_frame("Controls_Generator")
        # controlFrame = Frame(self)
        # controlFrame.grid(column=0,row=0)

        displayFrame = Frame(self)
        displayFrame.grid(column=0,row=0)

        width = 350
        height = 350

        #self.can.config(width=300, height=300)
        #self.can.config(xscrollcommand=hbar.set, yscrollcommand=vbar.set)
        #self.can.pack(side=LEFT, expand=True, fill=BOTH)

        self.can = Canvas(mainFrame, width=width, height=height, bg="#fffafa")
        self.can.grid(row=0, column=0, columnspan=4)  # .pack()
        qty.focus_set()

        vbar = Scrollbar(mainFrame, orient=VERTICAL)
        vbar.grid()
        vbar.config(command=self.can.yview)
        self.can.config(yscrollcommand=vbar.set)
        # displayFrame = Frame(self)
        # displayFrame.grid(column=1,row=0)

    #probably don't need, but made simple
        # def clearcan():
        #     for x in self.can:
        #         print (x)
        def open_player():
            self.file_path = filedialog.askopenfilename()

        def save_player():
            #should only invoke the dialog for path and name 1st time.
            if not self.file_path : self.file_path = filedialog.askopenfilename()


        def generate():
            self.can.delete("all")
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
            material = var2.get()
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

            for n, x in enumerate(items):
                type_selection = random.choice (type_gallery)
                material = type_selection[1]
                if x[0] == "Ruined": qlty_mod = 0.1
                if x[0] == "Shoddy": qlty_mod = 0.3
                if x[0] == "Poor": qlty_mod = 0.6
                if x[0] == "Standard": qlty_mod = 1
                if x[0] == "Superior": qlty_mod = 1.2
                if x[0] == "Exceptional": qlty_mod = 1.5
                if x[0] == "Masterwork": qlty_mod = 2

                if x[1] == "Common": mat_mod = 1
                if x[1] == "Uncommon": mat_mod = 1.2
                if x[1] == "Rare": mat_mod = 1.5
                if x[1] == "Very Rare": mat_mod = 1.8
                if x[1] == "Legendary": mat_mod = 2.2

                temptext = str(x[0])+' '+str(type_selection[0])+' '+str(x[2])+"% of "+str(x[1])+" material: "+str(math.ceil(type_selection[1]*0.5*qlty_mod*mat_mod))+"gp CM"
                print (temptext)
                self.can.create_text(5, 10+n*15, fill="darkblue", font="Arial 9", text=temptext,anchor=W)



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
        TextArea2.config(font="arial",wrap=WORD)

        popup.mainloop()


# As far as I can tell this is a pythony secure way to launch the main loop.
if __name__ == "__main__":
    app = Main()
    mainloop()
