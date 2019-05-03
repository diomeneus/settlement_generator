from tkinter import *
#import tkinter as tk
from math import cos, sin, sqrt, radians, floor
import math
import random
import os
import sqlite3
import ast
from sqlite3 import Error

class RiverNode:
    def __init__(self, parent, x, y, x2, y2, outline, color,tags):
        self.tags = tags
        parent.create_oval (x,
                              y,
                              x2,
                              y2,
                              outline = outline,
                              fill= color,
                              tags = self.tags,
                              state=HIDDEN)

class DrawRiver:
    def __init__(self, parent, x, y, x2,y2, color, tags):
        self.rtags = tags
        parent.create_line(x,
                           y,
                           x2,
                           y2,
                           fill=color,
                           width = 5,
                           tags=tags)

class FillHexagon:
    def __init__(self, parent, x, y, length, color, border, tags):
        self.parent = parent  # canvas
        self.start_x = x  # top left x
        self.start_y = y  # top left y
        self.length = length  # length of a side
        self.color = color  # fill color

        self.tags = tags
        self.district = False
        self.river = False
        self.coastal = False

        angle = 60
        coordinates = []
        for i in range(6):
            end_x = self.start_x + self.length * cos(radians(angle * i))
            end_y = self.start_y + self.length * sin(radians(angle * i))
            coordinates.append([self.start_x, self.start_y])
            self.start_x = end_x
            self.start_y = end_y
        self.parent.create_polygon(coordinates[0][0],
                                   coordinates[0][1],
                                   coordinates[1][0],
                                   coordinates[1][1],
                                   coordinates[2][0],
                                   coordinates[2][1],
                                   coordinates[3][0],
                                   coordinates[3][1],
                                   coordinates[4][0],
                                   coordinates[4][1],
                                   coordinates[5][0],
                                   coordinates[5][1],
                                   fill=self.color,
                                   outline=border,
                                   tags=self.tags)

