from tkinter import *
from math import cos, sin, sqrt, radians
import random
import os

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

# ---------------------------------------------------------
class App(Tk):

    def __init__(self):
        Tk.__init__(self)
        self.title("Settlement Generator")

        self.vstart = 0 #60
        self.hstart = 0 #150
        self.hexagons = []

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

        self.can = Canvas(main_frame, width=600, height=500, bg="#fffafa")
        self.can.pack()
        #self.hexagons = []

        """ This would be a good place to pull in all your database lengths and such"""
        self.theme_count=14
        self.settlement_feature_count=18
        self.district_type_count=26
        self.district_feature_count=18

        #initializes an array of 49 and populates it with 0
        self.layout = []
        for i in range(49): #can modify this later to be "grid size" instead of static
            self.layout.append(0)

        self.generate(int(e1.get())) #initial call
        #self.layout_populate([17, 18, 24, 25, 26, 31, 32])  # basically calling the default layout of the central 7 hexes, CAN CALL MORE OR LESS
        self.can.bind("<Button-1>", self.click)



    #just makes a new randomized array of hte size sent to it then sends that to the layout_populate
    def generate (self, generate_size):
        #self.cls()
        district_type_feature = [[0]*2]*generate_size #makes a nested list of 2, times how many districts there are
        theme = random.randint(1, self.theme_count+1)
        print ("Settlement Theme: ",theme)
        settlement_feature = random.randint(1, self.settlement_feature_count+1)
        print("Settlement feature: ", settlement_feature)
        for x in range(generate_size):
            district_type_feature[x][0] = random.randint(1, self.district_type_count+1)
            district_type_feature[x][1] = random.randint(1, self.district_feature_count+1)
            print("District type and feature: ",district_type_feature[x])

        generated_hexes = random.sample(range(1,49),generate_size) #change 49 to "grid size"
        print("Hex locations: ", generated_hexes)
        self.layout_populate(generated_hexes)

    # Takes in a list and enables those hexes in the layout list
    def layout_populate (self, layout_positions):
        for x in range(49):
            self.layout[x]=0 #resets the hex array to 0
        for i in layout_positions:
            self.layout[i]=1 #turns on the hexes sent in an array. ie [17, 18, 24, 25, 26, 31, 32] turns on hex 17 etc
        self.init_grid(7, 7, 30, debug=True)  # horizontal, vertical, hex size (side length), draw coordinates

    # Draws a hex grid from the parameters sent
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
                    h = FillHexagon(self.can,
                                c * (size * 1.5),
                                (r * (size * sqrt(3))) + offset,
                                size,
                                "#778899",
                                "#111111",
                                "{}.{}".format(r, c))
                    self.hexagons.append(h)
                    #print (h)
                    if debug:
                        coordinates = "{}, {}".format(r, c)
                        self.can.create_text(c * (size * 1.5) + (size / 2),
                                             (r * (size * sqrt(3))) + offset + (size / 2),
                                             text=coordinates + '\n' + str(n) +" "+ str(hexnum))

    def clear_grid(self):
        self.can.create_rectangle(0,0,600,500,fill="#ffffff")
        self.hexagons.clear()

    # Hex detection on click. Or will be...
    def click(self, evt):
        print(evt)
        """x, y = evt.x, evt.y

        for i in self.hexagons:
            i.selected = False
            self.can.itemconfigure(i.tags, fill=i.color)
            print (i,i.tags)


        for i, o in enumerate(self.hexagons):
            print (i, o, o.tags)
            o.selected = False
            self.can.itemconfigure(o.tags, fill=o.color)

        clicked = self.can.find_closest(x,y)[0]#(x, y)[0]  # find closest
        print(clicked)
        self.hexagons[int(clicked) - 1].selected = True

        for i in self.hexagons:  # goes through all hex objects and sets any marked as selected as green
            if i.selected:
                self.can.itemconfigure(i.tags, fill="#53ca53")
        #    if i.isNeighbour:
        #        self.can.itemconfigure(i.tags, fill="#76d576")
        """


    def cls(self):
        os.system('cls')# if os.name == 'nt' else 'clear')


# ----------------------------------------------------------


if __name__ == "__main__":
    app = App()
    mainloop()
