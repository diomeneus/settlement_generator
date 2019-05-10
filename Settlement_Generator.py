from tkinter import *
#import tkinter as tk
from math import cos, sin, sqrt, radians, floor
import math
import random
import os
import sqlite3
import ast
from sqlite3 import Error
from PIL import Image, ImageDraw, ImageTk, ImageFont


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
        #parent.draw

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
        btn_commit = Button(self, text="Print Layout", command=lambda: self.controller.key_commit)
        btn_clear = Button(self, text="Clear Layout", command=lambda: self.controller.key_empty)
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

        #variable declares
        tkvar_layout,tkvar_naming,tkvar_namelen = StringVar(self),StringVar(self),StringVar(self)
        drop_layouts = {'Any', 'Basic', 'Coastal', 'River', 'Confluence', 'Estuary'}
        tkvar_layout.set('Any')
        drop_namings = {'Generic', 'Good', 'Evil', 'Magical', 'Dwarven', 'Elven', 'Halfling', 'Orcish'}
        tkvar_naming.set('Generic')
        drop_namelens = {'Short', 'Any', 'Long'}
        tkvar_namelen.set('Any')

        #buttons, labels and labelframes
        Button(self, text="Layout Editor",width=18,command=lambda: [self.controller.swapeditor(),controller.show_frame("Controls_Editor")]).grid(column=0,row=0)#.pack()
        Label(self,text = "").grid(column=0,row=1)#.pack()
        labelframe_gen = LabelFrame(self, text="Generate",labelanchor=N,relief=GROOVE)
        labelframe_gen.grid(column=0,row=2)
        Button(labelframe_gen, text="Layout", height=1,width=9,anchor=W,command=lambda: self.controller.generate(True, False)).grid(column=0,row=0,sticky=W)#.pack(side=LEFT, anchor=NW, fill=X, expand=YES)
        dropmenu_layouts = Menubutton(labelframe_gen, text="Locks", width=9)#.grid(column=1,row=0, sticky=W)#tkvar_layout, *drop_layouts).grid(column=1,row=0, sticky=W)#.pack(side=LEFT, anchor=NE, fill=X, expand=YES)
        dropmenu_layouts.grid(column=1,row=0)
        Button(labelframe_gen, text="Districts",width=8,anchor=W, command=lambda: self.controller.generate(False, True)).grid(column=0,row=1, sticky=W)#.pack(anchor=W)
        #dropmenu_layouts = OptionMenu(labelframe_gen, tkvar_layout, *drop_layouts).grid(column=1, row=0, sticky=W)
        Button(labelframe_gen, text="Everything",width=18, command=lambda: self.controller.generate(True, True)).grid(column=0,row=2, sticky=W,columnspan=2)#.pack(anchor=W)
        Label(self, text="").grid(column=0, row=3)  # .pack()

        dropmenu_layouts.menu = Menu(dropmenu_layouts, tearoff=0)
        dropmenu_layouts["menu"] = dropmenu_layouts.menu

        self.lock_layout_basic = IntVar()
        self.lock_layout_coastal = IntVar()
        self.lock_layout_river = IntVar()
        self.lock_layout_confluence = IntVar()
        self.lock_layout_estuary = IntVar()

        dropmenu_layouts.menu.add_checkbutton(label="Basic", variable=self.lock_layout_basic)
        dropmenu_layouts.menu.add_checkbutton(label="Coastal", variable=self.lock_layout_coastal)
        dropmenu_layouts.menu.add_checkbutton(label="River", variable=self.lock_layout_river)
        dropmenu_layouts.menu.add_checkbutton(label="Confluence", variable=self.lock_layout_confluence)
        dropmenu_layouts.menu.add_checkbutton(label="Estuary", variable=self.lock_layout_estuary)
        drop_layouts = {'Any', 'Basic', 'Coastal', 'River', 'Confluence', 'Estuary'}

        #def change_dropdown(*args):
        #    print(tkvar_layout.get())
        # link function to change dropdown
        #tkvar_layout.trace('w', change_dropdown)

        labelframe_name =LabelFrame(self, text="Settlement")
        labelframe_name.grid(column=0,row=4)
        Label(labelframe_name, textvariable=controller.settlementname).grid(column=0,row=0,sticky=W)
        Button(labelframe_name, text="Name", width=15, command=lambda: self.controller.generate_name(0, "generic", "short")).grid(column=0,row=1,sticky=W)
        Button(labelframe_name, text="⭮", width=1,command=lambda: self.controller.refresh_name()).grid(column=1,row=1,sticky=W)

        #btn_genname.pack()
        #btn_refreshname.pack()
        # on change dropdown value



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

        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=lambda: self.brushswap("District"))
        filemenu.add_command(label="Save", command=lambda: self.brushswap("Coastal"))
        filemenu.add_command(label="Print", command=lambda: self.brushswap("Coastal"))
        menubar.add_cascade(label="File", menu=filemenu)

        optionsmenu = Menu(menubar, tearoff=0)
        optionsmenu.add_checkbutton(label="Theme", onvalue=True, offvalue=False)
        optionsmenu.add_checkbutton(label="Feature", onvalue=True, offvalue=False)
        optionsmenu.add_checkbutton(label="Layout", onvalue=True, offvalue=False)
        optionsmenu.add_checkbutton(label="Districts", onvalue=True, offvalue=False)
        optionsmenu.add_checkbutton(label="District Features", onvalue=True, offvalue=False)
        optionsmenu.add_checkbutton(label="Check", onvalue=True, offvalue=False)
        menubar.add_cascade(label="Locks", menu=optionsmenu)

        menubar.add_cascade(label="popout", command = self.popout)

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
        width = 465
        height = 385
        self.can = Canvas(displayFrame, width=width, height=height, bg="#fffafa")
        self.can.pack()
        self.image = Image.new("RGB", (width,height), "white")
        self.draw = ImageDraw.Draw(self.image)

        #Assigning controls
        self.can.bind("<Button-1>", self.click)
        self.bind("<B1-Motion>", self.drag)
        self.bind('<ButtonRelease-1>', self.clickrelease)
        self.can.bind("<Button-2>", self.mclick)
        self.can.bind("<Button-3>", self.rclick)
        self.can.bind("c", self.key_commit)
        self.can.bind("e", self.key_empty)
        self.can.focus_set()  #focus the window for keyboard controls

        #Declaration of variables and database connections
        self.vstart = 0  # 60
        self.hstart = 0  # 150
        self.hexagons = []
        self.rivernodes = []
        self.district_type_feature = []
        self.editing = False
        self.count = [0] * 14 #max row of all tables for rolling
            #count[0] = theme count
            #count[1] = settlement feature count
            #count[2] = layout count
            #count[3] = district type count
            #count[4] = district features count
            #count[5-13] = NAMING: generic 5-prefix/center,6-suffix,7-good,8-evil,9-magical,10-dwarven,11-elven,12-halfling,13-orcish

        # create a database connection
        database = "..\DB\settlement_generator.db"
        self.conn = self.create_connection(database)
        self.count = self.rowcounts(self.conn)  # counts the max rowlength for each table.
        self.generate(True,True) #gotta change the 7 to a calculation
        self.settlementname.set("Settlement Name")

        self.prefix, self.center, self.suffix = "","",""

    def export(self):
        print ("This should open a saving dialog that can be printed later. PDF?")

    def test(self,arg):
        print("successful test of the",arg,"command")

    def screengrab(self):
        size=30
        self.font=ImageFont.truetype("arial.ttf", 9)
        if self.coastals:
            for i in self.coastals:  # i should be a 2 item list of X and Y of the hex
                if i[1] % 2 == 0:
                    offset = size * sqrt(3) / 2
                else:
                    offset = 0
                start_x = i[1] * (size * 1.5) + 17
                start_y = (i[0] * (size * sqrt(3))) + offset
                length = size
                color = "#9FB6CD"  # fill color

                angle=60
                coordinates = []
                for i in range(6):
                    end_x = start_x + length * cos(radians(angle * i))
                    end_y = start_y + length * sin(radians(angle * i))
                    coordinates.append([start_x, start_y])
                    start_x = end_x
                    start_y = end_y
                self.draw.polygon((coordinates[0][0],
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
                                           coordinates[5][1]),
                                           fill=color,
                                           outline="#DBDBDB")
        n = -1
        for i in self.districts:  # i should be a 2 item list of X and Y of the hex
            n += 1
            if i[1] % 2 == 0:
                offset = size * sqrt(3) / 2
            else:
                offset = 0
            start_x = i[1] * (size * 1.5) + 17
            start_y = (i[0] * (size * sqrt(3))) + offset
            length = size
            color = "#778899"  # fill color

            angle = 60
            coordinates = []
            for o in range(6):
                end_x = start_x + length * cos(radians(angle * o))
                end_y = start_y + length * sin(radians(angle * o))
                coordinates.append([start_x, start_y])
                start_x = end_x
                start_y = end_y
            self.draw.polygon((coordinates[0][0],
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
                               coordinates[5][1]),
                              fill=color,
                              outline="#111111")
            msglen = self.font.getsize(self.district_type_feature[n][0])
            self.draw.text((i[1] * (size * 1.5) + (size / 2) + 17-(msglen[0]/2),
                                 (i[0] * (size * sqrt(3))) + offset + 5 + (size / 2)),
                                 text=(self.district_type_feature[n][0]),
                                 fill="black",
                                 font=self.font)
        if self.rivers:
            for i in self.rivers:
                c1 = i[1]
                r1 = i[0]
                c2 = i[3]
                r2 = i[2]
                if not c1 % 2 == 0: offset_x1 = 15
                else: offset_x1 = 0
                if not c2 % 2 == 0: offset_x2 = 15
                else: offset_x2 = 0

                if not r1 % 2 == 0: offset_y1 = -15
                else: offset_y1 = 0
                if not c1 % 2 == 0 and not r1 % 2 == 0: offset_y1 = 15
                if not r2 % 2 == 0: offset_y2 = -15
                else: offset_y2 = 0
                if not c2 % 2 == 0 and not r2 % 2 == 0: offset_y2 = 15

                x1 = c1 * (size * 1.5) + 15 - offset_x1
                x2 = c2 * (size * 1.5) + 17 - offset_x2
                y1 = r1 * (size * 0.86) + 27
                y2 = r2 * (size * 0.86) + 27

                self.draw.line((x1 + offset_y1,y1,x2 + offset_y2,y2), fill="blue", width=5)

        #for i in self.can.find_all():
            #print (self.can.type(i))

    def popout(self):
        if not self.editing:
            self.screengrab()
            popup = Toplevel()
            #popup = Tk()
            popup.title(self.settlementname.get())
            popup.geometry('930x768')
            popupbar = Menu(popup)
            popupbar.add_cascade(label="Save", command=lambda: self.test("save"))
            popupbar.add_cascade(label="Print", command=lambda: self.test("print"))
            popupbar.add_cascade(label="Close", command=popup.destroy)
            popup.config(menu=popupbar)
            width, height = 465, 385
            topframe=Frame(popup,width=width)
            topframe.pack(side=TOP)
            bottomframe=Frame(popup,width=width)
            bottomframe.pack(side=BOTTOM)
            leftframe = Frame(topframe, bd=1, width=width/2, bg="black")
            leftframe.pack(side=LEFT)
            rightframe = Frame(topframe,width=width)
            rightframe.pack(side=RIGHT)


            #frame = Frame(popup)
            #frame.pack()
            filename = "temp.png"
            self.image.save(filename)
            preview = ImageTk.PhotoImage(Image.open(filename))
            w, h = preview.width(),preview.height()
            x,y = 0,0
            overview = Label(leftframe, image=preview)
            overview.pack(side=TOP, fill=None, expand=NO)
            """----------------------------------------------------------------------------------------------------------"""
            #popup.can = Canvas(rightframe, width=width, height=height, bg="#fffafa")  # popuup frame?
            #popup.can.pack()
            #popup.can.focus_set()  # keyboard controls won't work unless the window is set to focussed
            topquote = "Settlement Name: " + self.settlementname.get() + "\nTheme: " + self.settlement_theme[
                1] + "\nFeature: " + self.settlement_feature[1] + "\n" + self.settlement_feature[2]
            bottomquote = """"""
            print(self.district_type_feature)
            for x in range(len(self.districts)):
                bottomquote += "\nDistrict " + str(x + 1) +": "+ str(self.district_type_feature[x][0])+" - "+str(self.district_type_feature[x][2]) +\
                               "\nFeature: "+str(self.district_type_feature[x][1])+" - "+str(self.district_type_feature[x][3]) +"\n"
            for x in (topquote, bottomquote):
                x = x.replace('{', '')
                x = x.replace('}', '')

            TextArea = Text(rightframe, height=21.25, width=60)
            TextArea.insert(END, topquote)
            TextArea.pack(expand=YES, fill=BOTH)
            TextArea.config(font="arial",wrap=WORD)  # ('Arial', 10, 'bold', 'italic'))

            TextArea2 = Text(bottomframe, height=21.25, width=120)
            TextArea2.pack(expand=YES, fill=BOTH)
            TextArea2.config(font="arial",wrap=WORD,)


            TextArea2.insert(END, bottomquote)

            popup.mainloop()

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()

    def hexpaint(self):
        for i in self.hexagons:  # re-configure district only
            self.can.itemconfig(i.tags, fill="#a1e2a1")
            if i.district: self.can.itemconfig(i.tags, fill="#53ca53")
            if i.coastal: self.can.itemconfig(i.tags, fill="#0000FF")
            if i.coastal and i.district: self.can.itemconfig(i.tags, fill="#00FFFF")

    def click(self, evt):
        x, y = evt.x, evt.y
        offset = self.can.find_all()[0]  # returns the ID of the first object on the canvas as it increases cnstly.
        clicked = int(self.can.find_closest(x, y)[0]) - offset
        rawclicked = self.can.find_closest(x, y)[0]
        brush = self.editorbrush.get()
        coord = []
        if not self.coastals: self.coastals=[]
        if not self.rivers: self.rivers=[]
        if self.editing and not brush == "River":
            coord = ast.literal_eval(self.hexagons[clicked].tags)

            # clicked equals the ID of the closest canvas object converted to an integer, then subtracted by the offest (the starting object ID on the canvas)
            if brush == "District" and self.hexagons[clicked].district:
                self.hexagons[clicked].district = not self.hexagons[clicked].district
                self.districts.remove(coord)
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
            self.rivercoord = self.can.gettags(rawclicked)[0].split(",")
            #self.rivercoord = str.split(self.can.gettags(rawclicked)[0],",")
            """LEARN TO SPLIT INTO INT IN ONE STEP"""
            x2 = self.can.bbox(rawclicked)[0]+((self.can.bbox(rawclicked))[2]-(self.can.bbox(rawclicked))[0]) / 2
            y2 = self.can.bbox(rawclicked)[1]+((self.can.bbox(rawclicked))[3]-(self.can.bbox(rawclicked))[1]) / 2
            self.rivselected += 1
            if self.rivselected == 2:
                self.can.itemconfig(self.oldclicked, fill="white")
                coord = self.oldriver + self.rivercoord
                for x, o in enumerate(coord): coord[x] = int(coord[x])
                h = DrawRiver(self.can,
                              self.x1,
                              self.y1,
                              x2,
                              y2,
                              "#00FFFF",
                              "{},{},{},{}".format(coord[0], coord[1],coord[2],coord[3]))
                self.rivers.append(coord)
                self.rivselected=0
            else: self.can.itemconfig(rawclicked, fill="blue")
            self.x1=x2
            self.y1=y2
            self.oldclicked = rawclicked
            self.oldriver = self.rivercoord
            self.hexpaint()

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

    def drag(self,evt):
        if self.editing and self.editorbrush.get() == "river":
            self.coords["x2"] = evt.x
            self.coords["y2"] = evt.y
            # Change the coordinates of the last created line to the new coordinates
            self.can.coords(self.lines[-1], self.coords["x"], self.coords["y"], self.coords["x2"], self.coords["y2"])

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
            self.hexpaint()

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

    def key_empty(self, event=None):
        if self.editing:
            self.districts.clear()
            if self.coastals: self.coastals.clear()
            if self.rivers: self.rivers.clear()
            self.init_grid([],[],[],10,7,30)

    def key_commit(self, event=None):
        coaststr, riverstr = "",""
        """for i, o in enumerate(self.hexagons):  # re-configure district only
            if o.district:
                districtstr += ", "+ str(o.tags)
            if o.coastal:
                coaststr += ", "+ str(o.tags)
        districtstr = "["+districtstr[2:]+"]"
        coaststr = "["+coaststr[2:]+"]""  """


        diststr =  "'"+str(self.districts)+"'"
        if not self.coastals: coaststr = "NULL"
        elif self.coastals == "" or len(self.coastals) == 0: coaststr="NULL"
        else: coaststr = "'"+str(self.coastals)+"'"
        if not self.rivers: riverstr = "NULL"
        elif self.rivers == "" or len(self.rivers) == 0: riverstr = "NULL"
        else: riverstr = "'"+str(self.rivers)+"'"
        #+str(riverstr) + "," + str(coaststr) + "," + str(self.districts) + ");")

        if not coaststr == "NULL" and not riverstr == "NULL":
            type = "'Estuary'"
        elif not coaststr == "NULL" and riverstr == "NULL":
            type = "'Coastline'"
        elif coaststr == "NULL" and not riverstr == "NULL":
            type = "'River'"
        else: type = "'Basic'"

        with self.conn:
            cur = self.conn.cursor()
            statement = ("INSERT INTO layout(layout_rivers,layout_coastal,layout_districts,layout_type)VALUES("+riverstr+","+coaststr+","+diststr+","+type+");")
            cur.execute(statement)
            print("Layout committed to database")

    def brushswap(self, brush):
        self.editorbrush.set(brush)

    def rivereditor(self,state):
        if state: toggle, fill = NORMAL, "#00FFFF"
        else: toggle, fill = HIDDEN, "white"
        for i in self.rivernodes:
            self.can.itemconfig(i.tags,state=toggle,activefill=fill)

    def swapeditor(self):#, cols, rows, size):
        # self.key_empty() #new inits wipe i'm pretty sure
        cols, rows, size = 10, 7, 30
        self.lines = []
        if self.editing:
            self.editing = False
            self.can.config(background="#fffafa")
            self.generate(False,True)
        else:
            self.editing = True
            self.can.config(background="#a1e2a1")
            self.init_grid([], [], [], cols, rows, size)
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
            if self.rivers:
                self.show_river(30)

    def generate_name(self, locks, type, length):
        with self.conn:
            num1=(random.randint(1, self.count[5]))
            num2 = (random.randint(1, self.count[6]))
            precent = self.valuenames(self.conn, "name_generic_precent", "id", str(num1))
            self.prefix = precent[1].split("/")
            self.center = precent[2].split("/")
            self.suffix = self.valuenames(self.conn, "name_generic_suffix", "id", str(num2))
            self.suffix = self.suffix[1].split("/")
        self.refresh_name()

    def refresh_name(self):
        name_part=[0]*3
        name_part[0] = (random.randint(1, len(self.prefix)))-1
        name_part[1] = (random.randint(1, len(self.center)))-1
        name_part[2] = (random.randint(1, len(self.suffix)))-1
        setname = (self.prefix[name_part[0]] + self.center[name_part[1]] + self.suffix[name_part[2]])
        self.settlementname.set(setname)

    def generate_layout(self):
        layoutid = random.randint(1, self.count[2])
        #layoutid = 55
        temp = self.valuenames(self.conn, "layout", "layout_id", str(layoutid))
        return temp

    def generate(self, dolayout,dodistricts):
        settlement_value=[0]*3
        #generates the values for the settlement theme, feature and layout.
        for x in range(2): settlement_value[x]=(random.randint(1, self.count[x]))
        with self.conn:
            self.settlement_theme = self.valuenames(self.conn, "theme", "theme_id", str(settlement_value[0]))
            self.settlement_feature = self.valuenames(self.conn, "settlement_feature", "set_feature_id", str(settlement_value[1]))
            if dolayout:
                self.settlement_layout = self.generate_layout()
                self.districts = ast.literal_eval(self.settlement_layout[2])
                if self.settlement_layout[3]: self.coastals = ast.literal_eval(self.settlement_layout[3])
                else: self.coastals = None
                if self.settlement_layout[4]: self.rivers = ast.literal_eval(self.settlement_layout[4])
                else: self.rivers = None
            required_districts = [[],[],[]]
            required_districts [0]= ["Ruling","Religious","Law and Order","Military","Governing"] #different forms of governing districts#[20,11,9,8,26]#
            required_districts [1]= ast.literal_eval(self.settlement_theme[2])
            required_districts [2] = ast.literal_eval(self.settlement_theme[3])


            if dodistricts:
                valueid,value  = 0,0
                just_districts = []
                self.district_type_feature = [[0, 0, 0, 0] for _ in range(len(self.districts))]
                for x in range(len(self.districts)):
                    #add in list of district ID's .... orrrrrrr check names under required instead of numbers!
                    if len(self.districts)-x==2 and not set(just_districts).intersection(required_districts[0]):
                        valueid= random.choice([20,11,9,8,26])
                        print ("Governing District set as",valueid)
                    elif len(self.districts)-x==1 and not set(just_districts).intersection(required_districts[2]):
                        valueid = random.choice(required_districts[1])
                        print("Thematic District set as", valueid)
                    else:
                        valueid= random.randint(1, self.count[3])
                    value= self.valuenames(self.conn, "district_type", "district_type_id", str(valueid))
                    #print("dis type",value)

                    #I could almost definitely ingest all the values as lists early and just use random.choice for all these...
                    self.district_type_feature[x][0] = value[1]
                    self.district_type_feature[x][2] = value[2]
                    just_districts.append(value[1])

                    value = self.valuenames(self.conn, "district_feature", "district_feature_id",
                                              str(random.randint(1, self.count[4])))
                    #print("feature type", value)
                    self.district_type_feature[x][1] = value[1]
                    self.district_type_feature[x][3] = value[2]

        self.init_grid(self.districts,self.coastals,self.rivers,10,7,30)

    def show_river (self, size):
        for i in self.rivers:
            c1 = i[1]
            r1 = i[0]
            c2 = i[3]
            r2 = i[2]
            if not c1 % 2 == 0: offset_x1 = 15
            else: offset_x1 = 0
            if not c2 % 2 == 0: offset_x2 = 15
            else: offset_x2 = 0

            if not r1 % 2 == 0: offset_y1 = -15
            else: offset_y1 = 0
            if not c1 % 2 == 0 and not r1 % 2 == 0: offset_y1 = 15
            if not r2 % 2 == 0: offset_y2 = -15
            else: offset_y2 = 0
            if not c2 % 2 == 0 and not r2 % 2 == 0: offset_y2 = 15

            x1 = c1 * (size * 1.5) + 15 - offset_x1
            x2 = c2 * (size * 1.5) + 17 - offset_x2
            y1 = r1 * (size * 0.86) + 27
            y2 = r2 * (size * 0.86) + 27

            h = DrawRiver(self.can,
                          x1 + offset_y1,
                          y1,
                          x2 + offset_y2,
                          y2,
                          "blue",
                          "{},{},{},{}".format(r1, c1, r2, c2))
            # self.rivers.append(h)

    #not called yet. replace init grid with separate draws
    def draw_layout(self, layout_districts, layout_coastal, layout_river, cols, rows, size):
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
            # draw river nodes
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
            # self.rivervisibility("hide")
        else:
            if layout_coastal:
                for i in layout_coastal:  # i should be a 2 item list of X and Y of the hex
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
            n = -1
            if layout_river:
                for i, o in enumerate(layout_river):
                    x1 = o[0]
                    y1 = o[1]
                    x2 = o[2]
                    y2 = o[3]
                    tag1 = str(x1) + "," + str(y1)
                    tag2 = [x2, y2]

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
            #self.rivervisibility("hide")
        else:
            if layout_coastal:
                for i in layout_coastal: #i should be a 2 item list of X and Y of the hex
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
            if layout_river:
                self.show_river(30)

    def clear_grid(self):
        self.can.delete("all")
        self.hexagons.clear()

    def create_connection(self, db_file):
        try:
            conn = sqlite3.connect(db_file)
            return conn
        except Error as e:
            print(e)
        return None

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