class Controls_Editor(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        btn_editor = Button(self, text="Generator", command=lambda: [self.controller.swapeditor(),controller.show_frame("Controls_Generator")])
        btn_editor.pack()
        Label(self,text = "").pack()
        btn_commit = Button(self, text="Print Layout", command=lambda: self.key_commit)
        btn_clear = Button(self, text="Clear Layout", command=lambda: self.key_empty)
        btn_commit.pack()
        btn_clear.pack()

        labelframe = LabelFrame(self, text="Brush")
        labelframe.pack(fill="both", expand="yes")
        brush_district = Button(labelframe, text="District",command=lambda: [self.controller.brushswap("District"),self.controller.rivereditor(False)])
        brush_coastal = Button(labelframe, text="Coastal", command=lambda: [self.controller.brushswap("Coastal"),self.controller.rivereditor(False)])
        brush_river = Button(labelframe, text="River", command=lambda: [self.controller.brushswap("River"),self.controller.rivereditor(True)])
#highlist the selected brush
        brush_district.pack()
        brush_coastal.pack()
        brush_river.pack()

        #btn_river = Button(self, text="River Maker", command=lambda: self.rivereditor())
        #btn_river.pack()

class Controls_Generator(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        btn_editor = Button(self, text="Layout Editor", command=lambda: [self.controller.swapeditor(),controller.show_frame("Controls_Editor")])
        btn_editor.pack()
        Label(self,text = "").pack()
        labelframe = LabelFrame(self, text="Generate")
        labelframe.pack(fill="both", expand="yes")

        btn_genname = Button(labelframe, text="Name", width = 8,command=lambda: self.controller.generate_name(0, "generic", "short"))
        btn_generate = Button(labelframe, text="Everything", width=8, command=lambda: self.controller.generate(True,True))
        btn_genlayout = Button(labelframe, text="Layout", width = 8, command=lambda: self.controller.generate(True,False))
        btn_gendistricts = Button(labelframe, text="Districts", width = 8, command=lambda: self.controller.generate(False,True))
        btn_genname.pack()
        btn_generate.pack()
        btn_genlayout.pack()
        btn_gendistricts.pack()
        Label(self, text="").pack()

        labelframe2 =LabelFrame(self, text="Settlement")
        labelframe2.pack(fill="both", expand="yes")
        Label(labelframe2, textvariable=controller.settlementname).pack()

class Main(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.settlementname = StringVar()
        self.editorbrush = StringVar()
        self.rivselected=0
        self.coords = {"x": 0, "y": 0, "x2": 0, "y2": 0}
        """Setting up our frames, titles and UI"""
        self.title("Settlement Generator")
        menubar = Menu(self)
        show_all = False

        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=lambda: self.brushswap("District"))
        filemenu.add_command(label="Save", command=lambda: self.brushswap("Coastal"))
        filemenu.add_command(label="Print", command=lambda: self.brushswap("Coastal"))
        menubar.add_cascade(label="File", menu=filemenu)

        optionsmenu = Menu(menubar, tearoff=0)
        optionsmenu.add_checkbutton(label="Theme", onvalue=True, offvalue=False, variable=show_all)
        optionsmenu.add_checkbutton(label="Feature", onvalue=True, offvalue=False, variable=show_all)
        optionsmenu.add_checkbutton(label="Layout", onvalue=True, offvalue=False, variable=show_all)
        optionsmenu.add_checkbutton(label="Districts", onvalue=True, offvalue=False, variable=show_all)
        optionsmenu.add_checkbutton(label="District Features", onvalue=True, offvalue=False, variable=show_all)
        optionsmenu.add_checkbutton(label="Check", onvalue=True, offvalue=False, variable=show_all)
        menubar.add_cascade(label="Locks", menu=optionsmenu)
        self.config(menu=menubar)

        #setting up our frames
        mainFrame = Frame(self)
        mainFrame.pack(side="left", fill="both", expand=True)
        mainFrame.grid_rowconfigure(0, weight=1)
        mainFrame.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (Controls_Editor, Controls_Generator):
            page_name = F.__name__
            frame = F(parent=mainFrame, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame("Controls_Generator")

        displayFrame = Frame(self)
        displayFrame.pack()
        self.brushswap("District")

        """
        need to make a box:
        Display generated name
        have a button for a new name
        have a slider for name length/complexity
        have a button for a name rework where is just moves minor bits
        """

        self.can = Canvas(displayFrame, width=465, height=385, bg="#fffafa")
        self.can.pack()
        #Assigning controls
        self.can.bind("<Button-1>", self.click)
        self.bind("<B1-Motion>", self.drag)
        self.bind('<ButtonRelease-1>', self.clickrelease)
        self.can.bind("<Button-2>", self.mclick)
        self.can.bind("<Button-3>", self.rclick)
        self.can.bind("c", self.key_commit)
        self.can.bind("e", self.key_empty)
        self.can.focus_set()  # keyboard controls won't work unless the window is set to focussed

        """Declaration of variables and database connections"""
        self.vstart = 0  # 60
        self.hstart = 0  # 150
        self.hexagons = []#[0] * 7
        self.rivers = []
        self.rivernodes = []
        self.district_type_feature = []
        self.editing = False
        # count will contain the max row count of each table, which becomes out max limit on our randomization
        self.count = [0] * 14
        """
            count[0] = theme count
            count[1] = settlement feature count
            count[2] = layout count
            count[3] = district type count
            count[4] = district features count
            count[5] = NAMING: generic prefix and center count
            count[6] =  NAMING: generic suffix count
            count[7] =  NAMING: good prefix, center and suffix count
            count[8] =  NAMING: evil prefix, center and suffix count
            count[9] =  NAMING: magical prefix, center and suffix count
            count[10] =  NAMING: dwarven prefix, center and suffix count
            count[11] =  NAMING: elven prefix, center and suffix count
            count[12] =  NAMING: halfling prefix and suffix
            count[13] =  NAMING: orcish prefix and suffix
        """
        # create a database connection
        database = "..\DB\settlement_generator.db"
        self.conn = self.create_connection(database)
        self.count = self.rowcounts(self.conn)  # counts the max rowlength for each table.
        self.generate(True,True) #gotta change the 7 to a calculation
        self.settlementname.set("Settlement Name")

        self.prefix = ""
        self.center = ""
        self.suffix = ""

    #
    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()

    #
    def hexpaint(self):
        for i in self.hexagons:  # re-configure district only
            self.can.itemconfig(i.tags, fill="#a1e2a1")
            if i.district: self.can.itemconfig(i.tags, fill="#53ca53")
            if i.coastal: self.can.itemconfig(i.tags, fill="#0000FF")
            if i.coastal and i.district: self.can.itemconfig(i.tags, fill="#00FFFF")

    #
    def click(self, evt):
        x, y = evt.x, evt.y
        offset = self.can.find_all()[0]  # returns the ID of the first object on the canvas as it increases cnstly.
        clicked = int(self.can.find_closest(x, y)[0]) - offset
        rawclicked = self.can.find_closest(x, y)[0]
        brush = self.editorbrush.get()
        coord = []
        if not self.coastals: self.coastals=[]
        if self.editing and not brush == "River":
            coord = ast.literal_eval(self.hexagons[clicked].tags)

            # clicked equals the ID of the closest canvas object converted to an integer, then subtracted by the offest (the starting object ID on the canvas)
            if brush == "District" and self.hexagons[clicked].district:
                self.hexagons[clicked].district = not self.hexagons[clicked].district
                self.districts.remove(coord)
                print(self.districts)
            elif brush == "District" and not self.hexagons[clicked].district:
                self.hexagons[clicked].district = not self.hexagons[clicked].district
                self.districts.append(coord)
            if brush == "Coastal" and self.hexagons[clicked].coastal:
                self.hexagons[clicked].coastal = not self.hexagons[clicked].coastal
                self.coastals.remove(coord)
            elif brush == "Coastal" and not self.hexagons[clicked].coastal:
                self.hexagons[clicked].coastal = not self.hexagons[clicked].coastal
                self.coastals.append(coord)
        if len(self.coastals) == 0: self.coastals = None

        if brush == "River" and self.can.type(rawclicked) == "oval":
            self.rivercoord = str.split(self.can.gettags(rawclicked)[0],",")
            """LEARN TO SPLIT INTO INT IN ONE STEP"""
            print (self.rivercoord)
            x2 = self.can.bbox(rawclicked)[0]+((self.can.bbox(rawclicked))[2]-(self.can.bbox(rawclicked))[0]) / 2
            y2 = self.can.bbox(rawclicked)[1]+((self.can.bbox(rawclicked))[3]-(self.can.bbox(rawclicked))[1]) / 2
            self.rivselected += 1
            if self.rivselected == 2:
                self.can.itemconfig(self.oldclicked, fill="white")
                h = DrawRiver(self.can,
                              self.x1,
                              self.y1,
                              x2,
                              y2,
                              "#00FFFF",
                              "{},{},{},{}".format(self.x1, self.y1,x2,y2))
                #self.rivers.append(coord)
                self.rivselected=0
            else: self.can.itemconfig(rawclicked, fill="blue")
            self.x1=x2
            self.y1=y2
            self.oldclicked = rawclicked

            self.hexpaint()

    #
    def mclick(self, evt):
        x, y = evt.x, evt.y
        if self.editing:
            offset = self.can.find_all()[0]  # returns the ID of the first object on the canvas as it increases constantly.
            clicked = self.can.find_closest(x, y)[0]  # find closest
            print ("Debug: you clicked a",self.can.type(clicked),
                   "with canvas ID of",clicked-offset,
                   "minus an offset",offset,
                   "at pos",self.can.bbox(clicked))
            self.can.itemconfig(clicked,fill = "#DC143C")

    #
    def drag(self,evt):
        if self.editing and self.editorbrush.get() == "river":
            self.coords["x2"] = evt.x
            self.coords["y2"] = evt.y
            # Change the coordinates of the last created line to the new coordinates
            self.can.coords(self.lines[-1], self.coords["x"], self.coords["y"], self.coords["x2"], self.coords["y2"])

    #
    def clickrelease(self,evt):
        if self.editing:
            x, y = evt.x, evt.y

            offset = self.can.find_all()[0]  # returns the ID of the first object on the canvas as it increases cnstly.
            clicked = int(self.can.find_closest(x, y)[0]) - offset
            rawclicked = self.can.find_closest(x, y)

            brush = self.editorbrush.get()
            if brush == "river" and self.can.type(rawclicked) == "oval":
                print ("clicked a node", rawclicked)
                print (self.can.bbox(rawclicked))
                self.coords["x"] = self.can.bbox(clicked)[0]#(self.can.bbox(clicked)[2]-[0])
                self.coords["y"] = self.can.bbox(clicked)[1]
                #change to be MUCH close to center of node
                self.can.coords(self.lines[-1], self.coords["x"], self.coords["y"], self.coords["x2"], self.coords["y2"])
            #elif brush == "river" and not self.can.type(clicked):    # self.riversnodes[clicked].on = True
            #    print("clicked:", clicked)
            #    self.lines.remove(self.lines[-1])
                # self.rivernodes[clicked].river = not self.hexagons[clicked].river

            self.hexpaint()

    #
    def rclick(self, evt):
        if self.editing:
            offset = self.can.find_all()[
                0]  # returns the ID of the first object on the canvas as it increases constantly.
            x, y = evt.x, evt.y
            clicked = int(self.can.find_closest(x, y)[0]) - offset  # find closest
            self.hexagons[clicked].district = False
            self.hexagons[clicked].coastal = False
            self.hexagons[clicked].river = False
            self.hexpaint()

    #
    def key_empty(self, event=None):
        if self.editing:
            for i in self.hexagons:  # re-configure district only
                i.district = False
                i.coastal = False
                i.river = False
            self.hexpaint()

    #
    def key_commit(self, event=None):
        if self.editing:
            districtstr = ""
            coaststr = ""
            riverstr = ""
            for i, o in enumerate(self.hexagons):  # re-configure district only
                if o.district:
                    districtstr += ", "+ str(o.tags)
                if o.coastal:
                    coaststr += ", "+ str(o.tags)
            districtstr = "["+districtstr[2:]+"]"
            coaststr = "["+coaststr[2:]+"]"
            #if coaststr != "":
            #    layoutstr = layoutstr[0:-1]
            #    layoutstr = layoutstr + ":" + coaststr
            #layoutstr = layoutstr[0:-1]

            print("District Layout: ", districtstr)
            print("Coastal Layout: ", coaststr)
            print("Rivers Layout: ", riverstr)

    #
    def brushswap(self, brush):
        self.editorbrush.set(brush)



    #
    def rivereditor(self,state):
        if state: toggle, fill = NORMAL, "#00FFFF"
        else: toggle, fill = HIDDEN, "white"
        for i in self.rivernodes:
            self.can.itemconfig(i.tags,state=toggle,activefill=fill)
    #
    def rivervisibility (self, state):
        if state == "show":
            for x in self.rivernodes:

                nothing = "nothing"
        else:
            for x in self.rivernodes:
                #print("hide this", x)
                nothing = "nothing"

    #
    def swapeditor(self):#, cols, rows, size):
        # self.key_empty() #new inits wipe i'm pretty sure
        cols = 10
        rows = 7
        size = 30

        self.lines = []
        if self.editing:
            self.editing = False
            self.can.config(background="#fffafa")
            # self.hex_control_frame.pack()
            print("\nSwitched to generator")
            number_of_hexes = len(self.districts)
            if self.coastals: number_of_hexes+= len(self.coastals)
            #self.init_grid(self.districts, self.coastals, [], 10, 7, 30)
            self.generate(False,True)  # default 7 hex size
            #self.controller.show_frame("controls_generator")
        else:
            self.editing = True
            self.can.config(background="#a1e2a1")
            # self.hex_control_frame.forget()
            print("\nSwitched to layout editor")
            self.init_grid([], [], [], cols, rows, size)
            #self.controller.show_frame("controls_layout")
            idoffset = self.can.find_all()[0]  # returns the ID of the first object on the canvas as it increases cnstly.
            for i in self.districts:  # i should be a 2 item list of X and Y of the hex
                if i[1] % 2 == 0:
                    y = i[0] * (size * sqrt(3)) + (size * sqrt(3) / 2) + 25
                else:
                    y = i[0] * (size * sqrt(3)) + 25
                x = i[1] * (size * 1.5) + 30

                clicked = int(self.can.find_closest(x, y)[0]) - idoffset
                self.hexagons[clicked].district = not self.hexagons[clicked].district
            if self.coastals:
                for i in self.coastals:  # i should be a 2 item list of X and Y of the hex
                    if i[1] % 2 == 0:
                        y = i[0] * (size * sqrt(3)) + (size * sqrt(3) / 2) + 25
                    else:
                        y = i[0] * (size * sqrt(3)) + 25
                    x = i[1] * (size * 1.5) + 30

                    clicked = int(self.can.find_closest(x, y)[0]) - idoffset
                    self.hexagons[clicked].coastal = not self.hexagons[clicked].coastal
            self.hexpaint()



            #draw river nodes

    #
    def generate_name(self, locks, type, length):
        with self.conn:
            # print("Max rolls for each table: ",self.count)
            num1=(random.randint(1, self.count[5]))
            num2 = (random.randint(1, self.count[6]))
            precent = self.valuenames(self.conn, "name_generic_precent", "id", str(num1))
            self.prefix = precent[1].split("/")
            self.center = precent[2].split("/")
            self.suffix = self.valuenames(self.conn, "name_generic_suffix", "id", str(num2))
            self.suffix = self.suffix[1].split("/")
        self.refresh_name()

    #
    def refresh_name(self):
        name_part=[0]*3
        name_part[0] = (random.randint(1, len(self.prefix)))-1
        name_part[1] = (random.randint(1, len(self.center)))-1
        name_part[2] = (random.randint(1, len(self.suffix)))-1
        setname = (self.prefix[name_part[0]] + self.center[name_part[1]] + self.suffix[name_part[2]])
        self.settlementname.set(setname)

    # Generates the random values for building the settlement
    def generate_layout(self):
        layoutid = random.randint(1, self.count[2])
        #layoutid = 55
        temp = self.valuenames(self.conn, "layout", "layout_id", str(layoutid))
        return temp

    #
    def generate(self, dolayout,dodistricts):
        settlement_value=[0]*3
        #generates the values for the settlement theme, feature and layout.
        for x in range(2): settlement_value[x]=(random.randint(1, self.count[x]))
        with self.conn:
            settlement_theme = self.valuenames(self.conn, "theme", "theme_id", str(settlement_value[0]))
            settlement_feature = self.valuenames(self.conn, "settlement_feature", "set_feature_id", str(settlement_value[1]))
            if dolayout:
                self.settlement_layout = self.generate_layout()
                self.districts = ast.literal_eval(self.settlement_layout[2])
                if self.settlement_layout[3]: self.coastals = ast.literal_eval(self.settlement_layout[3])
                else: self.coastals = None
                if self.settlement_layout[4]: self.rivers = ast.literal_eval(self.settlement_layout[4])
                else: self.rivers = None
            required_districts = [[],[]]
            required_districts [0]= ["Ruling","Religious","Law and Order","Military","Governing"] #different forms of governing districts
            required_districts [1]= ast.literal_eval(settlement_theme[2])
            #coastals = ast.literal_eval(settlement_layout[3])


            print("\nSettlement "+self.settlementname.get()+":",settlement_theme[1], " ", settlement_feature[1], " ", self.settlement_layout[1], " ")

            if dodistricts:
                valid = 0
                just_districts = []
                self.district_type_feature = [[0, 0] for _ in range(len(self.districts))]
                for x in range(len(self.districts)):
                    #add in list of district ID's .... orrrrrrr check names under required instead of numbers!
                    if len(self.districts)-x==2 and not set(just_districts).intersection(required_districts[0]):
                        value= random.choice(required_districts[0])
                        print ("Governing District set as",value)
                    elif len(self.districts)-x==1 and not set(just_districts).intersection(required_districts[1]):
                        value = random.choice(required_districts[1])
                        print("Thematic District set as", value)
                    else:
                        value= self.valuenames(self.conn, "district_type", "district_type_id", str(random.randint(1, self.count[3])))[1]
                    #I could almost definitely ingest all the values as lists early and just use random.choice for all these...
                    self.district_type_feature[x][0] = value
                    just_districts.append(value)

                    value = self.valuenames(self.conn, "district_feature", "district_feature_id",
                                              str(random.randint(1, self.count[4])))[1]
                    self.district_type_feature[x][1] = value
                    print("District",x+1,self.district_type_feature[x])


        #find max x and max y and throw in either an exception or make the grid bigger
        self.init_grid(self.districts,self.coastals,self.rivers,10,7,30)

    #not called yet. replace init grid with separate draws
    def draw_layout(self, layout_districts, layout_coastal, layout_river, cols, rows, size):
        self.clear_grid()
        if layout_coastal:
            for i in layout_coastal:  # i should be a 2 item list of X and Y of the hex
                n += 1
                if i[1] % 2 == 0:
                    offset = size * sqrt(3) / 2
                else:
                    offset = 0
                h = FillHexagon(self.can,
                                i[1] * (size * 1.5) + 17,
                                (i[0] * (size * sqrt(3))) + offset,
                                size,
                                "#9FB6CD",
                                "#DBDBDB",
                                "[{},{}]".format(i[1], i[0]))
                self.hexagons.append(h)  # list of hexagon objects created by fillhexagon class
        n = -1
        for i in layout_districts:  # i should be a 2 item list of X and Y of the hex
            n += 1
            if i[1] % 2 == 0:
                offset = size * sqrt(3) / 2
            else:
                offset = 0
            h = FillHexagon(self.can,
                            i[1] * (size * 1.5) + 17,
                            (i[0] * (size * sqrt(3))) + offset,
                            size,
                            "#778899",
                            "#111111",
                            "[{},{}]".format(i[1], i[0]))
            self.hexagons.append(h)  # list of hexagon objects created by fillhexagon class
            self.can.create_text(i[1] * (size * 1.5) + (size / 2) + 17,
                                 (i[0] * (size * sqrt(3))) + offset + 10 + (size / 2),
                                 justify=CENTER,
                                 text=(self.district_type_feature[n][0]))
        if layout_river:
            for i in layout_river:  # i should be a 2 item list of X and Y of the hex
                if i[1] % 2 == 0:
                    offset = size * sqrt(3) / 2
                else:
                    offset = 0
                h = DrawRiver(self.can,
                              i[1] * (size * 1.5) + 17,
                              (i[0] * (size * sqrt(3))) + offset,
                              20,
                              20,
                              "#BBFFFF",
                              "[{},{}]".format(i[1], i[0]))
                self.hexagons.append(h)  # list of hexagon objects created by fillhexagon class

    # Draws a hex grid from the parameters sent
    def init_grid(self, layout_districts, layout_coastal, layout_river, cols, rows, size):
        self.clear_grid()

        if self.editing:
            for c in range(cols):
                if c % 2 == 0:
                    offset = size * sqrt(3) / 2  # every even column is offset by the size
                else:
                    offset = 0  # self.vstart #initial offset from border
                for r in range(rows):
                    h = FillHexagon(self.can,
                                    c * (size * 1.5) + 17,
                                    (r * (size * sqrt(3))) + offset,
                                    size,
                                    "#a1e2a1",
                                    "#111111",
                                    "[{},{}]".format(r, c))
                    self.hexagons.append(h)
                    # self.can.create_text(c * (size * 1.5) + (size / 2),
                    #                 (r * (size * sqrt(3))) + offset + (size / 2),
                    #                 text="{}, {}".format(r, c))
            #draw river nodes
            for c in range(cols + 1):
                if not c % 2 == 0:
                    offset_x = 15
                else:
                    offset_x = 0
                x = c * (size * 1.5) + 13 - offset_x

                for r in range(rows * 2 + 1):  # rows*2+1):
                    if not r % 2 == 0:
                        offset_y = -15
                    else:
                        offset_y = 0
                    if not c % 2 == 0 and not r % 2 == 0: offset_y = 15
                    y = r * (size * 0.86) + 23
                    fillvar = "#FFFFFF"
                    if cols - c == 0: fillvar = "#EE3A8C"
                    if rows * 2 - r == 0: fillvar = "#EE3A8C"
                    h = RiverNode(self.can,
                                  x + offset_y,
                                  y,
                                  x + 10 + offset_y,
                                  y + 10,
                                  "#000000",
                                  fillvar,
                                  "{},{}".format(r, c))
                    self.rivernodes.append(h)
            self.rivervisibility("hide")
        else:#if not layout_coastal is None:
            n = -1
            if layout_coastal:
                for i in layout_coastal: #i should be a 2 item list of X and Y of the hex
                    n += 1
                    if i[1] % 2 == 0:
                        offset = size * sqrt(3) / 2
                    else:
                        offset = 0
                    h = FillHexagon(self.can,
                                    i[1] * (size * 1.5) + 17,
                                    (i[0] * (size * sqrt(3))) + offset,
                                    size,
                                    "#9FB6CD",
                                    "#DBDBDB",
                                    "[{},{}]".format(i[1], i[0]))
                    self.hexagons.append(h)  # list of hexagon objects created by fillhexagon class

            n = -1
            for i in layout_districts: #i should be a 2 item list of X and Y of the hex
                n += 1
                if i[1] % 2 == 0:
                    offset = size * sqrt(3) / 2
                else:
                    offset = 0
                h = FillHexagon(self.can,
                                i[1] * (size * 1.5) + 17,
                                (i[0] * (size * sqrt(3))) + offset,
                                size,
                                "#778899",
                                "#111111",
                                "[{},{}]".format(i[1], i[0]))
                self.hexagons.append(h)  # list of hexagon objects created by fillhexagon class
                self.can.create_text(i[1] * (size * 1.5) + (size / 2) + 17,
                                     (i[0] * (size * sqrt(3))) + offset + 10 + (size / 2),
                                     justify=CENTER,
                                     text=(self.district_type_feature[n][0]))
            n = -1
            if layout_river:
                for i in layout_river:  # i should be a 2 item list of X and Y of the hex
                    n += 1
                    if i[1] % 2 == 0:
                        offset = size * sqrt(3) / 2
                    else:
                        offset = 0
                    h = DrawRiver(self.can,
                                    i[1] * (size * 1.5) + 17,
                                    (i[0] * (size * sqrt(3))) + offset,
                                  20,
                                  20,
                                    "#BBFFFF",
                                    "[{},{}]".format(i[1], i[0]))
                    self.hexagons.append(h)  # list of hexagon objects created by fillhexagon class

    # wipes out the list of hexagon objects and draws a rectangle over the canvas.
    def clear_grid(self):
        self.can.delete("all")
        self.hexagons.clear()

    # create a database connection to the SQLite database specified by the db_file
    def create_connection(self, db_file):
        try:
            conn = sqlite3.connect(db_file)
            return conn
        except Error as e:
            print(e)
        return None

    # Query each table for it's rowcount and returns them as count[]
    def rowcounts(self, conn):
        cur = conn.cursor()

        cur.execute("SELECT COUNT(1) from theme")
        (self.count[0],) = cur.fetchone()
        cur.execute("SELECT COUNT(1) from settlement_feature")
        (self.count[1],) = cur.fetchone()
        cur.execute("SELECT COUNT(1) from layout")
        (self.count[2],) = cur.fetchone()
        cur.execute("SELECT COUNT(1) from district_type")
        (self.count[3],) = cur.fetchone()
        cur.execute("SELECT COUNT(1) from district_feature")
        (self.count[4],) = cur.fetchone()
        cur.execute("SELECT COUNT(1) from name_generic_precent")
        (self.count[5],) = cur.fetchone()
        cur.execute("SELECT COUNT(1) from name_generic_suffix")
        (self.count[6],) = cur.fetchone()
        cur.execute("SELECT COUNT(1) from name_good_precentsuf")
        (self.count[7],) = cur.fetchone()
        cur.execute("SELECT COUNT(1) from name_evil_precentsuf")
        (self.count[8],) = cur.fetchone()
        cur.execute("SELECT COUNT(1) from name_magical_precentsuf")
        (self.count[9],) = cur.fetchone()
        cur.execute("SELECT COUNT(1) from name_dwarven_precentsuf")
        (self.count[10],) = cur.fetchone()
        cur.execute("SELECT COUNT(1) from name_elven_precentsuf")
        (self.count[11],) = cur.fetchone()
        cur.execute("SELECT COUNT(1) from name_halfling_presuf")
        (self.count[12],) = cur.fetchone()
        cur.execute("SELECT COUNT(1) from name_orc_presuf")
        (self.count[13],) = cur.fetchone()

        return self.count

    def valuenames(self, conn, table, column, value):
        cur = conn.cursor()
        statement = ("SELECT * FROM " + table + " WHERE " + column + " = " + value)
        cur.execute(statement)
        return cur.fetchone()

# As far as I can tell this is a pythony secure way to launch the main loop.
if __name__ == "__main__":
    app = Main()
    mainloop()