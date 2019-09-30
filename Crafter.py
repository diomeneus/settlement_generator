from tkinter import *
from tkinter.filedialog import askopenfilename
from tkinter import filedialog

from math import cos, sin, sqrt, radians, floor
import math

import random
import os
import ast
import sqlite3
from sqlite3 import Error
from PIL import Image, ImageDraw, ImageTk, ImageFont,ImageChops
from fpdf import FPDF

class GearGen(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        
        self.title("Abandoned Gear Generator")
        """OK, here is the plan... I'm going to injest
        This quality gear generator with...
        Magic Item Generator...
        Crafting tracker...

        Player version that tracks crafting progress?
        DM version for generating gear

        you need a system for how the 'minor quirks' are adjusted based on YOU making the item.
        """
        TYPE = ["Armor", "Light Armor", "Medium Armor", "Heavy Armor", "Weapons", "Simple Weapons", "Martial Weapons",
                "Melee Weapons", "Ranged Weapons"]
        MATERIAL = ["Random", "Common", "Uncommon", "Rare", "Very Rare", "Legendary"]

        lightArmors = [["Padded", 5], ["Leather", 10], ["Studded Leather", 45]]
        mediumArmors = [["Hide", 10], ["Chain Shirt", 50], ["Scale Mail", 50], ["Breastplate", 400],
                        ["Half Plate", 750]]
        heavyArmors = [["Ring Mail", 30], ["Chain Mail", 75], ["Splint", 200], ["Plate", 1500]]
        simpleMeleeWeapons = [["Club", 1], ["Dagger", 2], ["Greatclub", 1], ["Handaxe", 5], ["Javelin", 1],
                              ["Light Hammer", 2], ["Mace", 5], ["Quarterstaff", 2], ["Sickle", 1], ["Spear", 1],
                              ["Saber", 15], ["Smithing Hammer", 3]]
        simpleRangedWeapons = [["Light Crossbow", 25], ["Dart", 1], ["Shortbow", 25], ["Sling", 1]]
        martialMeleeWeapons = [["Battleaxe", 10], ["Flail", 10], ["Glaive", 20], ["Greataxe", 30], ["Greatsword", 50],
                               ["Halberd", 20], ["Lance", 10], ["Longsword", 15], ["Maul", 10], ["Morningstar", 15],
                               ["Pike", 5], ["Rapier", 25], ["Scimitar", 25], ["Shortsword", 10], ["Trident", 5],
                               ["War Pick", 5], ["Warhammer", 15], ["Whip", 2], ["Harpoon", 5], ["Boar Spear", 5],
                               ["Heavy Flail", 10], ["Falchion", 25], ["Tonfa", 2], ["Bludgeoning Star", 15],
                               ["Lantern Shield", 50]]
        martialRangedWeapons = [["Blowgun", 10], ["Hand Crossbow", 75], ["Heavy Crossbow", 50], ["Longbow", 50],
                                ["Net", 1], ["Boomerang", 2]]

        typeString = StringVar(self)
        typeString.set(TYPE[0])  # default value
        var2materialString = StringVar(self)
        var2materialString.set(MATERIAL[0])  # default value

        controlFrame = Frame(self)
        controlFrame.grid(column=0, row=0)
        displayFrame = Frame(self)
        displayFrame.grid(column=1, row=0)
        geometry = [350, 350, 120]
        # width, height, controls width

        OptionMenu(controlFrame, typeString, *TYPE).grid(column=0, row=0)
        OptionMenu(controlFrame, var2materialString, *MATERIAL).grid(column=0, row=1)
        qty = Entry(controlFrame)
        qty.grid(column=0, row=2)
        qty.insert(END, '10')
        go = Button(controlFrame, text="Go", command=lambda: generate())
        go.grid(column=0, row=3)

        
        self.can = Canvas(displayFrame, width=geometry[0], height=geometry[1], bg="#fffafa")
        self.can.grid(row=0, column=0)  # .pack()
        qty.focus_set()

        vbar = Scrollbar(mainFrame, orient=VERTICAL)
        vbar.grid()
        vbar.config(command=self.can.yview)
        self.can.config(yscrollcommand=vbar.set)

        def generate():
            self.can.delete("all")
            print("\n")
            quantity = int(qty.get())
            items = []
            type_gallery = []
            if typeString.get() == "Armor": type_gallery += lightArmors + mediumArmors + heavyArmors
            if typeString.get() == "Light Armor": type_gallery += lightArmors
            if typeString.get() == "Medium Armor": type_gallery += mediumArmors
            if typeString.get() == "Heavy Armor": type_gallery += heavyArmors
            if typeString.get() == "Weapons": type_gallery += simpleMeleeWeapons + simpleRangedWeapons + martialMeleeWeapons + martialRangedWeapons
            if typeString.get() == "Simple Weapons": type_gallery += simpleMeleeWeapons + simpleRangedWeapons
            if typeString.get() == "Martial Weapons": type_gallery += martialMeleeWeapons + martialRangedWeapons
            if typeString.get() == "Melee Weapons": type_gallery += simpleMeleeWeapons + martialMeleeWeapons
            if typeString.get() == "Ranged Weapons": type_gallery += simpleRangedWeapons + martialRangedWeapons
            material = var2materialString.get()
            for x in range(quantity):
                if var2materialString.get() == "Random":
                    roll = random.randint(1, 20)
                    if roll < 10:
                        material = "Common"
                    elif roll < 17:
                        material = "Uncommon"
                    elif roll < 20:
                        material = "Rare"
                    else:
                        roll = random.randint(1, 8)
                        if roll == 8:
                            material = "Legendary"
                        else:
                            material = "Very Rare"

                # this is stupid. 1-6 ruined, 7-11 shoddy, 12-15 poor, 16-18 standard, 19 superior, 20 reroll for Expectional or Masterwork
                # if var3.get() == True:
                roll = random.randint(1, 20)
                if roll < 7:
                    quality = "Ruined"
                elif roll < 12:
                    quality = "Shoddy"
                elif roll < 16:
                    quality = "Poor"
                elif roll < 19:
                    quality = "Standard"
                elif roll == 19:
                    quality = "Superior"
                else:
                    roll = random.randint(1, 8)
                    if roll == 8:
                        quality = "Masterwork"
                    else:
                        quality = "Exceptional"

                items.append([quality, material, random.randint(1, 100)])
            print(type_gallery)

            for n, x in enumerate(items):
                type_selection = random.choice(type_gallery)
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

                temptext = str(x[0]) + ' ' + str(type_selection[0]) + ' ' + str(x[2]) + "% of " + str(
                    x[1]) + " material: " + str(math.ceil(type_selection[1] * 0.5 * qlty_mod * mat_mod)) + "gp CM"
                print(temptext)
                self.can.create_text(5, 10 + n * 15, fill="darkblue", font="Arial 9", text=temptext, anchor=W)
       
        


class Enchanter(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller

        controlFrame = Frame(self)
        controlFrame.grid(column=0, row=0)
        displayFrame = Frame(self)
        displayFrame.grid(column=1, row=0)
        geometry = [350, 350, 120]
        # width, height, controls width

        btn_editor = Button(controlFrame, text="Generator")#, command=lambda: [self.ditor(),controller.show_frame("Controls_Generator")])
        btn_editor.pack()
        Label(controlFrame,text = "").pack()
        btn_commit = Button(controlFrame, text="Print Layout")#, command=lambda: self.controller.printlayout())
        btn_clear = Button(controlFrame, text="Clear Layout")#, command=lambda: self.controller.key_empty())
        btn_commit.pack()
        btn_clear.pack()

        labelframe = LabelFrame(controlFrame, text="Brush")
        labelframe.pack(fill="both", expand="yes")
        brush_district = Button(labelframe, text="District")#,command=lambda: [self.controller.brushswap("District"),self.controller.rivereditor(False)])
        brush_coastal = Button(labelframe, text="Coastal")#, command=lambda: [self.controller.brushswap("Coastal"),self.controller.rivereditor(False)])
        brush_river = Button(labelframe, text="River")#, command=lambda: [self.controller.brushswap("River"),self.controller.rivereditor(True)])

class Crafter(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller

        controlFrame = Frame(self)
        controlFrame.grid(column=0, row=0)
        displayFrame = Frame(self)
        displayFrame.grid(column=1, row=0)
        geometry = [350, 350, 120]
        # width, height, controls width

        
class Main(Tk):
    def __init__(self):
        Tk.__init__(self)

        #the FIRST thing we will do is setup a launcher
        self.title("Crafter - Gear Generator")
        menubar = Menu(self)

        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=lambda: self.open())
        filemenu.add_command(label="Save", command=lambda: self.save(True,False))
        filemenu.add_command(label="Save As", command=lambda: self.save(True,True))
        filemenu.add_command(label="Print", command=lambda: [self.save(False),self.make_print()])
        menubar.add_cascade(label="File", menu=filemenu)

        optionsmenu = Menu(menubar, tearoff=0)
        optionsmenu.add_checkbutton(label="one", onvalue=True, offvalue=False)
        optionsmenu.add_checkbutton(label="two", onvalue=True, offvalue=False)
        optionsmenu.add_checkbutton(label="three", onvalue=True, offvalue=False)
        menubar.add_cascade(label="Options", menu=optionsmenu)

        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Gear Generator", command=lambda: self.show_frame("GearGen"))
        filemenu.add_command(label="Enchanter", command=lambda: self.show_frame("Enchanter"))
        filemenu.add_command(label="Crafter", command=lambda: self.show_frame("Crafter"))
        menubar.add_cascade(label="Program", menu=filemenu)

        self.config(menu=menubar)
        width = 465
        height = 385

        #setting up our frames
        mainFrame = Frame(self)
        mainFrame.grid(column=0,row=0)

        self.frames = {}
        for F in (GearGen, Enchanter, Crafter):
            page_name = F.__name__
            frame = F(parent=mainFrame, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame("Controls_GearGen")

        displayFrame = Frame(self)
        displayFrame.grid(column=1,row=0)

       
        #Assigning controls
        self.can.bind("<Button-1>", self.click)
        self.bind("<B1-Motion>", self.drag)
        self.bind('<ButtonRelease-1>', self.clickrelease)
        self.can.bind("<Button-2>", self.mclick)
        self.can.bind("<Button-3>", self.rclick)
        self.can.bind("c", self.key_commit)
        self.can.bind("e", self.key_empty)
        self.can.focus_set()  #focus the window for keyboard controls
  
    def show_frame(self, page_name): #swaps the left frame from editor to generator controls
        frame = self.frames[page_name]
        frame.tkraise()

    def test(self,arg):
        print("successful test of the",arg,"command")

    def save(self,dialog,saveas): #only works properly when invoked from a popup window currently. makes a pdf.
        print("save a thing, 1st value i think was to track if you working off a current one or a new one that needs a filename-path. Basically first hit of hte save should invoke save as")
        if dialog:
            self.filename = filedialog.asksaveasfilename(initialfile= self.settlementname.get()+".pdf",initialdir = "/",title = "Select file",filetypes = (("pdf files","*.pdf"),("all files","*.*")))
            if self.filename is None:  # asksaveasfile return `None` if dialog closed with "cancel".
                return
            self.image.save(str(self.settlementname)+".png")

        else: self.filename = "Settlements/" + self.settlementname.get() + ".pdf"
        print (self.filename)
        
        
    def make_print(self):
        print (self.filename)
        #os.startfile(self.filename, "print")

    def open(self):
        filename = askopenfilename()  # show an "Open" dialog box and return the path to the selected file
        print(filename)

    def popout(self): #makes a popup window with the current settlement and the full description.
        width = 800
        height = 600
        popup = Toplevel()
        popup.title("popup")
        popup.geometry("300x200")

        popupbar = Menu(popup)
        popupbar.add_cascade(label="Save", command=lambda: self.save(True))
        popupbar.add_cascade(label="Print", command=lambda: [self.save(False),self.make_print()])
        popupbar.add_cascade(label="Close", command=popup.destroy)
        popup.config(menu=popupbar)
        
        popup.mainloop()

    def click(self, evt): #I no longer know where click starts and clickrelease ends....
        print (evt)
        #x, y = evt.x, evt.y
   
    def mclick(self, evt):
        print(evt)

    def clickrelease(self,evt):
        print(evt)

    def rclick(self, evt): #right clicking is currently the "erase" function of the editor
        print(evt)

    def create_connection(self, db_file):
        try:
            conn = sqlite3.connect(db_file)
            return conn
        except Error as e:
            print(e)
        return None

if __name__ == "__main__":
    app = Main()
    mainloop()
