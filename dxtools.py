# -*- coding: utf-8 -*-
"""
DxTools: Processing XRD data files recorded with the Bruker D8 diffractometer
Copyright 2016-2017 Alexandre  Boulle
alexandre.boulle@unilim.fr
"""
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
import tkinter.ttk as ttk
import matplotlib.pyplot as plt
import os
import sys

from data_reader import *
from data_processor import *

# Custom class to create a status bar from a tk frame
class StatusBar(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        self.label = Label(self, bd=1, relief=FLAT, anchor=W)
        self.label.pack(fill=X)

    def set(self, format, *args):
        self.label.config(text=format % args)
        self.label.update_idletasks()

    def clear(self):
        self.label.config(text="")
        self.label.update_idletasks()
# GUI class
class MyApp(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)

        self.parent = parent
        self.initializeUI()

    def initializeUI(self):
        self.parent.title("Dx Tools")
        self.pack(fill=BOTH, expand="yes")
        self.parent.resizable(width=False, height=False) #fixed window size
        if sys.platform == "win32":
            self.parent.iconbitmap(os.path.join(os.getcwd(),"icon.ico"))
        elif sys.platform == "linux" or sys.platform == "linux2":
            self.parent.wm_iconphoto(True, PhotoImage(file=os.path.join(os.getcwd(),"icon128.gif")))
        self.parent.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.flag_data = 0 # no data on startup
        #****************************************
        #Window size and position
        #****************************************
        w, h = 450, 300
        xc, yc = (self.parent.winfo_screenwidth() - w)/2, (self.parent.winfo_screenheight() - h)/2
        self.parent.geometry("%dx%d+%d+%d" % (w, h, xc, yc))

        #****************************************
        # Create status bar
        #****************************************
        self.status = StatusBar(self)
        self.status.set("Welcome to Dx Tools")
        self.status.pack(side=BOTTOM, fill=X, pady = 2, padx = 5)
        
        #****************************************
        ## Create menu bar
        #****************************************
        menubar = Menu(self.parent, tearoff=0, relief=FLAT)
        self.parent.config(menu=menubar)
        # Create file menu
        fileMenu = Menu(menubar, tearoff=0)
        fileMenu.add_command(label="Import uxd", command=self.importUXD)
        fileMenu.add_command(label="Import brml", command=self.importBRML)
        fileMenu.add_separator()
        fileMenu.add_command(label="Exit", command=self.quit)
        menubar.add_cascade(label="File", menu=fileMenu)
        # Create help menu
        helpMenu = Menu(menubar, tearoff=0)
        helpMenu.add_command(label="About", command=self.about)
        menubar.add_cascade(label="Help", menu=helpMenu)

        #****************************************
        ## Create tab bar
        #****************************************
        nb = ttk.Notebook(self)
        nb.pack(fill='both', expand='yes')
        # create a child frame for each page
        f1 = ttk.Frame()
        f2 = ttk.Frame()
        f3 = ttk.Frame()
        #f4 = ttk.Frame()
        f5 = ttk.Frame()
        f6 = ttk.Frame()
        f7 = ttk.Frame()
        # create the pages
        nb.add(f1, text='RS Map')
        nb.add(f2, text='Temperature')
        nb.add(f3, text='X/Y scan')
        #nb.add(f4, text='XY scan') #Not relevant for a linear beam. Not yet implemented.
        nb.add(f5, text=u'Sin²\u03C8')
        nb.add(f6, text='Pole figure')
        nb.add(f7, text='Custom')

        #****************************************
        # Tab: RS Map
        #****************************************
        f1.columnconfigure(0, weight=1, minsize=82)
        f1.columnconfigure(1, weight=1, minsize=82)
        f1.columnconfigure(2, weight=1, minsize=82)
        f1.columnconfigure(3, weight=1, minsize=82)
        rowsize = 5
        f1.rowconfigure(0, weight=1, minsize=rowsize)
        f1.rowconfigure(1, weight=1, minsize=rowsize)
        f1.rowconfigure(2, weight=1, minsize=rowsize)
        f1.rowconfigure(3, weight=1, minsize=rowsize)
        f1.rowconfigure(4, weight=1, minsize=rowsize)
        f1.rowconfigure(5, weight=1, minsize=rowsize)
        f1.rowconfigure(6, weight=1, minsize=rowsize)
        f1.rowconfigure(7, weight=1, minsize=rowsize)
        f1.rowconfigure(8, weight=1, minsize=rowsize)
        f1.rowconfigure(9, weight=1, minsize=rowsize)
        
        label_options1 = ttk.Label(f1, text="Export options:")
        label_options1.grid(row=0, column=0, sticky = "w", pady = (0,0), padx = (5,0))
        
        self.state_log1= IntVar()
        self.state_log1.set(1)
        button_log1 = ttk.Checkbutton(f1, text="Log(Intensity) scale.", variable=self.state_log1)
        button_log1.grid(row=1, column=0, columnspan = 3, sticky="w", pady = (0,0), padx = (15,0))

        self.state_angmat1 = IntVar()
        self.state_angmat1.set(0)
        button_angmat1 = ttk.Checkbutton(f1, text="Angular-space intensity matrix.", variable=self.state_angmat1)
        button_angmat1.grid(row=2, column=0, columnspan = 3, sticky="w", pady = (0,0), padx = (15,0))

        self.state_qmat1 = IntVar()
        self.state_qmat1.set(1)
        button_qmat1 = ttk.Checkbutton(f1, text="Q-space intensity matrix. Interpolation step (2"+u"\u03C0" +"/" +u"\u212B"+"):", variable=self.state_qmat1)
        button_qmat1.grid(row=3, column=0, columnspan = 4, sticky="w", pady = (0,0), padx = (15,0))
        self.entry_step1=ttk.Entry(f1, width=7)
        self.entry_step1.grid(row = 3, column=3, sticky = "w", pady = (0,0), padx=(0,0))
        self.entry_step1.insert(0,0.0005)
        #label_step1 = ttk.Label(f1, text="(2"+u"\u03C0" +"/" +u"\u212B"+")")
        #label_step1.grid(row=3, column=3,  sticky = "e", pady = (5,0), padx = (5,0))

        self.state_xyz1 = IntVar()
        self.state_xyz1.set(0)
        button_xyzf1 = ttk.Checkbutton(f1, text="3-column format (Qx, Qz, Intensity).", variable=self.state_xyz1)
        button_xyzf1.grid(row=4, column=0, columnspan=3, sticky="w", pady = (0,0), padx = (15,0))

        label_spacer1 = ttk.Label(f1, text="")
        label_spacer1.grid(row=5, column=0, columnspan=3, rowspan=1, sticky = "w", pady = (0,0), padx = (5,0))

        label_skip1 = ttk.Label(f1, text="Skip points at start/stop:")
        label_skip1.grid(row=6, column=0, columnspan=3, rowspan=1, sticky = "w", pady = (0,0), padx = (5,0))
        
        label_skipstartp1 = ttk.Label(f1, text="Primary scanning axis: ")
        label_skipstartp1.grid(row=7, column=0, columnspan=3, sticky = "w", pady = (0,0), padx = (15,0))
        self.entry_skipstartp1=ttk.Entry(f1, width=7)
        self.entry_skipstartp1.grid(row = 7, column=2, sticky = "", pady = (0,0), padx=(0,0))
        self.entry_skipstartp1.insert(0,0)
        self.entry_skipstopp1=ttk.Entry(f1, width = 7)
        self.entry_skipstopp1.grid(row = 7, column=3, sticky = "w", pady = (0,0), padx=(0,0))
        self.entry_skipstopp1.insert(0,0)
        
        label_skipstarts1 = ttk.Label(f1, text="Secondary axis:")
        label_skipstarts1.grid(row=8, column=0, columnspan=3, sticky = "w", pady = (0,0), padx = (15,0))
        self.entry_skipstarts1=ttk.Entry(f1, width=7)
        self.entry_skipstarts1.grid(row = 8, column=2, sticky = "", pady = (0,0), padx=(0,0))
        self.entry_skipstarts1.insert(0,0)
        self.entry_skipstops1=ttk.Entry(f1, width = 7)
        self.entry_skipstops1.grid(row = 8, column=3, sticky = "w", pady = (0,0), padx=(0,0))
        self.entry_skipstops1.insert(0,0)
        
        self.process1=ttk.Button(f1, text="Process Data", command=self.processRSM)
        self.process1.grid(row=9, column=0, columnspan=4, sticky="ew", pady=(0,0), padx=(20,20))
        self.process1.focus()
        self.process1.bind('<Return>', self.processRSM)



        #****************************************
        # Tab: Temperature
        #****************************************
        f2.columnconfigure(0, weight=1, minsize=82)
        f2.columnconfigure(1, weight=1, minsize=82)
        f2.columnconfigure(2, weight=1, minsize=82)
        f2.columnconfigure(3, weight=1, minsize=82)
        f2.rowconfigure(0, weight=1, minsize=rowsize)
        f2.rowconfigure(1, weight=1, minsize=rowsize)
        f2.rowconfigure(2, weight=1, minsize=rowsize)
        f2.rowconfigure(3, weight=1, minsize=rowsize)
        f2.rowconfigure(4, weight=1, minsize=rowsize)
        f2.rowconfigure(5, weight=1, minsize=rowsize)
        f2.rowconfigure(6, weight=1, minsize=rowsize)
        f2.rowconfigure(7, weight=1, minsize=rowsize)
        f2.rowconfigure(8, weight=1, minsize=rowsize)
        f2.rowconfigure(9, weight=1, minsize=rowsize)
        
        
        label_options2 = ttk.Label(f2, text="Export options:")
        label_options2.grid(row=0, column=0, sticky = "w", pady = (0,0), padx = (5,0))
        
        self.state_indv2= IntVar()
        self.state_indv2.set(1)
        button_indv2 = ttk.Checkbutton(f2, text="Individual scans.", variable=self.state_indv2)
        button_indv2.grid(row=1, column=0, columnspan=3, sticky="w", pady = (0,0), padx = (15,0))

        self.state_mat2 = IntVar()
        self.state_mat2.set(0)
        button_mat2 = ttk.Checkbutton(f2, text="Temperature/angle intensity matrix.", variable=self.state_mat2)
        button_mat2.grid(row=2, column=0, columnspan=3, sticky="w", pady = (0,0), padx = (15,0))

        label_analysis2 = ttk.Label(f2, text="Data analysis:")
        label_analysis2.grid(row=3, column=0, columnspan=3, sticky = "w", pady = (0,0), padx = (5,0))

        self.state_fit2 = IntVar()
        self.state_fit2.set(0)
        radio_fit2 = ttk.Radiobutton(f2, text="Numerical intensity integration.", variable= self.state_fit2, value=0)
        radio_fit2.grid(row=4, column=0, columnspan=3, sticky="w", pady = (0,0), padx = (15,0))

        radio_fit2 = ttk.Radiobutton(f2, text="Peak fitting (one peak only).", variable= self.state_fit2, value=1)
        radio_fit2.grid(row=5, column=0, columnspan=3, sticky="w", pady = (0,0), padx = (15,0))

        label_skip2 = ttk.Label(f2, text="Skip points at start/stop:")
        label_skip2.grid(row=6, column=0, columnspan=3, sticky = "w", pady = (0,0), padx = (5,0))

        label_skipstart2 = ttk.Label(f2, text="Primary scanning axis:")
        label_skipstart2.grid(row=7, column=0, columnspan=3, sticky = "w", pady = (0,0), padx = (15,0))
        self.entry_skipstart2=ttk.Entry(f2, width=7)
        self.entry_skipstart2.grid(row = 7, column=2, sticky = "", pady = (0,0))
        self.entry_skipstart2.insert(0,0)
        self.entry_skipstop2=ttk.Entry(f2, width = 7)
        self.entry_skipstop2.grid(row = 7, column=3, sticky = "w", pady = (0,0))
        self.entry_skipstop2.insert(0,0)

        label_skipstartT2 = ttk.Label(f2, text="Temperature range:")
        label_skipstartT2.grid(row=8, column=0, columnspan=3, sticky = "w", pady = (0,0), padx = (15,0))
        self.entry_skipstartT2=ttk.Entry(f2, width=7)
        self.entry_skipstartT2.grid(row = 8, column=2, sticky = "", pady = (0,0))
        self.entry_skipstartT2.insert(0,0)
        self.entry_skipstopT2=ttk.Entry(f2, width = 7)
        self.entry_skipstopT2.grid(row = 8, column=3, sticky = "w", pady = (0,0))
        self.entry_skipstopT2.insert(0,0)


        self.process2=ttk.Button(f2, text="Process Data", command=self.processTemp)
        self.process2.grid(row=9, column=0, columnspan=4, sticky="we", pady=(0,0), padx=(20,20))
        self.process2.focus()
        self.process2.bind('<Return>', self.processTemp)


        #****************************************
        # Tab: X/Y scan
        #****************************************
        f3.columnconfigure(0, weight=1, minsize=82)
        f3.columnconfigure(1, weight=1, minsize=82)
        f3.columnconfigure(2, weight=1, minsize=82)
        f3.columnconfigure(3, weight=1, minsize=82)
        f3.rowconfigure(0, weight=1, minsize=rowsize)
        f3.rowconfigure(1, weight=1, minsize=rowsize)
        f3.rowconfigure(2, weight=1, minsize=rowsize)
        f3.rowconfigure(3, weight=1, minsize=rowsize)
        f3.rowconfigure(4, weight=1, minsize=rowsize)
        f3.rowconfigure(5, weight=1, minsize=rowsize)
        f3.rowconfigure(6, weight=1, minsize=rowsize)
        f3.rowconfigure(7, weight=1, minsize=rowsize)
        f3.rowconfigure(8, weight=1, minsize=rowsize)
        f3.rowconfigure(9, weight=1, minsize=rowsize)
        label_options3 = ttk.Label(f3, text="Export options:")
        label_options3.grid(row=0, column=0, sticky = "w", pady = (0,0), padx = (5,0))

        self.state_indv3= IntVar()
        self.state_indv3.set(1)
        button_indv3 = ttk.Checkbutton(f3, text="Individual scans.", variable=self.state_indv3)
        button_indv3.grid(row=1, column=0, columnspan=3, sticky="w", pady = (0,0), padx = (15,0))

        self.state_mat3 = IntVar()
        self.state_mat3.set(0)
        button_mat3 = ttk.Checkbutton(f3, text="Translation/angle intensity matrix.   ", variable=self.state_mat3)
        button_mat3.grid(row=2, column=0, columnspan=3, sticky="w", pady = (0,0), padx = (15,0))

        label_analysis3 = ttk.Label(f3, text="Data analysis:")
        label_analysis3.grid(row=3, column=0, columnspan=3, sticky = "w", pady = (0,0), padx = (5,0))

        self.state_fit3 = IntVar()
        self.state_fit3.set(0)
        radio_fit3 = ttk.Radiobutton(f3, text="Numerical intensity integration.", variable= self.state_fit3, value=0)
        radio_fit3.grid(row=4, column=0, columnspan=3, sticky="w", pady = (0,0), padx = (15,0))

        radio_fit3 = ttk.Radiobutton(f3, text="Peak fitting (one peak only).", variable= self.state_fit3, value=1)
        radio_fit3.grid(row=5, column=0, columnspan=3, sticky="w", pady = (0,0), padx = (15,0))

        label_skip3 = ttk.Label(f3, text="Skip points at start/stop:")
        label_skip3.grid(row=6, column=0, columnspan=3, sticky = "w", pady = (0,0), padx = (5,0))
        
        label_skipstart3 = ttk.Label(f3, text="Primary scanning axis:")
        label_skipstart3.grid(row=7, column=0, columnspan=3, sticky = "w", pady = (0,0), padx = (15,0))
        self.entry_skipstart3=ttk.Entry(f3, width=7)
        self.entry_skipstart3.grid(row = 7, column=2, sticky = "", pady = (0,0), padx=(0,0))
        self.entry_skipstart3.insert(0,0)
        self.entry_skipstop3=ttk.Entry(f3, width = 7)
        self.entry_skipstop3.grid(row = 7, column=3, sticky = "w", pady = (0,0), padx=(0,0))
        self.entry_skipstop3.insert(0,0)

        label_skipstartX3 = ttk.Label(f3, text="Translation range:")
        label_skipstartX3.grid(row=8, column=0, columnspan = 3, sticky = "w", pady = (0,0), padx = (15,0))
        self.entry_skipstartX3=ttk.Entry(f3, width=7)
        self.entry_skipstartX3.grid(row = 8, column=2, sticky = "", pady = (0,0), padx=(0,0))
        self.entry_skipstartX3.insert(0,0)
        self.entry_skipstopX3=ttk.Entry(f3, width = 7)
        self.entry_skipstopX3.grid(row = 8, column=3, sticky = "w", pady = (0,0), padx=(0,0))
        self.entry_skipstopX3.insert(0,0)


        self.process3=ttk.Button(f3, text="Process Data", command=self.processX)
        self.process3.grid(row=9, column=0, columnspan=4, sticky="ew", pady=(0,0), padx=(20,20))
        self.process3.focus()
        self.process3.bind('<Return>', self.processX)
        
        #****************************************
        # Tab: Sin²Psi
        #****************************************
        f5.columnconfigure(0, weight=1, minsize=82)
        f5.columnconfigure(1, weight=1, minsize=82)
        f5.columnconfigure(2, weight=1, minsize=82)
        f5.columnconfigure(3, weight=1, minsize=82)
        f5.rowconfigure(0, weight=1, minsize=rowsize)
        f5.rowconfigure(1, weight=1, minsize=rowsize)
        f5.rowconfigure(2, weight=1, minsize=rowsize)
        f5.rowconfigure(3, weight=1, minsize=rowsize)
        f5.rowconfigure(4, weight=1, minsize=rowsize)
        f5.rowconfigure(5, weight=1, minsize=rowsize)
        f5.rowconfigure(6, weight=1, minsize=rowsize)
        f5.rowconfigure(7, weight=1, minsize=rowsize)
        f5.rowconfigure(8, weight=1, minsize=rowsize)
        f5.rowconfigure(9, weight=1, minsize=rowsize)
        
        label_options5 = ttk.Label(f5, text="Export options:")
        label_options5.grid(row=0, column=0, sticky = "w", pady = (0,0), padx = (5,0))

        self.state_indv5= IntVar()
        self.state_indv5.set(1)
        button_indv5 = ttk.Checkbutton(f5, text="Individual scans.", variable=self.state_indv5)
        button_indv5.grid(row=1, column=0, columnspan=3, sticky="w", pady = (0,0), padx = (15,0))

        label_spacer5 = ttk.Label(f5, text="")
        label_spacer5.grid(row=2, column=0, columnspan=3, sticky = "w", pady = (0,0), padx = (5,0))
        
        label_analysis5 = ttk.Label(f5, text="Data analysis: ")
        label_analysis5.grid(row=3, column=0, columnspan=3, sticky = "w", pady = (0,0), padx = (5,0))

        self.state_fit5 = IntVar()
        self.state_fit5.set(1)
        radio_fit5 = ttk.Radiobutton(f5, text="d-spacing from peak maximum.", variable= self.state_fit5, value=0)
        radio_fit5.grid(row=4, column=0, columnspan=3, sticky="w", pady = (0,0), padx = (15,0))

        radio_fit5 = ttk.Radiobutton(f5, text="d-spacing from peak fitting (one peak only).", variable= self.state_fit5, value=1)
        radio_fit5.grid(row=5, column=0, columnspan=4,sticky="w", pady = (0,0), padx = (15,0))

        label_skip5 = ttk.Label(f5, text="Skip points at start/stop:")
        label_skip5.grid(row=6, column=0, columnspan=3, sticky = "w", pady = (0,0), padx = (5,0))

        label_skipstart5 = ttk.Label(f5, text="Primary scanning axis:")
        label_skipstart5.grid(row=7, column=0, columnspan=3, sticky = "w", pady = (0,0), padx = (15,0))
        self.entry_skipstart5=ttk.Entry(f5, width=7)
        self.entry_skipstart5.grid(row = 7, column=2, sticky = "", pady = (0,0), padx = (0,0))
        self.entry_skipstart5.insert(0,0)
        self.entry_skipstop5=ttk.Entry(f5, width = 7)
        self.entry_skipstop5.grid(row = 7, column=3, sticky = "w", pady = (0,0), padx = (0,0))
        self.entry_skipstop5.insert(0,0)
        
        label_skipstartpsi5 = ttk.Label(f5, text="Psi range:")
        label_skipstartpsi5.grid(row=8, column=0, columnspan=3, sticky = "w", pady = (0,0), padx = (15,0))
        self.entry_skipstartpsi5=ttk.Entry(f5, width=7)
        self.entry_skipstartpsi5.grid(row = 8, column=2, sticky = "", pady = (0,0), padx = (0,0))
        self.entry_skipstartpsi5.insert(0,0)
        self.entry_skipstoppsi5=ttk.Entry(f5, width = 7)
        self.entry_skipstoppsi5.grid(row = 8, column=3, sticky = "w", pady = (0,0), padx = (0,0))
        self.entry_skipstoppsi5.insert(0,0)

        self.process5=ttk.Button(f5, text="Process Data", command=self.processStress)
        self.process5.grid(row=9, column=0, columnspan=4, sticky="ew", pady=(0,0), padx=(20,20))
        self.process5.focus()
        self.process5.bind('<Return>', self.processStress)
        
        #****************************************
        # Tab: Pole figure
        #****************************************
        f6.columnconfigure(0, weight=1, minsize=82)
        f6.columnconfigure(1, weight=1, minsize=82)
        f6.columnconfigure(2, weight=1, minsize=82)
        f6.columnconfigure(3, weight=1, minsize=82)
        f6.rowconfigure(0, weight=1, minsize=rowsize)
        f6.rowconfigure(1, weight=1, minsize=rowsize)
        f6.rowconfigure(2, weight=1, minsize=rowsize)
        f6.rowconfigure(3, weight=1, minsize=rowsize)
        f6.rowconfigure(4, weight=1, minsize=rowsize)
        f6.rowconfigure(5, weight=1, minsize=rowsize)
        f6.rowconfigure(6, weight=1, minsize=rowsize)
        f6.rowconfigure(7, weight=1, minsize=rowsize)
        f6.rowconfigure(8, weight=1, minsize=rowsize)
        f6.rowconfigure(9, weight=1, minsize=rowsize)
        
        label_options6 = ttk.Label(f6, text="Export options:")
        label_options6.grid(row=0, column=0, sticky = "w", pady = (0,0), padx = (5,0))
        
        self.state_indv6= IntVar()
        self.state_indv6.set(1)
        button_indv6 = ttk.Checkbutton(f6, text="Individual scans.", variable=self.state_indv6)
        button_indv6.grid(row=1, column=0, columnspan=3, sticky="w", pady = (0,0), padx = (15,0))

        self.state_angmat6 = IntVar()
        self.state_angmat6.set(0)
        button_angmat6 = ttk.Checkbutton(f6, text="Chi-Phi intensity matrix.", variable=self.state_angmat6)
        button_angmat6.grid(row=2, column=0, columnspan = 3, sticky="w", pady = (0,0), padx = (15,0))

        self.state_xyz6 = IntVar()
        self.state_xyz6.set(0)
        button_xyzf6 = ttk.Checkbutton(f6, text="3-column format (Chi, Phi, Intensity).", variable=self.state_xyz6)
        button_xyzf6.grid(row=3, column=0, columnspan=3, sticky="w", pady = (0,0), padx = (15,0))
        
        label_spacer6 = ttk.Label(f6, text="")
        label_spacer6.grid(row=4, column=0, columnspan=3, sticky = "w", pady = (0,0), padx = (5,0))
        
        label_spacer62 = ttk.Label(f6, text="")
        label_spacer62.grid(row=5, column=0, columnspan=3, sticky = "w", pady = (0,0), padx = (5,0))

        label_skip6 = ttk.Label(f6, text="Skip points at start/stop:")
        label_skip6.grid(row=6, column=0, columnspan=3, sticky = "w", pady = (0,0), padx = (5,0))
        
        label_skipstartp6 = ttk.Label(f6, text="Primary scanning axis: ")
        label_skipstartp6.grid(row=7, column=0, columnspan=3, sticky = "w", pady = (0,0), padx = (15,0))
        self.entry_skipstartp6=ttk.Entry(f6, width=7)
        self.entry_skipstartp6.grid(row = 7, column=2, sticky = "", pady = (0,0), padx=(0,0))
        self.entry_skipstartp6.insert(0,0)
        self.entry_skipstopp6=ttk.Entry(f6, width = 7)
        self.entry_skipstopp6.grid(row = 7, column=3, sticky = "w", pady = (0,0), padx=(0,0))
        self.entry_skipstopp6.insert(0,0)
        
        label_skipstarts6 = ttk.Label(f6, text="Secondary axis:")
        label_skipstarts6.grid(row=8, column=0, columnspan=3, sticky = "w", pady = (0,0), padx = (15,0))
        self.entry_skipstarts6=ttk.Entry(f6, width=7)
        self.entry_skipstarts6.grid(row = 8, column=2, sticky = "", pady = (0,0), padx=(0,0))
        self.entry_skipstarts6.insert(0,0)
        self.entry_skipstops6=ttk.Entry(f6, width = 7)
        self.entry_skipstops6.grid(row = 8, column=3, sticky = "w", pady = (0,0), padx=(0,0))
        self.entry_skipstops6.insert(0,0)
        
        self.process6=ttk.Button(f6, text="Process Data", command=self.processPole)
        self.process6.grid(row=9, column=0, columnspan=4, sticky="ew", pady=(0,0), padx=(20,20))
        self.process6.focus()
        self.process6.bind('<Return>', self.processPole)
        
        ##****************************************
        ## Tab: Custom
        ##****************************************
        f7.columnconfigure(0, weight=1, minsize=82)
        f7.columnconfigure(1, weight=1, minsize=82)
        f7.columnconfigure(2, weight=1, minsize=82)
        f7.columnconfigure(3, weight=1, minsize=82)
        f7.rowconfigure(0, weight=1, minsize=rowsize)
        f7.rowconfigure(1, weight=1, minsize=rowsize)
        f7.rowconfigure(2, weight=1, minsize=rowsize)
        f7.rowconfigure(3, weight=1, minsize=rowsize)
        f7.rowconfigure(4, weight=1, minsize=rowsize)
        f7.rowconfigure(5, weight=1, minsize=rowsize)
        f7.rowconfigure(6, weight=1, minsize=rowsize)
        f7.rowconfigure(7, weight=1, minsize=rowsize)
        f7.rowconfigure(8, weight=1, minsize=rowsize)
        f7.rowconfigure(9, weight=1, minsize=rowsize)
        

        label_select7 = ttk.Label(f7, text="Select looping motors: ")
        label_select7.grid(row=0, column=0, columnspan = 4, sticky = "w", pady = (0,0), padx = (5,0))

        self.state_th7= IntVar()
        self.state_th7.set(1)
        button_th7 = ttk.Checkbutton(f7, text="Theta", variable=self.state_th7)
        button_th7.grid(row=1, column=0, sticky="w", pady = (0,0), padx = (15,0))

        self.state_tth7 = IntVar()
        self.state_tth7.set(0)
        button_tth7 = ttk.Checkbutton(f7, text="2 Theta", variable=self.state_tth7)
        button_tth7.grid(row=1, column=1, sticky="w", pady = (0,0), padx = (15,0))
        
        self.state_temp7 = IntVar()
        self.state_temp7.set(0)
        button_temp7 = ttk.Checkbutton(f7, text="Temperature", variable=self.state_temp7)
        button_temp7.grid(row=1, column=2, sticky="w", pady = (0,0), padx = (15,0))

        self.state_chi7 = IntVar()
        self.state_chi7.set(0)
        button_chi7 = ttk.Checkbutton(f7, text="Chi/Psi", variable=self.state_chi7)
        button_chi7.grid(row=2, column=0, sticky="w", pady = (0,0), padx = (15,0))

        self.state_phi7 = IntVar()
        self.state_phi7.set(0)
        button_phi7 = ttk.Checkbutton(f7, text="Phi", variable=self.state_phi7)
        button_phi7.grid(row=2, column=1, sticky="w", pady = (0,0), padx = (15,0))
        
        self.state_x7 = IntVar()
        self.state_x7.set(0)
        button_x7 = ttk.Checkbutton(f7, text="X", variable=self.state_x7)
        button_x7.grid(row=3, column=0, sticky="w", pady = (0,0), padx = (15,0))
        
        self.state_y7 = IntVar()
        self.state_y7.set(0)
        button_y7 = ttk.Checkbutton(f7, text="Y", variable=self.state_y7)
        button_y7.grid(row=3, column=1, sticky="w", pady = (0,0), padx = (15,0))
        
        label_spacer7 = ttk.Label(f7, text="")
        label_spacer7.grid(row=4, column=0, columnspan=3, rowspan=2, sticky = "w", pady = (0,0), padx = (5,0))
       
        label_skip7 = ttk.Label(f7, text="Skip points at start/stop:")
        label_skip7.grid(row=6, column=0, columnspan=3, sticky = "w", pady = (0,0), padx = (5,0))
       
        label_skipstart7 = ttk.Label(f7, text="Primary scanning axis:")
        label_skipstart7.grid(row=7, column=0, columnspan=3, sticky = "w", pady = (0,0), padx = (15,0))
        self.entry_skipstart7=ttk.Entry(f7, width=7)
        self.entry_skipstart7.grid(row = 7, column=2, sticky = "", pady = (0,0))
        self.entry_skipstart7.insert(0,0)
        self.entry_skipstop7=ttk.Entry(f7, width = 7)
        self.entry_skipstop7.grid(row = 7, column=3, sticky = "w", pady = (0,0))
        self.entry_skipstop7.insert(0,0)
        
        label_spacer72 = ttk.Label(f7, text="")
        label_spacer72.grid(row=8, column=0, columnspan=3, sticky = "w", pady = (0,0), padx = (5,0))

        self.process7=ttk.Button(f7, text="Process Data", command=self.processCustom)
        self.process7.grid(row=9, column=0, columnspan = 4, sticky="ew", pady=(0,0), padx=(20,20))
        self.process7.focus()
        self.process7.bind('<Return>', self.processCustom)

    #****************************************
    #Function definitions
    #****************************************
    def about(self):
        messagebox.showinfo("About", "Dx Tools by A. Boulle.\nalexandre.boulle@unilim.fr\nhttps://aboulle.github.io/DxTools/")

    def warning(self):
        messagebox.showwarning("Warning", "Not yet implemented.")

    def data_warning(self):
        messagebox.showerror("Warning", "No data to process. \n Load data first.")
        
    def processing_warning(self):
        messagebox.showinfo("Warning", "Processing data, this may take some time.")
    
    def reading_warning(self):
        messagebox.showinfo("Warning", "Reading data, this may take some time.")
        
    def datatype_warning(self):
        messagebox.showerror("Error", "Not a valid data set.")
        
    def file_econding_error(self):
        messagebox.showerror("Error", "Invalid data file encoding.\nConvert file to UTF-8.")

    #def importText(self):
        #ftypes = [('Bruker files', '*.uxd *.brml'), ('All files', '*')]
        #filename = filedialog.askopenfilename(filetypes = ftypes)
        #if filename != '':
            #text = self.readFile(filename)
            #self.txt.insert(END, text)

    #def readFile(self, filename):
        #f = open(filename, "r")
        #text = f.read()
        #return text

    def importUXD(self):
        try:
            f=open("last_path", "r")
            init_dir=f.read()
            f.close()
        except:
            init_dir=os.getcwd()
        ftypes = [('Bruker uxd files', '*.uxd *.UXD')]
        filename = filedialog.askopenfilename(filetypes = ftypes, initialdir=init_dir)
        if filename != '':
            self.filepath = filename
            self.status.set("Reading data, please wait.")
            self.status.pack(side=BOTTOM, fill=X)
            self.parent.config(cursor="watch")
            self.parent.update()
            self.scan, self.line, self.wl = uxd_reader(filename)
            if self.scan == "encoding error":
                self.file_econding_error()
                pass
            self.parent.config(cursor="")
            self.status.set("Done.")
            self.export_path=self.filepath[:-4]
            self.flag_data=1
            f = open("last_path", "w")
            f.write(os.path.split(self.filepath)[0])
            f.close()
            self.raw_data = loadtxt("tmp")
            
    def importBRML(self):
        try:
            f=open("last_path", "r")
            init_dir=f.read()
            f.close()
        except:
            init_dir=os.getcwd()
        ftypes = [('Bruker uxd files', '*.brml *.BRML')]
        filename = filedialog.askopenfilename(filetypes = ftypes, initialdir=init_dir)
        if filename != '':
            self.filepath = filename
            self.status.set("Reading data, please wait.")
            self.status.pack(side=BOTTOM, fill=X)
            self.parent.config(cursor="watch")
            self.parent.update()
            self.scan, self.line, self.wl = brml_reader(filename)
            if self.scan == "implementation_warning":
                self.warning()
                pass
            self.parent.config(cursor="")
            self.status.set("Done.")
            self.export_path=self.filepath[:-5]
            self.flag_data=1
            f = open("last_path", "w")
            f.write(os.path.split(self.filepath)[0])
            f.close()
            self.raw_data = loadtxt("tmp")

    def processRSM(self, event = None):
        if self.flag_data == 1:
            self.status.set("Computing reciprocal space map, please wait.")
            self.status.pack(side=BOTTOM, fill=X)
            self.processing_warning()
            self.parent.config(cursor="watch")
            self.parent.update()
            status = generate_RSM(self.raw_data, self.export_path, self.scan, float(self.line), float(self.wl),
                     int(self.state_log1.get()), int(self.state_angmat1.get()), int(self.state_qmat1.get()),
                     int(self.state_xyz1.get()), float(self.entry_step1.get()), float(self.entry_skipstartp1.get()),
                     float(self.entry_skipstopp1.get()), float(self.entry_skipstarts1.get()),float(self.entry_skipstops1.get()))
            self.status.set("Done.")
            self.parent.config(cursor="")
            if status == 0:
                self.datatype_warning()
        else:
            self.data_warning()
            pass

    def processTemp(self, event = None):
        if self.flag_data == 1:
            self.status.set("Processing temperature data, please wait.")
            self.status.pack(side=BOTTOM, fill=X)
            #self.processing_warning()
            self.parent.config(cursor="watch")
            self.parent.update()
            status = generate_Temp(self.raw_data, self.export_path, float(self.line), int(self.state_indv2.get()),
                     int(self.state_mat2.get()), int(self.state_fit2.get()), float(self.entry_skipstart2.get()),
                     float(self.entry_skipstop2.get()), float(self.entry_skipstartT2.get()),float(self.entry_skipstopT2.get()),)
            self.status.set("Done.")
            self.parent.config(cursor="")
            if status == 0:
                self.datatype_warning()
        else:
            self.data_warning()
            pass
    
    def processX(self, event = None):
        if self.flag_data == 1:
            self.status.set("Processing X-scan data, please wait.")
            self.status.pack(side=BOTTOM, fill=X)
            #self.processing_warning()
            self.parent.config(cursor="watch")
            self.parent.update()
            status = generate_Xscan(self.raw_data, self.export_path, float(self.line), int(self.state_indv3.get()),
                     int(self.state_mat3.get()), int(self.state_fit3.get()), float(self.entry_skipstart3.get()),
                     float(self.entry_skipstop3.get()), float(self.entry_skipstartX3.get()), float(self.entry_skipstopX3.get()))
            self.status.set("Done.")
            self.parent.config(cursor="")
            if status == 0:
                self.datatype_warning()
        else:
            self.data_warning()
            pass

    def processStress(self, event = None):
        if self.flag_data == 1:
            self.status.set("Processing sin²psi data, please wait.")
            self.status.pack(side=BOTTOM, fill=X)
            #self.processing_warning()
            self.parent.config(cursor="watch")
            self.parent.update()
            status = generate_Stress(self.raw_data, self.export_path, float(self.line), float(self.wl), int(self.state_indv5.get()),
                     int(self.state_fit5.get()), float(self.entry_skipstart5.get()), float(self.entry_skipstop5.get()),
                     float(self.entry_skipstartpsi5.get()), float(self.entry_skipstoppsi5.get()))
            self.status.set("Done.")
            self.parent.config(cursor="")
            if status == 0:
                self.datatype_warning()
        else:
            self.data_warning()
            pass
    
    def processPole(self, event = None):
        if self.flag_data == 1:
            self.status.set("Computing pole figure, please wait.")
            self.status.pack(side=BOTTOM, fill=X)
            #self.processing_warning()
            self.parent.config(cursor="watch")
            self.parent.update()
            status = generate_Pole(self.raw_data, self.export_path, self.scan,
                    float(self.line), int(self.state_indv6.get()),
                    int(self.state_angmat6.get()), int(self.state_xyz6.get()),
                    float(self.entry_skipstartp6.get()), float(self.entry_skipstopp6.get()),
                    float(self.entry_skipstarts6.get()),float(self.entry_skipstops6.get()))
            self.status.set("Done.")
            self.parent.config(cursor="")
            if status == 0:
                self.datatype_warning()
        else:
            self.data_warning()
            pass
    
    def processCustom(self, event = None):
        if self.flag_data == 1:
            self.status.set("Processing data, please wait.")
            self.status.pack(side=BOTTOM, fill=X)
            #self.processing_warning()
            self.parent.config(cursor="watch")
            self.parent.update()
            status = generate_Custom(self.raw_data, self.export_path, float(self.line), int(self.state_th7.get()),
                     int(self.state_tth7.get()), int(self.state_chi7.get()), int(self.state_phi7.get()),
                     int(self.state_x7.get()), int(self.state_y7.get()), int(self.state_temp7.get()),
                     float(self.entry_skipstart7.get()), float(self.entry_skipstart7.get()))
            self.status.set("Done.")
            self.parent.config(cursor="")
            if status == 0:
                self.datatype_warning()
        else:
            self.data_warning()
            pass

    def on_closing(self):
        try:
            os.remove("tmp")
        except:
            pass
        sys.exit()
        self.quit()

    

def main():
    print("Welcome to DxTools")
    root = Tk()
    application = MyApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()