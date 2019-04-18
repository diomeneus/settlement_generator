from tkinter import *
from math import cos, sin, sqrt, radians
import random
import os
import sqlite3
import ast

from sqlite3 import Error

class DrawRiver:
    def __init__(self, parent, nodes,x,y,length, color,tags):
        self.parent = parent  # canvas
        self.start_x = x  # top left x
        self.start_y = y  # top left y
        self.length = length  # length of a side
        self.color = color  # fill color
        self.tags = tags
        self.nodes = nodes

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
                                   tags=self.tags)

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


# before it had a separate def to call the draw immediately following the init. couldn't tell why not to combine

# ---------------------------------------------------------
class Main(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.settlementname = StringVar()
        self.editorbrush = StringVar()


        """Setting up our frames, titles and UI"""
        self.title("Settlement Generator")
        menubar = Menu(self)
        show_all = False

        districtmenu = Menu(menubar, tearoff=0)
        districtmenu.add_command(label="District", command=lambda: self.brushswap("district"))
        districtmenu.add_command(label="Coastal", command=lambda: self.brushswap("coastal"))
        districtmenu.add_command(label="River", command=lambda: self.brushswap("river"))
        menubar.add_cascade(label="Districts", menu=districtmenu)

        optionsmenu = Menu(menubar, tearoff=0)
        optionsmenu.add_checkbutton(label="Check", onvalue=True, offvalue=False, variable=show_all)
        menubar.add_cascade(label="Options", menu=optionsmenu)

        menubar.add_command(label="Generate", command=lambda: self.generate(int(e1.get())))
        menubar.add_separator()
        menubar.add_command(label="Layout Editor", command=self.swapeditor)

        self.config(menu=menubar)

        #setting up our frames
        hex_control_frame = Frame(self,width=200)#, justify=LEFT)
        hex_control_frame.pack(side=LEFT)
        hex_display_frame = Frame(self)
        hex_display_frame.pack()


        Label(hex_control_frame, text="Controls").pack()
        Label(hex_control_frame, textvariable=self.settlementname).pack()
        Label (hex_control_frame, textvariable=self.editorbrush).pack()
        btn_genname = Button(hex_control_frame, text="Generate Name", command=self.generate_name(0,"generic","short"))
        btn_commit = Button(hex_control_frame,text="Commit",command=self.key_commit)
        btn_clear = Button(hex_control_frame, text="Clear", command=self.key_empty)

        e1 = Entry(hex_control_frame, width=10)
        e1.insert(END, "7")
        self.brushswap("district")

        """
        need to make a box:
        Display generated name
        have a button for a new name
        have a slider for name length/complexity
        have a button for a name rework where is just moves minor bits
        """
        btn_genname.pack()
        btn_commit.pack()
        btn_clear.pack()
        e1.pack()


        self.can = Canvas(hex_display_frame, width=465, height=385, bg="#fffafa")
        self.can.pack()
        """Assigning controls"""
        self.can.bind("<Button-1>", self.click)
        self.can.bind("<Button-2>", self.mclick)
        self.can.bind("<Button-3>", self.rclick)
        self.can.bind("c", self.key_commit)
        self.can.bind("e", self.key_empty)
        self.can.focus_set() #keyboard controls won't work unless the window is set to focussed

        """Declaration of variables and database connections"""
        self.vstart = 0  # 60
        self.hstart = 0  # 150
        self.hexagons = [0] * 7
        self.district_type_feature = []
        self.editing = False
        #count will contain the max row count of each table, which becomes out max limit on our randomization
        self.count = [0]*14
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
        #with self.conn:

        #initializes an array of 49 for the grid and populates it with 0
        self.layout = [0]*70

        self.generate(int(e1.get())) #initial call
        self.can.bind("<Button-1>", self.click)

    def hexpaint(self):
        for i in self.hexagons:  # re-configure district only
            self.can.itemconfigure(i.tags, fill="#a1e2a1")
            if i.district:
                self.can.itemconfigure(i.tags, fill="#53ca53")
            if i.coastal:
                self.can.itemconfigure(i.tags, fill="#0000FF")
            if i.coastal and i.district:
                self.can.itemconfigure(i.tags, fill="#00FFFF")

    def click(self, evt):
        if self.editing:
            offset = self.can.find_all()[0] #returns the ID of the first object on the canvas as it increases constantly.
            x, y = evt.x, evt.y
            #clicked equals the ID of the closest canvas object converted to an integer, then subtracted by the offest (the starting object ID on the canvas)
            clicked = int(self.can.find_closest(x, y)[0])-offset
            brush = self.editorbrush.get()
            if brush == "district": self.hexagons[clicked].district = not self.hexagons[clicked].district
            if brush == "coastal": self.hexagons[clicked].coastal = not self.hexagons[clicked].coastal
            if brush == "river":
                self.hexagons[clicked].river = not self.hexagons[clicked].river

            self.hexpaint()

    def mclick(self, evt):
        print ("I used to do stuff. Now I do not. For soothe!")
        """if self.editing:
            offset = self.can.find_all()[0]  # returns the ID of the first object on the canvas as it increases constantly.
            x, y = evt.x, evt.y
            clicked = self.can.find_closest(x, y)[0]  # find closest

            if self.hexagons[int(clicked) - offset].coastal:
                self.hexagons[int(clicked) - offset].coastal = False
            else:
                self.hexagons[int(clicked) - offset].coastal = True
            self.hexpaint()
        """

    def rclick(self, evt):
        if self.editing:
            offset = self.can.find_all()[0]  # returns the ID of the first object on the canvas as it increases constantly.
            x, y = evt.x, evt.y
            clicked = int(self.can.find_closest(x, y)[0])-offset  # find closest
            self.hexagons[clicked].district = False
            self.hexagons[clicked].coastal = False
            self.hexagons[clicked].river = False
            self.hexpaint()

    def key_empty(self, event=None):
        if self.editing:
            for i in self.hexagons:  # re-configure district only
                i.district = False
                i.coastal = False
                i.river = False
            self.hexpaint()

    def key_commit(self,event=None):
        if self.editing:
            layoutstr = ""
            coaststr = ""
            for i, o in enumerate(self.hexagons):  # re-configure district only
                if o.district:
                    layoutstr = layoutstr + str(i) + "."
                if o.coastal:
                    coaststr = coaststr + str(i) + "."
            if coaststr != "":
                layoutstr = layoutstr[0:-1]
                layoutstr = layoutstr + ":" + coaststr
            layoutstr = layoutstr[0:-1]

            print(layoutstr)

    def brushswap (self,brush):
        #print ("\nset brush to "+brush)
        self.editorbrush.set(brush)

    def swapeditor (self):
        #self.key_empty() #new inits wipe i'm pretty sure
        if self.editing:
            self.editing = False
            #self.hex_control_frame.pack()
            print ("\nSwitched to generator")
            self.generate(7)  # default 7 hex size
        else:
            self.editing = True
            #self.hex_control_frame.forget()
            print ("\nSwitched to layout editor")
            self.init_grid([], 10, 7, 30)

    def generate_name (self, locks, type, length):
        self.settlementname.set("test text")
        #print("\nNEW NAMES BITCHESSSSS\n")

    #Generates the random values for building the settlement
    def generate (self, generate_size):
        if not self.editing:
            self.district_type_feature = [[0, 0] for _ in range(generate_size)]#makes a nested list of 2, times how many districts there are
            settlement_value=[0]*3
            #generates the values for the settlement theme, feature and layout.
            for x in range(3):
                settlement_value[x]=(random.randint(1, self.count[x]))#self.count[x]+1)) change 6 to the commented text when you have more layouts.
            """temporarily just random 1-10 layout or a specific layout. Delete me"""
            settlement_value[2]=56#(random.randint(1, 50)) #56 is our tester

            #generates the values for the districts and their features
            with self.conn:
                #print("Max rolls for each table: ",self.count)
                settlement_theme = self.valuenames(self.conn, "theme", "theme_id", str(settlement_value[0]))
                settlement_feature = self.valuenames(self.conn, "settlement_feature", "set_feature_id", str(settlement_value[1]))
                settlement_layout = self.valuenames(self.conn, "layout", "layout_id", str(settlement_value[2]))
                # splits the layout list into a proper integer list and sends it to be populated.
                """ layout_hexes is going bye bye """
                layout_hexes = [0] * 3  # * (coastal+river+1)

                river = settlement_layout[2].split('r')
                coastals =river[0].split(':')
                layout_hexes[0]=coastals[0].split('.')
                if len(river)>1:
                    layout_hexes[2] = river[1].split('.')
                    for x in range(len(layout_hexes[2])):
                        layout_hexes[2][x] = layout_hexes[2][x].split('-')
                        for z in range(len(layout_hexes[2][x])):
                            layout_hexes[2][x][z] = int(layout_hexes[2][x][z])
                if len(coastals)>1:
                    layout_hexes[1] = coastals[1].split('.')
                for a in range(2):
                    for x in range(len(layout_hexes[a])):
                        layout_hexes[a][x] = int(layout_hexes[a][x])

                #print("river: ", layout_hexes[2])
                #print("coastal: ", layout_hexes[1])
                #print("district: ", layout_hexes[0])

                #print(settlement_theme[1], " ", settlement_feature[1], " ", settlement_layout[1], " ",layout_hexes[0])

                for x in range(len(layout_hexes[0])):
                    value=self.valuenames(self.conn, "district_type", "district_type_id", str(random.randint(1, self.count[3])))[1]
                    self.district_type_feature[x][0] = value
                    value = self.valuenames(self.conn, "district_feature", "district_feature_id",str(random.randint(1, self.count[4])))[1]
                    self.district_type_feature[x][1] = value
                    #print("District ",x+1,self.district_type_feature[x])
            #self.init_grid(layout_hexes, 10, 7, 30)
            sampleDBdistrict = "[[1, 4], [2, 3], [2, 4], [2, 5], [3, 3], [3, 4], [3, 5]]"
            sampleDBcoastal = "[[0, 4], [1, 2], [1, 3], [1, 5], [2, 2]]"
            sampleDBriver = StringVar()
            print (sampleDBriver)
            districts = ast.literal_eval(sampleDBdistrict)
            coastal = ast.literal_eval(sampleDBcoastal)
            #rivers = ""
            print (districts)
            print (districts[0])
            self.init_grid(districts,coastal,river,10,7,30)

    #Draws a hex grid from the parameters sent
    def init_grid(self, layout_districts,layout_coastal,layout_river, cols, rows, size):
        self.clear_grid()
        x=-1
        for i in layout_districts:
            x+=1
            if layout_districts[x][0] % 2 == 0: offset = size * sqrt(3) / 2
            else: offset = 0
            h = FillHexagon(self.can,
                            layout_districts[x][0] * (size * 1.5) + 17,
                            (layout_districts[x][1] * (size * sqrt(3))) + offset,
                            size,
                            "#778899",
                            "#111111",
                            "{}.{}".format(layout_districts[x][1],layout_districts[x][0]))  # ,"hex")) #SEND THE HEX TAG HERE
            self.hexagons.append(h)  # list of hexagon objects created by fillhexagon class


        """OLD CODE"""

        """
        for x in range(cols*rows):
            self.layout[x]=0 #resets the hex array to 0
        #if you are in editing mode, make the background green, else run through a for loop for each list sent in layout_positions then set self.layout at the position value to 1 for district or 2 for coastline 
        if self.editing:
            self.can.config(background="#a1e2a1")
        else:
            print (len(layout_positions))
            for i in range(len(layout_positions)-1):  #-1 to turn off rivers for now....
                for x in layout_positions[i]:
                    self.layout[x] += 1+i  #sets layout[hex position to turn on] to 1 for district, 2 for coast. right now it will OVERWRITE A DISTRICT. bad
                    print ("i: ",i,"x: ", x, "hex: ",self.layout[x])
            for x in range(len(layout_positions[2])):
                #print (layout_positions[2][x])
                self.layout[layout_positions[2][x][0]] +=4
            self.can.config(background="#fffafa")
            print (self.layout)
        #big endian binary coding: 1111   1= district, 2= coast, 4=river, 8=?,

        districtnum = 0
        hexcount = -1
        for c in range(cols):
            if c % 2 == 0: offset = size * sqrt(3) / 2  # every even column is offset by the size
            else: offset = 0  # self.vstart #initial offset from border
            for r in range(rows):
                hexcount += 1
                if self.layout[hexcount] == 2:
                    coast = FillHexagon(self.can,
                                        c * (size * 1.5)+17,
                                        (r * (size * sqrt(3))) + offset,
                                        size,
                                        "#9FB6CD",
                                        "",#"#DBDBDB",
                                        "{}.{}".format(r, c))
                    self.hexagons.append(coast)  # list of hexagon objects created by fillhexagon class
                elif not self.layout[hexcount] % 2 == 0: #basically if it's an odd number... which means a district
                    h = FillHexagon(self.can,
                                    c * (size * 1.5)+17,
                                    (r * (size * sqrt(3))) + offset,
                                    size,
                                "#778899",
                                "#111111",
                                "{}.{}".format(r, c))#,"hex")) #SEND THE HEX TAG HERE
                    self.hexagons.append(h) #list of hexagon objects created by fillhexagon class
                elif self.layout[hexcount] == 3:
                    print("42")

                elif self.editing:
                    h = FillHexagon(self.can,
                                    c * (size * 1.5)+17,
                                    (r * (size * sqrt(3))) + offset,
                                    size,
                                    "#a1e2a1",
                                    "#111111",
                                    "{}.{}".format(r, c))
                    self.hexagons.append(h)

        hexcount = -1
        for c in range(cols):
            if c % 2 == 0: offset = size * sqrt(3) / 2 # every even column is offset by the size
            else: offset = 0 #self.vstart #initial offset from border
            for r in range(rows):
                hexcount += 1
                if not self.layout[hexcount]  % 2 == 0:
                    districtnum += 1
                    print (districtnum)
                    self.can.create_text(c * (size * 1.5) + (size / 2)+17,
                                     (r * (size * sqrt(3))) + offset + 10 + (size / 2),
                                     justify=CENTER,
                                     text=(self.district_type_feature[districtnum - 1][0]))
        """

    #wipes out the list of hexagon objects and draws a rectangle over the canvas.
    def clear_grid(self):
        self.can.delete("all")
        self.hexagons.clear()

    #supposed to clear the output window.
    def cls(self):
        os.system('cls')# if os.name == 'nt' else 'clear')

    #create a database connection to the SQLite database specified by the db_file
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

    def valuenames(self, conn, table,column, value):
        cur = conn.cursor()
        statement = ("SELECT * FROM "+table+" WHERE "+column+" = "+value)
        cur.execute(statement)
        return cur.fetchone()

#As far as I can tell this is a pythony secure way to launch the main loop.
if __name__ == "__main__":
    app = Main()
    mainloop()
