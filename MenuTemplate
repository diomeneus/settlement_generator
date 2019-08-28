from tkinter import *
from tkinter.font import Font
import ast
import os
from tkinter.filedialog import askopenfilename
from tkinter import filedialog
#from fpdf import FPDF

class Main(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.title("Menu Template")
        self.geometry("960x660")#+300+300")
        mainfont = Font(family="Arial", size=10)

        menubar = Menu(self)
        header1_menu = Menu(menubar)
        header2_menu = Menu(menubar)

        self.config(menu=menubar)

        sm1_list = [[],[]] #first value is a list of stored submenus, second is a count
        sm2_list = [[],[]] #[[],0]
        menubar.add_cascade(label="File", underline=0, menu=header1_menu)
        menubar.add_cascade(label="Edit", underline=0, menu=header2_menu)
        menubar.add_command(label="Go", underline=0, command=lambda: showcurrent())

        sm1_Titles=(["Category1","Category2"])
        sm1_1Options = [["Alpha"], ["Beta"], ["Charlie"]]
        sm1_1Options[0].append(["test1", "test2", "test3", "test4"])
        sm1_1Options[1].append(["list2stuff", "more stuff"])
        sm1_1Options[2].append(["example", "w00t"])

        sm1_2Options = [["One"], ["Two"]]
        sm1_2Options[0].append(["testes", "tester", "testosterone"])
        sm1_2Options[1].append(["yes", "no"])

        sm2_Titles = (["Example1"])
        sm2_1Options = [["Sub1"], ["Sub2"],["Sub3"],["Sub4"]]
        sm2_1Options[0].append(["Mario", "Luigi", "Peach","Toad"])
        sm2_1Options[1].append(["dog", "cat"])
        sm2_1Options[2].append(["car", "plane", "boat"])
        sm2_1Options[3].append(["Shovel", "Rake","Screwdriver","Drill"])

        cbVarList=[[],[]]
        for index, x in enumerate(sm1_1Options+sm1_2Options): #Takes the list of sm01options and makes an intVar for each for checkbuttons
            cbVarList[0].append(IntVar(self)) #appends an intVar to the list
            cbVarList[0][index].set(1) #on by default
        cbVarList+=[]
        for index, x in enumerate(sm2_1Options): #Takes the list of smoptions and makes an intVar for each for checkbuttons
            cbVarList[1].append(IntVar(self)) #appends an intVar to the list
            cbVarList[1][index].set(1) #on by default

        ###--------------------HEADER 1 drop down--------------------###
        header1_menu.add_command(label="Save PDF", command=lambda: self.exportPDF())
        #Copy this section and paste for each submenu you add, add single buttons here.
        sm1_1 = Menu(header1_menu)
        sm1_list[0].append(sm1_1)           #adds the menu to a list of menus
        sm1_list[1].append(len(sm1_1Options))     #adds the count of cb options in this menu to a secondary list of matching length
        sm1_1.add_command(label="All",command=lambda :modAll(cbVarList[0][0:len(sm1_1Options)],1))
        sm1_1.add_command(label="None",command=lambda :modAll(cbVarList[0][0:len(sm1_1Options)],0))
        sm1_1.add_separator()
        for index, i in enumerate(sm1_1Options):
            sm1_1.add_checkbutton(label=i[0],variable=cbVarList[0][index],onvalue=1,offvalue=0, command = lambda :refreshState())
        #submenu2
        sm1_2 = Menu(header1_menu)
        sm1_list[0].append(sm1_2)
        sm1_list[1].append(len(sm1_2Options))
        sm1_2.add_command(label="All", command=lambda: modAll(cbVarList[0][-len(sm1_2Options):], 1))
        sm1_2.add_command(label="None", command=lambda: modAll(cbVarList[0][-len(sm1_2Options):], 0))
        sm1_2.add_separator()
        for index, i in enumerate(sm1_2Options, start=len(sm1_1Options)):
            sm1_2.add_checkbutton(label=i[0], variable=cbVarList[0][index], onvalue=1, offvalue=0, command = lambda :refreshState())
        #adds the submenues to the header drop down.
        for index, i in enumerate(sm1_Titles): #adds every sub menu to a different entry under file
            header1_menu.add_cascade(label=i, menu=sm1_list[0][index], underline=0)
        header1_menu.add_command(label="Exit", underline=0, command=self.onExit)

        ###--------------------HEADER 2 drop down--------------------###
        sm2_1 = Menu(header2_menu)
        sm2_list[0].append(sm2_1)
        sm2_list[1].append(len(sm2_1Options))
        sm2_1.add_command(label="All", command=lambda: modAll(cbVarList[1][0:len(sm2_1Options)], 1))
        sm2_1.add_command(label="None", command=lambda: modAll(cbVarList[1][0:len(sm2_1Options)], 0))
        sm2_1.add_separator()
        for index, i in enumerate(sm2_1Options):
            sm2_1.add_checkbutton(label=i[0], variable=cbVarList[1][index], onvalue=1, offvalue=0, command=lambda: refreshState())
        for index, i in enumerate(sm2_Titles):  # adds every sub menu to a different entry under file
            header2_menu.add_cascade(label=i, menu=sm2_list[0][index], underline=0)

        ###--------------------Textbox--------------------###
        T = Text(self, height=4, width=60)
        T.configure(font=mainfont)
        T.pack()
        #T.insert(END, "Just a text Widget\nin two lines\n")

        # takes a list of variables and sets them to the state requested... need try's to stop you from sending str to an intvar and such
        def modAll(var, state):
            for index, i in enumerate(var):
                var[index].set(state)

        def showcurrent():
            for index, list in enumerate(cbVarList, start=1): #a convaluted way to dissassemble which checkboxes are in which menus...
                num = 1
                for n,i in enumerate(list,start=1):
                    if index == 1:
                        if n == sm1_list[1][0]+1: num+=1
                    if index == 2:
                        if n == sm2_list[1][0] + 1: num += 1
                    print ("Header:",index,"submenu:",num,"cb state:",i.get())
                #print (index,list)
            textPackage="boobs"
            T.delete(END)
            T.insert(END, textPackage)

        def refreshState():
            print (cbVarList)

    def exportPDF(self):  # only works properly when invoked from a popup window currently. makes a pdf.
        self.filename = filedialog.asksaveasfilename(initialfile="filename" + ".pdf", initialdir="/",
                                                     title="Select file",
                                                     filetypes=(("pdf files", "*.pdf"), ("all files", "*.*")))
        if self.filename is None: return #return None if closed w/cancel
        else: self.filename = "/temp.pdf"
        print(self.filename)
        """
        pdf = FPDF()
        pdf.add_page()
        width = 8.5 #self.image.width
        height = 11 #self.image.height
        #pdf.set_font("Arial",10)
        pdf.set_xy(width,height)# / 2.25, 10)
        pdf.multi_cell(0, 4, "text")
        pdf.output(self.filename)
        """


    def onExit(self):
        self.quit()

if __name__ == '__main__':
    app = Main()
    mainloop()
