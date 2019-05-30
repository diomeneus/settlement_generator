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
#import pyautogui
class input_name:
    def __init__(self,parent):
        self.controller=parent
        top=self.top=Toplevel(parent)
        self.l=Label(top,text="Enter a Settlement Name")
        self.l.pack()
        self.e=Entry(top)
        self.e.pack()
        self.b=Button(top,text='Ok',command=self.cleanup)
        self.b.pack()
    def cleanup(self):
        self.value=self.e.get()
        #print (self.controller)
        self.controller.settlementname.set(self.value)
        self.top.destroy()

class RiverNode: #draws the circles on Hex corners for making rivers. Should only be visible during river editor
    def __init__(self, parent, x, y, x2, y2, outline, color,tags):
        self.tags = tags
        self.selected = False
        parent.create_oval (x,
                              y,
                              x2,
                              y2,
                              outline = outline,
                              fill= color,
                              tags = self.tags,
                              state=HIDDEN)

class DrawRiver: #pretty self explanatory. Draws a line from coordinates sent with the tags supplied.
    def __init__(self, parent, x, y, x2,y2, color, tags):
        self.rtags = tags
        parent.create_line(x,
                           y,
                           x2,
                           y2,
                           fill=color,
                           width = 5,
                           tags=tags)

class DrawHexagon:
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
        self.disnum = 0

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
        btn_commit = Button(self, text="Print Layout", command=lambda: self.controller.printlayout())
        btn_clear = Button(self, text="Clear Layout", command=lambda: self.controller.key_empty())
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
        self.tkvar_layout,self.tkvar_naming,self.tkvar_namelen = StringVar(self),StringVar(self),StringVar(self)
        #drop_layouts = {'Any', 'Basic', 'Coastal', 'River', 'Confluence', 'Estuary'}
        #tkvar_layout.set('Any')

        #buttons, labels and labelframes
        Button(self, text="Layout Editor",width=18,command=lambda: [self.controller.swapeditor(),controller.show_frame("Controls_Editor")]).grid(column=0,row=0)
        Label(self,text = "").grid(column=0,row=1)#.pack()
        labelframe_gen = LabelFrame(self, text="Generate",labelanchor=N,relief=GROOVE)
        labelframe_gen.grid(column=0,row=2)
        Button(labelframe_gen, text="Layout", height=1,width=9,anchor=W,command=lambda: self.controller.generate(False,False,True, False,self.getlayoutlocks())).grid(column=0,row=0,sticky=W)
        dropmenu_layouts = Menubutton(labelframe_gen, text="Filters", width=9)
        dropmenu_layouts.grid(column=1,row=0)
        Button(labelframe_gen, text="Districts",width=8,anchor=W, command=lambda: self.controller.generate(False,False,False, True,False)).grid(column=0,row=1, sticky=W)
        #dropmenu_layouts = OptionMenu(labelframe_gen, tkvar_layout, *drop_layouts).grid(column=1, row=0, sticky=W)
        Button(labelframe_gen, text="Everything",width=18, command=lambda: self.controller.generate(True,True,True, True,self.getlayoutlocks())).grid(column=0,row=2, sticky=W,columnspan=2)
        Label(self, text="").grid(column=0, row=3)  # .pack()

        dropmenu_layouts.menu = Menu(dropmenu_layouts, tearoff=0)
        dropmenu_layouts["menu"] = dropmenu_layouts.menu

        self.lock_layout_basic = IntVar()
        self.lock_layout_basic.set(1)
        self.lock_layout_coastal = IntVar()
        self.lock_layout_coastal.set(1)
        self.lock_layout_river = IntVar()
        self.lock_layout_river.set(1)
        self.lock_layout_confluence = IntVar()
        self.lock_layout_confluence.set(1)
        self.lock_layout_estuary = IntVar()
        #self.lock_layout_estuary.set(1)
        self.lock_layout_wetland = IntVar()
        #self.lock_layout_wetland.set(1)

        dropmenu_layouts.menu.add_checkbutton(label="Basic", variable=self.lock_layout_basic)
        dropmenu_layouts.menu.add_checkbutton(label="Coastal", variable=self.lock_layout_coastal)
        dropmenu_layouts.menu.add_checkbutton(label="River", variable=self.lock_layout_river)
        dropmenu_layouts.menu.add_checkbutton(label="Confluence", variable=self.lock_layout_confluence)
        dropmenu_layouts.menu.add_checkbutton(label="Estuary", variable=self.lock_layout_estuary)
        dropmenu_layouts.menu.add_checkbutton(label="Wetland", variable=self.lock_layout_wetland)

        labelframe_name =LabelFrame(self, text="Settlement")
        labelframe_name.grid(column=0,row=4)
        Label(labelframe_name, textvariable=controller.settlementname).grid(column=0,row=0,sticky=W)
        Button(labelframe_name, text="Name", width=15, command=lambda: self.controller.generate_name(0, self.tkvar_naming.get(), self.tkvar_namelen.get())).grid(column=0,row=1,sticky=W)
        Button(labelframe_name, text="⭮", width=1,command=lambda: self.controller.refresh_name(self.tkvar_namelen.get())).grid(column=1,row=1,sticky=W)
        Button(labelframe_name, text="↩", width=1,command=lambda: input_name(controller)).grid(column=2, row=1, sticky=W)


        drop_namings = {'Generic', 'Good', 'Evil', 'Magical', 'Dwarven', 'Elven', 'Halfling', 'Orc'}
        self.tkvar_naming.set('Generic')
        drop_namelens = {'Short', 'Any', 'Long'}
        self.tkvar_namelen.set('Any')

        dropmenu_nametype = OptionMenu(labelframe_name, self.tkvar_naming, *drop_namings)
        dropmenu_nametype.grid(column=0,row=5)
        dropmenu_namelength = OptionMenu(labelframe_name, self.tkvar_namelen, *drop_namelens)
        dropmenu_namelength.grid(column=1,row=5)

        # on change dropdown value
        def change_dropdown(*args):
            print(tkvar.get())

        #dropmenu_nametype = Menubutton(labelframe_name, text="Name Type", width=9)
        #dropmenu_nametype.grid(column=0, row=5)
        #dropmenu_namelength = Menubutton(labelframe_name, text="any", width=1)
        #dropmenu_namelength.grid(column=1, row=5)

        #dropmenu_nametype.menu = Menu(drop_namings, tearoff=0)
        #dropmenu_nametype["menu"] = dropmenu_nametype.menu

    def getlayoutlocks(self):
        layoutlocks=[]
        layoutlocks.append(self.lock_layout_basic.get())
        layoutlocks.append(self.lock_layout_coastal.get())
        layoutlocks.append(self.lock_layout_river.get())
        layoutlocks.append(self.lock_layout_confluence.get())
        layoutlocks.append(self.lock_layout_estuary.get())
        layoutlocks.append(self.lock_layout_wetland.get())
        #print (layoutlocks)
        return layoutlocks

