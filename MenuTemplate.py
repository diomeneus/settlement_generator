from tkinter import *
from tkinter.font import Font
import ast
import os
from tkinter.filedialog import askopenfilename
from tkinter import filedialog
#from fpdf import FPDF

#class He

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

        sm_list = [] #a list of submenus ***MAY BE AN OBSOLETE AND UNNEEDED VARIABLE***
        cbVarList = [] #a list containing lists of variables for checkbox states

        menubar.add_cascade(label="File", underline=0, menu=header1_menu)
        menubar.add_cascade(label="Edit", underline=0, menu=header2_menu)
        menubar.add_command(label="Go", underline=0, command=lambda: showcurrent())

        sm_titles=(["Category1","Category2","Example1"])

        sm1_options = [["Alpha"], ["Beta"], ["Charlie"]]
        sm1_options[0].append(["test1", "test2", "test3", "test4"])
        sm1_options[1].append(["list2stuff", "more stuff"])
        sm1_options[2].append(["example", "w00t"])
        tmplist = []
        for _ in enumerate(sm1_options): tmplist.append(IntVar(self))
        cbVarList.append(tmplist)  # creates an intvar for each option
        sm_list.append(sm1_options)

        sm2_options = [["One"], ["Two"]]
        sm2_options[0].append(["testes", "tester", "testosterone"])
        sm2_options[1].append(["yes", "no"])
        tmplist = []
        for _ in enumerate(sm2_options): tmplist.append(IntVar(self))
        cbVarList.append(tmplist)
        sm_list.append(sm2_options)

        sm3_options = [["Sub1"], ["Sub2"],["Sub3"],["Sub4"]]
        sm3_options[0].append(["Mario", "Luigi", "Peach","Toad"])
        sm3_options[1].append(["dog", "cat"])
        sm3_options[2].append(["car", "plane", "boat"])
        sm3_options[3].append(["Shovel", "Rake","Screwdriver","Drill"])
        tmplist = []
        for _ in enumerate(sm3_options): tmplist.append(IntVar(self))
        cbVarList.append(tmplist)
        sm_list.append(sm3_options)

        for i in cbVarList: #cbVarlist is a list of checkbox lists... this just goes 2 layers deep and defauls them to 1
            for x in i: x.set(1)

        ###HEADER1
        header1_menu.add_command(label="Save PDF", command=lambda: self.exportPDF())
        sm1 = Menu(header1_menu)
        sm1.add_command(label="All",command=lambda :modAll(cbVarList[0],1))
        sm1.add_command(label="None",command=lambda :modAll(cbVarList[0],0))
        sm1.add_separator()
        for index, i in enumerate(sm1_options):
            sm1.add_checkbutton(label=i[0],variable=cbVarList[0][index],onvalue=1,offvalue=0, command = lambda :refreshState())
        header1_menu.add_cascade(label=sm_titles[0],menu=sm1,underline=0)

        sm2 = Menu(header1_menu)
        sm2.add_command(label="All", command=lambda: modAll(cbVarList[1], 1))
        sm2.add_command(label="None", command=lambda: modAll(cbVarList[1], 0))
        sm2.add_separator()
        for index, i in enumerate(sm2_options):
            sm2.add_checkbutton(label=i[0], variable=cbVarList[1][index], onvalue=1, offvalue=0, command = lambda :refreshState())
        header1_menu.add_cascade(label=sm_titles[1], menu=sm2, underline=0)
        header1_menu.add_command(label="Exit", underline=0, command=self.onExit)

        ###HEADER2
        sm3 = Menu(header2_menu)
        sm3.add_command(label="All", command=lambda: modAll(cbVarList[2][0:len(sm3_options)], 1))
        sm3.add_command(label="None", command=lambda: modAll(cbVarList[2][0:len(sm3_options)], 0))
        sm3.add_separator()
        for index, i in enumerate(sm3_options):
            sm3.add_checkbutton(label=i[0], variable=cbVarList[2][index], onvalue=1, offvalue=0, command=lambda: refreshState())
        header2_menu.add_cascade(label=sm_titles[2], menu=sm3, underline=0)

        ###--------------------Textbox--------------------###
        T = Text(self, height=4, width=60)
        T.configure(font=mainfont)
        T.pack()

        # takes a list of variables and sets them to the state requested... need try's to stop you from sending str to an intvar and such
        def modAll(var, state):
            for index, i in enumerate(var):
                var[index].set(state)

        def showcurrent():
            checks_on = []
            checks_off = []
            for x, i in enumerate(cbVarList):
                cat_total = len(cbVarList[x])
                for y, o in enumerate(i):
                    if o.get() == 1:
                        checks_on.append(sm_list[x][y][0])
                    else:
                        checks_off.append(sm_list[x][y][0])
                        cat_total = cat_total-1
                if cat_total == len(cbVarList[x]):
                    print ("All of",sm_titles[x],"selected.")
                elif cat_total > 0:
                    print("Some of",sm_titles[x], "selected")
                else: print ("None of",sm_titles[x], "selected")
            print ("Options  on: ",checks_on)
            print ("Options off:",checks_off)

            #for t in sm_titles:
            #    print (t,)

            textPackage="boobs"
            T.delete(END)
            T.insert(END, textPackage)

        def refreshState():
            print("Option state changed")

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
