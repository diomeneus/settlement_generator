from tkinter import *
from math import cos, sin, sqrt, radians
import random
import os
import sqlite3
from sqlite3 import Error
"""
# ------------------------------------------------------------------------------
class Field:
    types = {
        "grass": "#a1e2a1",
        "water": "#60ace6",
        "mountain": "#a1603a",
        "district": "#778899"
    }

    def __init__(self, parent, x, y, kind, size):
        self.parent = parent
        self.x = x
        self.y = y
        self.kind = kind
        self.color = Field.types[self.kind]
        self.selected = False

    def draw(self):
        FillHexagon(self.parent, self.x, self.y, self.size, self.color)

    def enlight(self):
        pass

"""
# ------------------------------------------------------------------------------

# before it had a separate def to call the draw immediately following the init. couldn't tell why not to combine
class FillHexagon:
    def __init__(self, parent, x, y, length, color, border, tags):
        self.parent = parent  # canvas
        self.start_x = x  # top left x
        self.start_y = y  # top left y
        self.length = length  # length of a side
        self.color = color  # fill color

        self.selected = False
        self.tags = tags
        print (tags)
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
        """self.parent.create_text(x * (length * 1.5) + (length / 2),
                                 (y * (length * sqrt(3))) + (length / 2),
                                 justify=CENTER,
                                 text=text)"""