class Main(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.settlementname = StringVar()
        self.settlement_theme=["0","0","0","0"]
        self.settlement_feature=["0","0","0","0"]
        self.editorbrush = StringVar()
        self.rivselected,self.num=0,0
        self.coords = {"x": 0, "y": 0, "x2": 0, "y2": 0}
        self.selectednode =[]
        self.fullrandom=False
        self.lastclicked=False
        """Setting up our frames, titles and UI"""
        self.title("Settlement Generator")
        menubar = Menu(self)

        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=lambda: self.open())
        filemenu.add_command(label="Save", command=lambda: self.save(True))
        filemenu.add_command(label="Print", command=lambda: [self.save(False),self.make_print()])
        menubar.add_cascade(label="File", menu=filemenu)

        optionsmenu = Menu(menubar, tearoff=0)
        optionsmenu.add_checkbutton(label="Theme", onvalue=True, offvalue=False)
        optionsmenu.add_checkbutton(label="Feature", onvalue=True, offvalue=False)
        optionsmenu.add_checkbutton(label="Layout", onvalue=True, offvalue=False)
        optionsmenu.add_checkbutton(label="Districts", onvalue=True, offvalue=False)
        optionsmenu.add_checkbutton(label="District Features", onvalue=True, offvalue=False)
        optionsmenu.add_checkbutton(label="Check", onvalue=True, offvalue=False)
        menubar.add_cascade(label="Locks", menu=optionsmenu)


        menubar.add_cascade(label="Options", command=self.popout)

        menubar.add_cascade(label="Popout", command=self.popout)

        self.config(menu=menubar)
        width = 465
        height = 385

        #setting up our frames
        mainFrame = Frame(self)
        mainFrame.grid(column=0,row=0)
        #mainFrame.pack(side="left", fill="both", expand=True)
        #mainFrame.grid_rowconfigure(0, weight=1)
        #mainFrame.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (Controls_Editor, Controls_Generator):
            page_name = F.__name__
            frame = F(parent=mainFrame, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame("Controls_Generator")

        displayFrame = Frame(self)
        displayFrame.grid(column=1,row=0)

        highlightFrame = Frame(self)
        #highlightFrame.config()
        highlightFrame.grid(column=2,row=0)
        buttonwidth = 11

        self.highlight_settheme = StringVar()
        self.highlight_setfeature = StringVar()

        self.btn_reroll_settheme = Button(highlightFrame, text="Theme", width=buttonwidth,command=lambda: self.generate(True,False,False,False,False))
        self.btn_reroll_settheme.grid(row=0, column=0)
        self.btn_reroll_setfeature = Button(highlightFrame, text="Feature", width=buttonwidth,command=lambda: self.generate(False,True,False,False,False))
        self.btn_reroll_setfeature.grid(row=1, column=0)
        self.lbl_settheme = Label(highlightFrame,textvariable=self.highlight_settheme).grid(row=0,column=1)
        self.lbl_setfeature = Label(highlightFrame, textvariable=self.highlight_setfeature).grid(row=1, column=1)


        self.highcan = Canvas(highlightFrame, width=200, height=height/3, bg="#fffafa")
        self.highcan.grid(row=2,column=0,columnspan=2)#.pack()

        self.brushswap("District")


        self.highlighthex = DrawHexagon(self.highcan,
                                        70,
                                        20,
                                        60,
                                        "#9FB6CD",
                                        "#111111",  # DBDBDB",
                                        "[{},{}]".format("y", "x"))
        self.highlighttext = self.highcan.create_text(100,
                                                      80,
                                                      justify=CENTER,
                                                      text="District")
        self.highlighttitle = self.highcan.create_text(70,
                                                      10,
                                                      justify=CENTER,
                                                      text="District")
        self.btn_reroll_district = Button(highlightFrame, text="District Type", width=buttonwidth, command=lambda: self.reroll_feature(self.num,0))
        self.btn_reroll_district.grid(row=3, column=0)
        Button(highlightFrame, text="District Feature", width=buttonwidth, command=lambda: self.reroll_feature(self.num,1)).grid(row=4,column=0)
        self.isreq = Label(highlightFrame, text="Required", width=buttonwidth)
        self.isreq.grid(row=5,column=0)


        self.highlight_district = StringVar()
        self.highlight_feature=StringVar()
        self.highlight_required=StringVar()


        self.lbl_districttype = Label(highlightFrame, textvariable=self.highlight_district).grid(row=3, column=1)
        self.lbl_districtfeature = Label(highlightFrame, textvariable=self.highlight_feature).grid(row=4, column=1)
        self.lbl_required = Label(highlightFrame, textvariable=self.highlight_required).grid(row=5, column=1)

        self.highlightdescription = Text(highlightFrame, height=12, width=15)
        #self.highlightdescription.insert(END, "Description")
        #self.highlightdescription.grid(row=3,column=1,rowspan=18)#self.highlightdescription.pack()#expand=NO, fill=BOTH)
        #self.highlightdescription.config(font="arial", wrap=WORD)

        """
        make a "debug" option that draws info over the canvas
        """
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
        self.count = [0] * 4 #max row of all tables for rolling
        self.layoutcount = [0] * 6  # max row of all tables for rolling
        self.namecount = [0] * 24  # max row of all tables for rolling




        # create a database connection
        database = "..\DB\settlement_generator.db"
        self.conn = self.create_connection(database)
        self.rowcounts(self.conn)  # counts the max rowlength for each table.
        self.generate(True,True,True,True,[1,1,1,1,0,0])
        self.settlementname.set("Settlement Name")

        self.prefix, self.center, self.suffix = "","",""

    def test(self,arg):
        print("successful test of the",arg,"command")

    def screengrab(self): #needs rework.... essentially redraws the entire canvas onto a PIL drawing
        size=30
        self.font=ImageFont.truetype("arial.ttf", 10)
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

    def trim(self,im):
        bg = Image.new(im.mode, im.size, im.getpixel((0, 0)))
        diff = ImageChops.difference(im, bg)
        #diff = ImageChops.add(diff, diff, 2.0, -100)
        bbox = diff.getbbox()
        if bbox:
            return im.crop(bbox)

    def save(self,dialog): #only works properly when invoked from a popup window currently. makes a pdf.
        if dialog:
            self.filename = filedialog.asksaveasfilename(initialfile= self.settlementname.get()+".pdf",initialdir = "/",title = "Select file",filetypes = (("pdf files","*.pdf"),("all files","*.*")))
            if self.filename is None:  # asksaveasfile return `None` if dialog closed with "cancel".
                return
            self.image.save(str(self.settlementname)+".png")

        else: self.filename = "Settlements/" + self.settlementname.get() + ".pdf"
        print (self.filename)
        toptext, bottomtext = self.getdescriptions()
        pdf = FPDF()
        pdf.add_page()
        width = self.image.width
        height = self.image.height
        pdf.image("temp.png")#, x=10, y=8, w=100)
        pdf.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)
        pdf.set_font('DejaVu', '', 12)
        #pdf.cell(200, 10, txt="{}".format("temp.png"), ln=1)
        pdf.set_xy(width/2.25,10)
        pdf.multi_cell(0, 4, toptext)
        pdf.set_xy(10, height/2.5)
        pdf.multi_cell(0, 4, bottomtext)

        #pdf.multi_cell(200, 40, txt=bottomtext, ln=3, align="L")
        pdf.output(self.filename)
        #get a filename you WANT to save as... explorer window or use the settlement name.

    def make_print(self):
        print (self.filename)
        #os.startfile(self.filename, "print")

    def open(self):
        filename = askopenfilename()  # show an "Open" dialog box and return the path to the selected file
        print(filename)

    def getdescriptions(self):
        topquote = "Settlement Name: " + self.settlementname.get() + "\nTheme: " + self.settlement_theme[
            1] + "\nFeature: " + self.settlement_feature[1] + "\n" + self.settlement_feature[2]
        bottomquote = """"""
        for x in range(len(self.districts)):
            bottomquote += "\nDistrict " + str(x + 1) + ": " + str(self.district_type_feature[x][0]) + " - " + str(
                self.district_type_feature[x][2]) + \
                           "\nFeature: " + str(self.district_type_feature[x][1]) + " - " + str(
                self.district_type_feature[x][3]) + "\n"
        for x in (topquote, bottomquote):
            x = x.replace('{', '')
            x = x.replace('}', '')
        return topquote,bottomquote;

    def popout(self): #makes a popup window with the current settlement and the full description.
        if not self.editing:
            width = 800
            height = 600
            self.image = Image.new("RGB", (width, height), "white")
            self.draw = ImageDraw.Draw(self.image)
            self.screengrab()
            self.image = self.trim(self.image)
            popup = Toplevel()
            popup.title(self.settlementname.get())
            popup.geometry("800x600")

            popupbar = Menu(popup)
            popupbar.add_cascade(label="Save", command=lambda: self.save(True))
            popupbar.add_cascade(label="Print", command=lambda: [self.save(False),self.make_print()])
            popupbar.add_cascade(label="Close", command=popup.destroy)
            popup.config(menu=popupbar)
            iwidth = self.image.width
            iheight = self.image.height
            topframe=Frame(popup,width=width,height=iheight)
            topframe.pack(side=TOP)
            bottomframe=Frame(popup,width=width)
            bottomframe.pack(side=BOTTOM)
            leftframe = Frame(topframe, bd=1, width=iwidth, bg="black")
            leftframe.pack(side=LEFT)
            rightframe = Frame(topframe,width=width-iwidth,height=iheight)#,bg="black",bd=1)
            rightframe.pack(side=RIGHT)

            self.image.save("temp.png")
            preview = ImageTk.PhotoImage(Image.open("temp.png"))
            overview = Label(leftframe, image=preview).pack(side=TOP, fill=None, expand=NO)
            topquote,bottomquote = self.getdescriptions()

            TextArea = Text(rightframe, height=self.image.height/18, width=60)
            TextArea.insert(END, topquote)
            TextArea.pack(expand=YES, fill=BOTH)
            TextArea.config(font="arial",wrap=WORD)  # ('Arial', 10, 'bold', 'italic'))

            TextArea2 = Text(bottomframe, height=21.25, width=int(width/9))
            TextArea2.insert(END, bottomquote)
            TextArea2.pack(expand=YES, fill=BOTH)
            TextArea2.config(font="arial",wrap=WORD,)

            popup.mainloop()

    def show_frame(self, page_name): #swaps the left frame from editor to generator controls
        frame = self.frames[page_name]
        frame.tkraise()

    def hexpaint(self): #goes through hexagons stored in a list and sets their background according to their tags.
        for i in self.hexagons:  # re-configure district only
            self.can.itemconfig(i.tags, fill="#a1e2a1")
            if i.district: self.can.itemconfig(i.tags, fill="#53ca53")
            if i.coastal: self.can.itemconfig(i.tags, fill="#0000FF")
            if i.coastal and i.district: self.can.itemconfig(i.tags, fill="#00FFFF")

    def reroll_feature(self,num,type):
        if not self.required or type ==1:
            valueid = random.randint(1, self.count[2+type])
            if type==0:
                value = self.valuenames(self.conn, "district_type", "district_type_id", str(valueid))
            else:
                value = self.valuenames(self.conn, "district_feature", "district_feature_id", str(valueid))
            self.district_type_feature[num][0+type] = value[1]
            self.district_type_feature[num][2+type] = value[2]
            self.generate(False,False,False,False,False)
        else: print("required district")
        #event = ast.literal_eval("<ButtonPress event state=Mod1 num=1 x="+str(self.lastcoord[0])+" y="+str(self.lastcoord[1])+">")

        #pyautogui.click(self.lastcoord[0], self.lastcoord[1])
        #event.x = self.lastcoord[0]
        #event.y = self.lastcoord[1]
        #self.click(evt=ast.literal_eval("<ButtonPress event state=Mod1 num=1 x="+str(self.lastcoord[0])+" y="+str(self.lastcoord[1])+">"))
        #print (self.lastcoord)
        #self.can.itemconfig(self.lastclicked, width=3)

    def click(self, evt): #I no longer know where click starts and clickrelease ends....
        #print (evt)
        x, y = evt.x, evt.y
        offset = self.can.find_all()[0]  # returns the ID of the first object on the canvas as it increases cnstly.
        clicked = int(self.can.find_closest(x, y)[0]) - offset
        rawclicked = self.can.find_closest(x, y)[0]
        brush = self.editorbrush.get()
        coord = []
        if not self.coastals: self.coastals=[]
        if not self.rivers: self.rivers=[]

        if not self.editing and self.can.type(rawclicked) == "polygon":# and self.hexagons(clicked):
            self.can.itemconfig(self.lastclicked, width=1)
            self.can.itemconfig(rawclicked,width=3)
            self.btn_reroll_district.config(fg="black")
            self.required = False

            n=-1
            for x in enumerate(self.hexagons):
                y=x[0]
                #print (self.hexagons[x[0]].disnum)
                if self.hexagons[x[0]].district:
                    n+=1
                    self.hexagons[x[0]].disnum=n

            coord = ast.literal_eval(self.can.gettags(rawclicked)[0])
            self.num = self.hexagons[clicked].disnum
            self.highcan.itemconfig(self.highlighttitle, text="District " + str(self.num+1))
            self.highcan.itemconfig(self.highlighttext,text=self.district_type_feature[self.num][0])

            t1, t2,required =0,0,False
            for x in enumerate(self.districts):
                n=x[0]
                i = {self.district_type_feature[n][0]}
                if set(i).intersection(self.required_districts[0]): t1+=1
                if set(i).intersection((set(self.required_districts[2]))): t2+=1
            i = {self.district_type_feature[self.num][0]}
            if set(i).intersection(self.required_districts[0]) and t1==1:
                self.required = True
                self.btn_reroll_district.config(fg="gray")

            elif set(i).intersection(self.required_districts[2]) and t2==1:
                self.required = True
                self.btn_reroll_district.config(fg="gray")


            self.highlight_district.set (str(self.district_type_feature[self.num][0]))
            self.highlight_feature.set(str(self.district_type_feature[self.num][1]))
            self.highlight_required.set(str(self.required))
            #description = str(self.district_type_feature[self.num][0]) + "\n\n" + str(self.district_type_feature[self.num][1])+"\n\n"+str(self.required)
            #self.highlightdescription.delete('1.0', END)
            #self.highlightdescription.insert(END, description)

            self.lastclicked=rawclicked
            w=self.can.bbox(self.lastclicked)
            #print (w)
            self.lastcoord=[w[0]+30,w[1]+15]
            #print (self.lastcoord)
            #print(self.can.bbox(self.lastclicked))

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
            x2 = self.can.bbox(rawclicked)[0]+((self.can.bbox(rawclicked))[2]-(self.can.bbox(rawclicked))[0]) / 2
            y2 = self.can.bbox(rawclicked)[1]+((self.can.bbox(rawclicked))[3]-(self.can.bbox(rawclicked))[1]) / 2
            self.rivselected += 1
            self.selectednode=self.rivercoord
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
                self.selectednode=[]
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
                   "at pos",self.can.bbox(clicked),
                   "with the tags", self.can.gettags(clicked))
            self.can.itemconfig(clicked,fill = "#DC143C")

    def drag(self,evt): #just for dragging rivers from nodes to nodes.... doesn't check for that though. i'm lazy
        x, y = evt.x, evt.y
        rawclicked = self.can.find_closest(x, y)[0]
        #brush = self.editorbrush.get()
        if self.can.type(rawclicked) == "oval" and self.can.gettags(rawclicked)[0].split(",") != self.selectednode:
            self.click(evt)

    def clickrelease(self,evt):
        if self.editing:
            x, y = evt.x, evt.y

            offset = self.can.find_all()[0]  # returns the ID of the first object on the canvas as it increases cnstly.
            clicked = int(self.can.find_closest(x, y)[0]) - offset
            rawclicked = self.can.find_closest(x, y)

            brush = self.editorbrush.get()
            if brush == "river" and self.can.type(rawclicked) == "oval":
                self.coords["x"] = self.can.bbox(clicked)[0]#(self.can.bbox(clicked)[2]-[0])
                self.coords["y"] = self.can.bbox(clicked)[1]
                #change to be MUCH close to center of node
                self.can.coords(self.lines[-1], self.coords["x"], self.coords["y"], self.coords["x2"], self.coords["y2"])
            self.hexpaint()

    def rclick(self, evt): #right clicking is currently the "erase" function of the editor
        x, y = evt.x, evt.y
        offset = self.can.find_all()[0]  # returns the ID of the FIRST object on the canvas as it increases constantly.
        if self.editing:
            clicked = int(self.can.find_closest(x, y)[0]) - offset  # find closest
            rawclicked = self.can.find_closest(x, y)[0]

            if self.can.type(rawclicked) == "line":
                coord = ast.literal_eval(self.can.gettags(rawclicked)[0])#ast.literal_eval(self.can.gettags(rawclicked)[0])
                coord = list(coord)

                self.can.delete(rawclicked)
                self.rivers.remove(coord)
            else:
                coord = ast.literal_eval(self.hexagons[clicked].tags)
                if self.hexagons[clicked].district:
                    self.districts.remove(coord)
                    self.hexagons[clicked].district = False
                if self.hexagons[clicked].coastal:
                    self.coastals.remove(coord)
                    self.hexagons[clicked].coastal = False

            self.hexpaint()

    def key_empty(self, event=None):
        if self.editing:
            self.districts.clear()
            if self.coastals: self.coastals.clear()
            if self.rivers: self.rivers.clear()
            self.init_grid([],[],[],10,7,30)

    def printlayout(self):
        self.calculatelayout()#diststr,coaststr,riverstr = self.calculatelayout()
        print ("\nlayout type: ",self.layouttype)
        print ("disctricts:  ",self.districts)
        print ("coastals:    ",self.coastals)
        print ("rivers:      ",self.rivers,"\n")

    def calculatelayout(self):
        coaststr, riverstr = "",""
        diststr =  "'"+str(self.districts)+"'"
        if not self.coastals: coaststr = "NULL"
        elif self.coastals == "" or len(self.coastals) == 0: coaststr="NULL"
        else: coaststr = "'"+str(self.coastals)+"'"

        if not self.rivers: riverstr = "NULL"
        elif self.rivers == "" or len(self.rivers) == 0: riverstr = "NULL"
        else:
            riverstr = "'"+str(self.rivers)+"'"
            #Checking for a splitting river
            nodelist =[]
            confluence=False
            for x in self.rivers:
                check1=[x[0],x[1]]
                check2=[x[2],x[3]]
                nodelist.append(check1)
                nodelist.append(check2)
            for i in nodelist:
                n = 0
                for x in enumerate(nodelist):
                    if i == x[1]: n+=1
                    if n == 3: confluence=True

        if not coaststr == "NULL" and not riverstr == "NULL" and not confluence:
            self.layouttype = "estuary"
        elif not coaststr == "NULL" and not riverstr == "NULL":
            self.layouttype = "wetland"
        elif not coaststr == "NULL" and riverstr == "NULL":
            self.layouttype = "coastal"
        elif coaststr == "NULL" and not riverstr == "NULL" and not confluence:
            self.layouttype = "rivers"
        elif coaststr == "NULL" and not riverstr == "NULL":
            self.layouttype = "confluence"
        else: self.layouttype = "basic"
        return diststr, coaststr, riverstr

    def key_commit(self, event=None): #writes the layout string lists to the database
        diststr,coaststr,riverstr = self.calculatelayout()
        self.printlayout()
        with self.conn:
            cur = self.conn.cursor()
            statement = ("INSERT INTO layout_"+self.layouttype+"(layout_rivers,layout_coastal,layout_districts)VALUES("+riverstr+","+coaststr+","+diststr+");")
            print ("to be added to a personal database... later...\n",statement)
            #cur.execute(statement)
            #print("*********************************Layout committed to database*********************************")

    def brushswap(self, brush): #weeeeeeeeeeeee
        self.editorbrush.set(brush)

    def rivereditor(self,state): #receives true or false and sets all the river nodes to hidden or visible accordingly.
        if state: toggle, fill = NORMAL, "#00FFFF"
        else: toggle, fill = HIDDEN, "white"
        for i in self.rivernodes:
            self.can.itemconfig(i.tags,state=toggle,activefill=fill)

    def swapeditor(self): #ideally i think all the hexes should exist and just have their state swapped but this currently destroys the layout, makes a grid of hexes, then reads the existing coord lists and turns those hexes on
        # self.key_empty() #new inits wipe i'm pretty sure
        cols, rows, size = 10, 7, 30
        self.lines = []
        if self.editing:
            self.editing = False
            self.can.config(background="#fffafa")
            self.generate(False,False,False,True,False)
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

    def generate_name(self, locks, type, length): # pre - prefic, cent - center, suf - suffix
        #print ("length:",length,"type:",type)
        nametypes = ["Generic", "Good", "Evil", "Magical", "Dwarven", "Elven", "Halfling", "Orc"]
        n = nametypes.index(type)*3
        with self.conn:
            preid = (random.randint(1, self.namecount[n]))
            cenid = (random.randint(1, self.namecount[n+1]))
            sufid = (random.randint(1, self.namecount[n+2]))
            pre = self.valuenames(self.conn, "name_"+type+"_prefix", "id", str(preid))
            cen = self.valuenames(self.conn, "name_"+type+"_center", "id", str(cenid))
            suf = self.valuenames(self.conn, "name_"+type+"_suffix", "id", str(sufid))
            if pre: self.prefix = pre[1].split("/")
            if cen: self.center = cen[1].split("/")
            if suf: self.suffix = suf[1].split("/")
            #self.suffix = self.suffix[1].split("/")
        self.refresh_name(length)

    #def input_name(self):


    def refresh_name(self,length): #rerolls the name components only. Essentialy a "soft reroll"
        name_part=[0]*3
        name_part[0] = (random.randint(1, len(self.prefix)))-1
        if length == "Long":
            name_part[1] = (random.randint(1, len(self.center)))-1
            print ("long name")
        elif length == "Any" and random.randint(1, 2) == 2:
            name_part[1] = (random.randint(1, len(self.center))) - 1
            print("long name")
        else:
            name_part[1]= -1
            print("short name")
        #print(name_part[1])

        name_part[2] = (random.randint(1, len(self.suffix)))-1
        if name_part[1]== -1: middle = ""
        else: middle = self.center[name_part[1]]
        setname = (self.prefix[name_part[0]] + middle + self.suffix[name_part[2]])
        self.settlementname.set(setname)

    def generate_layout(self,type): #not sure this needs to be it's own function anymore.... it would be 2 lines included
        if not self.fullrandom:
            num = random.randint(0, 5)
            while type[num]==0:
                print ("reroll")
                num = random.randint(0, 5)
            self.layouttype = ("layout_basic", "layout_coastal", "layout_rivers","layout_confluence", "layout_estuary","layout_wetland")[num]
            layoutid = random.randint(1, self.layoutcount[num])
        else:
            print("make a big list and pull a rando number/layout")
        #layoutid = 55
        temp = self.valuenames(self.conn, self.layouttype, "layout_id", str(layoutid))
        return temp

    def generate(self, dotheme,dofeature, dolayout,dodistricts,layouttype): #rolls a new layout and/or new districts. basically all the rolling.
        settlement_value=[0]*3
        #generates the values for the settlement theme, feature and layout.
        for x in range(2): settlement_value[x]=(random.randint(1, self.count[x]))
        with self.conn:
            if dotheme:
                self.settlement_theme = self.valuenames(self.conn, "theme", "theme_id", str(settlement_value[0]))
                self.highlight_settheme.set(self.settlement_theme[1])
            if dofeature:
                self.settlement_feature = self.valuenames(self.conn, "settlement_feature", "set_feature_id", str(settlement_value[1]))
                self.highlight_setfeature.set(self.settlement_feature[1])
            if dolayout:
                self.settlement_layout = self.generate_layout(layouttype)
                #print (self.settlement_layout)
                self.districts = ast.literal_eval(self.settlement_layout[1])
                if self.settlement_layout[2]: self.coastals = ast.literal_eval(self.settlement_layout[2])
                else: self.coastals = None
                if self.settlement_layout[3]: self.rivers = ast.literal_eval(self.settlement_layout[3])
                else: self.rivers = None
            self.required_districts = [[],[],[]]
            self.required_districts [0]= ["Ruling","Religious","Law and Order","Military","Governing"] #different forms of governing districts#[20,11,9,8,26]#
            self.required_districts [1]= ast.literal_eval(self.settlement_theme[2])
            self.required_districts [2] = ast.literal_eval(self.settlement_theme[3])


            if dodistricts:
                valueid,value  = 0,0
                just_districts = []
                self.district_type_feature = [[0, 0, 0, 0] for _ in range(len(self.districts))]
                for x in range(len(self.districts)):
                    #add in list of district ID's .... orrrrrrr check names under required instead of numbers!
                    if len(self.districts)-x==2 and not set(just_districts).intersection(self.required_districts[0]):
                        valueid= random.choice([20,11,9,8,26])
                        print ("Governing District set as",valueid)
                    elif len(self.districts)-x==1 and not set(just_districts).intersection(self.required_districts[2]):
                        valueid = random.choice(self.required_districts[1])
                        print("Thematic District set as", valueid)
                    else:
                        valueid= random.randint(1, self.count[2])
                    value= self.valuenames(self.conn, "district_type", "district_type_id", str(valueid))
                    #print("dis type",value)

                    #I could almost definitely ingest all the values as lists early and just use random.choice for all these...
                    self.district_type_feature[x][0] = value[1]
                    self.district_type_feature[x][2] = value[2]
                    just_districts.append(value[1])

                    value = self.valuenames(self.conn, "district_feature", "district_feature_id",
                                              str(random.randint(1, self.count[3])))
                    #print("feature type", value)
                    self.district_type_feature[x][1] = value[1]
                    self.district_type_feature[x][3] = value[2]

        self.init_grid(self.districts,self.coastals,self.rivers,10,7,30)

    def show_river (self, size): #was going to hide and show rivers... this just goes through the coord list for rivers and redraws them
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

    #CURRENTLY UNUSED. replace init grid with separate draws
    def draw_layout(self, layout_districts, layout_coastal, layout_river, cols, rows, size):
        self.clear_grid()

        if self.editing:
            for c in range(cols):
                if c % 2 == 0:
                    offset = size * sqrt(3) / 2  # every even column is offset by the size
                else:
                    offset = 0  # self.vstart #initial offset from border
                for r in range(rows):
                    h = DrawHexagon(self.can,
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
                    h = DrawHexagon(self.can,
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
                h = DrawHexagon(self.can,
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
                    h = DrawHexagon(self.can,
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
                    h = DrawHexagon(self.can,
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
                h = DrawHexagon(self.can,
                                i[1] * (size * 1.5) + 17,
                                (i[0] * (size * sqrt(3))) + offset,
                                size,
                                "#778899",
                                "#111111",
                                "[{},{}]".format(i[1], i[0]))
                self.hexagons.append(h)  # list of hexagon objects created by fillhexagon class
                self.hexagons[-1].district = True

                #self.can.create_text(i[1] * (size * 1.5) + (size / 2) + 17,
                #                     (i[0] * (size * sqrt(3))) + offset + 10 + (size / 2),
                #                     justify=CENTER,
                #                     text=(self.district_type_feature[n][0]))
            n=-1
            for i in layout_districts: #i should be a 2 item list of X and Y of the hex
                n += 1
                if i[1] % 2 == 0:
                    offset = size * sqrt(3) / 2
                else:
                    offset = 0
                self.can.create_text(i[1] * (size * 1.5) + (size / 2) + 17,
                                     (i[0] * (size * sqrt(3))) + offset + 10 + (size / 2),
                                     justify=CENTER,
                                     text=(self.district_type_feature[n][0]))
            if layout_river:
                self.show_river(30)
    #def drawtext(self,canvas,x,y,size):

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

        n=0
        for x in ("theme","settlement_feature","district_type","district_feature"):
            cur.execute("SELECT COUNT(1) from "+x)
            (self.count[n],) = cur.fetchone()
            n+=1
        n = 0
        for x in ("layout_basic", "layout_coastal", "layout_rivers","layout_confluence", "layout_estuary","layout_wetland"):
            cur.execute("SELECT COUNT(1) from " + x)
            (self.layoutcount[n],) = cur.fetchone()
            n += 1
        n=0
        for x in ("generic", "good", "evil", "magical", "dwarven", "elven", "halfling", "orc"):
            cur.execute("SELECT COUNT(1) from name_"+x+"_prefix")
            (self.namecount[n],) = cur.fetchone()
            cur.execute("SELECT COUNT(1) from name_"+x+"_center")
            (self.namecount[n+1],) = cur.fetchone()
            cur.execute("SELECT COUNT(1) from name_"+x+"_suffix")
            (self.namecount[n+2],) = cur.fetchone()
            n +=3

    def valuenames(self, conn, table, column, value):
        cur = conn.cursor()
        statement = ("SELECT * FROM " + table + " WHERE " + column + " = " + value)
        cur.execute(statement)
        return cur.fetchone()

# As far as I can tell this is a pythony secure way to launch the main loop.
if __name__ == "__main__":
    app = Main()
    mainloop()