# ---------------------------------------------------------
class Main(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.title("Settlement Generator")

        self.vstart = 0 #60
        self.hstart = 0 #150
        self.hexagons = [0]*7
        self.district_type_feature = []

        control_frame = Frame(self)
        control_frame.pack(side=LEFT)
        main_frame = Frame(self)
        main_frame.pack(side=RIGHT)

        Label (control_frame, text="Hex Count")
        e1 = Entry(control_frame, width=2)
        e1.insert(END, "7")
        e1.pack(side=LEFT)
        generate_button = Button(control_frame, command=lambda: self.generate(int(e1.get())), text="Generate")
        generate_button.pack(side=LEFT)

        self.can_hex = Canvas(main_frame, width=600, height=500, bg="#fffafa")
        self.can_hex.place(x=0,y=0)
        self.can_hex.pack()
        #self.can_txt = Canvas(main_frame, width=600, height=500, bg="#fffafa")
        #self.can_txt.place(x=0,y=0)
        #self.can_txt.pack()
        #count will contain the max row count of each table, which becomes out max limit on our randomization
        self.count = [0]*5

        # create a database connection
        database = "T:\\sqlite\SQLiteStudio\settlement_generator"
        conn = self.create_connection(database)
        with conn:
            self.count = self.rowcounts(conn)

        #print("Total rows in each table: ", self.count)
        """ This would be a good place to pull in all your database lengths and such"""

        #initializes an array of 49 and populates it with 0
        self.layout = [0]*49 #can mofify 49 to other grid sizes later

        self.generate(int(e1.get())) #initial call
        #self.layout_populate([17, 18, 24, 25, 26, 31, 32])  # basically calling the default layout of the central 7 hexes, CAN CALL MORE OR LESS
        self.can_hex.bind("<Button-1>", self.click)

    #just makes a new randomized array of hte size sent to it then sends that to the layout_populate
    def generate (self, generate_size):
        #self.cls()
        self.district_type_feature = [[0]*2]*generate_size #makes a nested list of 2, times how many districts there are
        settlement_value=[0]*3
        database = "T:\\sqlite\SQLiteStudio\settlement_generator"
        conn = self.create_connection(database)

        #generates the values for the settlement theme, feature and layout.
        for x in range(3):
            settlement_value[x]=(random.randint(1, 6))#self.count[x]+1)) change 7 to the commented text when you have more layouts.
        #generates the values for the districts and their features
        for x in range(generate_size):
            self.district_type_feature[x][0] = self.valuenames(conn,"district_type", "district_type_id", str(random.randint(1, self.count[3] + 1)))
            self.district_type_feature[x][1] = self.valuenames(conn,"district_feature", "district_feature_id", str(random.randint(1, self.count[4] + 1)))
            print("District: ",self.district_type_feature[x]) #this seems to work...
        with conn:
            settlement_theme = self.valuenames(conn, "theme", "theme_id", str(settlement_value[0]))
            settlement_feature = self.valuenames(conn, "settlement_feature", "set_feature_id", str(settlement_value[1]))
            settlement_layout = self.valuenames(conn, "layout", "layout_id", str(settlement_value[2]))
            print(settlement_theme[1], " ", settlement_feature[1], " ", settlement_layout[2])
            # print(settlement_layout[2])

        for x in range(generate_size):
            print(self.district_type_feature[x])

        #splits the layout list into a proper integer list and sends it to be populated.
        #generated_hexes = random.sample(range(1,49),generate_size) #change 49 to "grid size". #true random layout value
        hexes = settlement_layout[2].split('.')
        for x in range(len(hexes)):
            hexes[x]=int(hexes[x])
        self.layout_populate(hexes)


        #settlement_value [0]= self.valuenames(self.conn,"theme", "theme_id",str(self.settlement_value[x]))




    """ CAN I JUST PUT THIS INTO INIT_GRID?"""
    # Takes in a list and enables those hexes in the layout list.
    def layout_populate (self, layout_positions):
        for x in range(49):
            self.layout[x]=0 #resets the hex array to 0
        for i in layout_positions:
            self.layout[i]=1 #turns on the hexes sent in an array. ie [17, 18, 24, 25, 26, 31, 32] turns on hex 17 etc
        self.init_grid(7, 7, 30, debug=True)  #horizontal, vertical, hex size (side length), draw coordinates

    #Draws a hex grid from the parameters sent
    def init_grid(self, cols, rows, size, debug):
        self.clear_grid()
        n=-1
        hexnum=0
        for c in range(cols):
            if c % 2 == 0:
                offset = size * sqrt(3) / 2 # every even column is offset by the size
            else:
                offset = 0 #self.vstart #initial offset from border
            for r in range(rows):
                n = n + 1
                #print (n,n2,self.layout[n],c,r)
                if self.layout[n] == 1:
                    hexnum=hexnum+1
                    cleanprint = self.district_type_feature[hexnum - 1][0]
                    h = FillHexagon(self.can_hex,
                                    c * (size * 1.5),
                                    (r * (size * sqrt(3))) + offset,
                                    size,
                                "#778899",
                                "#111111",
                                "{}.{}".format(r, c))#,"hex")) #SEND THE HEX TAG HERE
                    self.hexagons.append(h) #list of hexagon objects created by fillhexagon class
                    #print (h)
                    if debug:
                        coordinates = "{}, {}".format(r, c)
                        t=self.can_hex.create_text(c * (size * 1.5) + (size / 2),
                                                 (r * (size * sqrt(3))) + offset + (size / 2),
                                                 justify=CENTER,
                                                 text=coordinates +'\n' +str(cleanprint[1]))


    #wipes out the list of hexagon objects and draws a rectangle over the canvas.
    def clear_grid(self):
        self.can_hex.create_rectangle(0, 0, 600, 500, fill="#ffffff")
        self.hexagons.clear()

    #Hex detection on click. Or will be...
    def click(self, evt):
        print(evt)
        x, y = evt.x, evt.y

        """for i, o in enumerate(self.hexagons):
            print (i+1, o, o.tags)
            o.selected = False
            self.can_hex.itemconfigure(o.tags, fill=o.color)"""

        print ("Hexagon List:")
        for i, o in enumerate(self.hexagons):#self.can_hex.find_all()):
            print (i+1, o)#, o.tags,o.start_x,o.start_y)
            o.selected = False
            self.can_hex.itemconfigure(o.tags, fill=o.color)

        for i in self.can_hex.find_all():
            print (self.can_hex.type(i))

        #hex_only = self.can_hex.find_withtag("hex")
        #print ("hex only list: ", hex_only)
        #clicked = hex_only.find_closest(x, y)[0]#(x, y)[0]  # find closest
        clicked = self.can_hex.find_closest(x, y,halo=None,start=8)[0]#(x, y)[0]  # find closest

        if self.can_hex.type(clicked) == "polygon":
            print("closest object ID: ",clicked)
            print ("All canvas objects",self.can_hex.find_all())
            self.hexagons[int(clicked) - 1].selected = True

            for i in self.hexagons:  # goes through all hex objects and sets any marked as selected as green
                if i.selected:
                    self.can_hex.itemconfigure(i.tags, fill="#53ca53")
            #    if i.isNeighbour:
            #        self.can.itemconfigure(i.tags, fill="#76d576")



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
        #print (self.count)
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
