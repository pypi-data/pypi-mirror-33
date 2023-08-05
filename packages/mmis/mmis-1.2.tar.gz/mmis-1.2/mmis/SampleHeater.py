import wx
from wx.lib.pubsub import pub
import os
import time
#import serial
import spidev
#import serial.tools.list_ports
import matplotlib
matplotlib.use('wxAgg')
import matplotlib.dates as md
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import \
    FigureCanvasWxAgg as FigureCanvas, \
    NavigationToolbar2WxAgg as NavigationToolbar
import pandas as pd
import numpy as np
from wx.lib.masked import NumCtrl
import pylab
import math
import RPi.GPIO as GPIO
import mmis.Functions
#from .Functions import *
import mmis.DebugFunctions
#from .DebugFunctions import *
from datetime import datetime

class Settings(wx.Panel):
    
    def __init__(self, parent, Module, pubsub1, pubsub2):

        wx.Panel.__init__(self, parent = parent)
        
        #self.spi = spidev.SpiDev()
        #self.spi.open(0,0)
        #self.spi.max_speed_hz = 50000

        self.chipselect = Module[0]
        self.interruptpin = Module[1]

        self.B = []
        self.paused = True
        self.pubsubname = pubsub1
        self.pubsubalarm = pubsub2

        """ Creating a Timer """
         
        self.redraw_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_redraw_timer, self.redraw_timer) #Timer event occurs every few milliseconds that it was set 

        self.grid = wx.GridBagSizer(hgap=5, vgap=5)
        self.font1 = wx.Font(16, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Consolas')
        self.font2 = wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Consolas')
        
        self.lblname1 = wx.StaticText(self, label = "A :", pos = (40,30))
        self.lblname1.SetFont(self.font2)
        #self.SET_A = NumCtrl(self, id = -1, value = 0.25,integerWidth=6, fractionWidth = 3, min=0, max = 800, size=(80,40), pos = (70,25), limited = True, selectOnEntry = False, decimalChar = '.', groupChar = ',', groupDigits = True, name = "masked.number", useParensForNegatives = False)
        self.SET_A = wx.SpinCtrlDouble(self, size=(150,40), min =0, max = 800, inc = 0.1, value='0.25', pos = (70,25))
        self.SET_A.SetDigits(3)
        self.SET_A.SetBackgroundColour('white')

        self.lblname7 = wx.StaticText(self, label = "B :", pos = (230,30))
        self.lblname7.SetFont(self.font2)
        self.SET_B = wx.TextCtrl(self, size=(150,40), pos = (260,25), style = wx.TE_NO_VSCROLL|wx.TE_LEFT|wx.TE_READONLY)
        self.SET_B.SetBackgroundColour('grey')

        self.lblname2 = wx.StaticText(self, label = "T-Amb :", pos = (420,30))
        self.lblname2.SetFont(self.font2)
        #self.SET_Tamb = NumCtrl(self, id = -1, value = 20.0, integerWidth=6, fractionWidth = 3, min=-300, max = 800, size=(60,40), pos = (500,25), limited = True, selectOnEntry = False, decimalChar = '.', groupChar = ',', groupDigits = True, name = "masked.number", useParensForNegatives = False)
        self.SET_Tamb = wx.SpinCtrlDouble(self, size=(150,40), min =-300, max = 800, inc = 0.1, value='20.00', pos = (480,25))
        self.SET_Tamb.SetDigits(3)
        self.SET_Tamb.SetBackgroundColour('white')
        
        self.button1 = wx.Button(self, label="Start Calibration", pos=(650, 25), size = (140,40), id = -1)
        self.button1.SetFont(self.font2)
        self.Bind(wx.EVT_BUTTON, self.ON_CALIBRATE_B, self.button1)
        self.button1.Bind(wx.EVT_UPDATE_UI, self.on_update_pause_button)
        self.button1.SetForegroundColour('black')

        self.lblname3 = wx.StaticText(self, label = "T-Max :", pos = (40,140))
        self.lblname3.SetFont(self.font2)
        #self.SET_Tmax = NumCtrl(self, id = -1, value = 800.0, integerWidth=6, fractionWidth = 3, min=0, max = 800, size=(80,40), pos = (200,130), limited = True, selectOnEntry = False, decimalChar = '.', groupChar = ',', groupDigits = True, name = "masked.number", useParensForNegatives = False)
        self.SET_Tmax = wx.SpinCtrlDouble(self, size=(160,40), min = 0, max = 800, inc = 0.1, value='800.00', pos = (200,130))
        self.SET_Tmax.SetDigits(3)
        self.SET_Tmax.SetBackgroundColour('white')

        self.button3 = wx.Button(self, label="Set", pos=(380, 130), size = (100,40), id = -1)
        self.button3.SetFont(self.font2)
        self.Bind(wx.EVT_BUTTON, self.ON_SET_TMAX,self.button3)
        self.button3.SetForegroundColour('black')
        self.button3.SetBackgroundColour(wx.Colour(211,211,211))

        myserial = self.getserial()
        if myserial=='00000000e138f974':
            self.lblname4 = wx.StaticText(self, label = "Calibration :", pos = (40,85))
            self.lblname4.SetFont(self.font2)
            self.Mode_Selection = ['Open Circuit', 'Short Circuit', '200 Ohm', 'CAL_MDAC']
            self.Combo1 = wx.ComboBox(self, choices = self.Mode_Selection, pos = (200,80), size = (160,-1))
            
            self.button2 = wx.Button(self, label="Set", pos=(380, 75), size = (100,40), id = -1)
            self.button2.SetFont(self.font2)
            self.Bind(wx.EVT_BUTTON, self.ON_SET_MODE,self.button2)
            self.button2.SetForegroundColour('black')
            self.button2.SetBackgroundColour(wx.Colour(211,211,211))

        #self.lblname5 = wx.StaticText(self, label = "Module Name :", pos = (40,140))
        #self.lblname5.SetFont(self.font2)
        #self.Module_Name = wx.TextCtrl(self, size=(160,50), pos = (200,130), style = wx.TE_NO_VSCROLL|wx.TE_LEFT|wx.TE_READONLY)

        #self.lblname6 = wx.StaticText(self, label = "Version :", pos = (40,195))
        #self.lblname6.SetFont(self.font2)
        #self.Soft_Version = wx.TextCtrl(self, size=(160,40), pos = (200,185), style = wx.TE_NO_VSCROLL|wx.TE_LEFT|wx.TE_READONLY)

        #self.lblname6 = wx.StaticText(self, label = "Create Log File :", pos = (40,195))
        #self.lblname6.SetFont(self.font2)
        #self.File_name = wx.TextCtrl(self, size=(160,40), pos = (200,185), style = wx.TE_NO_VSCROLL|wx.TE_LEFT)
        
        #self.button4 = wx.Button(self, label="Get", pos=(380, 185), size = (100,40), id = -1)
        #self.button4.SetFont(self.font2)
        #self.Bind(wx.EVT_BUTTON, self.ON_VERSION_REQUEST,self.button4)
        #self.button4.SetForegroundColour('black')

        #self.button4 = wx.Button(self, label="Create", pos=(380, 185), size = (100,40), id = -1)
        #self.button4.SetFont(self.font2)
        #self.Bind(wx.EVT_BUTTON, self.ON_CREATE,self.button4)
        #self.button4.SetForegroundColour('black')
        
        print (myserial)
        self.button5 = wx.Button(self, label="Software Reset", pos=(40, 245), size = (200,40), id = -1)
        self.button5.SetFont(self.font2)
        self.Bind(wx.EVT_BUTTON, self.ON_SOFT_RESET,self.button5)
        self.button5.SetForegroundColour('black')
        self.button5.SetBackgroundColour(wx.Colour(211,211,211))

        self.button6 = wx.Button(self, label="Alarm Reset", pos=(290, 245), size = (200,40), id = -1)
        self.button6.SetFont(self.font2)
        self.Bind(wx.EVT_BUTTON, self.ON_ALARM_RESET,self.button6)
        self.button6.SetForegroundColour('black')
        self.button6.SetBackgroundColour(wx.Colour(211,211,211))

    def getserial(self):
      # Extract serial from cpuinfo file
      cpuserial = "0000000000000000"
      try:
        f = open('/proc/cpuinfo','r')
        for line in f:
          if line[0:6]=='Serial':
            cpuserial = line[10:26]
        f.close()
      except:
        cpuserial = "ERROR000000000"
     
      return cpuserial

    def ON_CALIBRATE_B(self, e):
        self.B.clear()
        self.paused = not self.paused
        self.A = self.SET_A.GetValue()
        self.Tamb = self.SET_Tamb.GetValue()
        print (self.A, self.Tamb)
        self.redraw_timer.Start(1000)

    def on_update_pause_button(self, e):
        if self.paused:
            label = "Start Calibration"
            color = "light green"
            self.redraw_timer.Stop()
        else:
            label = "Stop Calibration"
            color = "red"
    
        self.button1.SetLabel(label)
        self.button1.SetBackgroundColour(color)

    def on_redraw_timer(self, e):
        R = mmis.Functions.GETTransactions(0X07, self.chipselect, self.interruptpin)
        self.Alarm = R.Alarm
        pub.sendMessage(self.pubsubalarm, alarm = int(self.Alarm))
        Get_R = R.Float.Float[0]
        self.B.append((Get_R - (self.A*self.Tamb)))
        pub.sendMessage(self.pubsubname, value1 = self.A, value2 = self.B[len(self.B)-1]) # used Pubsub functionality to set data across different frames
        self.SET_B.SetValue(str(self.B[len(self.B)-1]))
        self.Stop_Calibration()
        

    def Stop_Calibration(self):
        if len(self.B)>4:
            delta_B = self.B[len(self.B)-1] - self.B[len(self.B)-5]
            if abs(delta_B)<0.1:
                print ("Calibration finished")
                self.paused = not self.paused
                self.button1.SetLabel("Start Calibration")
                self.button1.SetBackgroundColour("light green")
                self.redraw_timer.Stop()
            else:
                print ("Calibration still Going on ....")

        
    def ON_SET_TMAX(self, e):
        Tmax = self.SET_Tmax.GetValue()
        Rmax = str(self.A*Tmax + self.B[len(self.B)-1])
        set_tmax = mmis.Functions.SETTransactions(0X08, Rmax , self.chipselect, self.interruptpin)
        print (Rmax)
        
    def ON_SET_MODE(self, e):
        data = str(self.Combo1.GetSelection())
        if int(data) == 0:
            print ("Open Circuit Calibration Going on")
            mode = mmis.DebugFunctions.GETTransactions(0X12, self.chipselect, self.interruptpin, 4)
            print (mode.Received)
        elif int(data) == 1:
            print ("Short Circuit Calibration Going on")
            mode = mmis.DebugFunctions.GETTransactions(0X11, self.chipselect, self.interruptpin, 4)
            print (mode.Received)
        elif int(data) == 2:
            print ("200 Ohm Calibration Going on")
            mode = mmis.DebugFunctions.GETTransactions(0X10, self.chipselect, self.interruptpin, 4)
            print (mode.Received)
        elif int(data) == 3:
            print ("Calibration MDAC Going on")
            mode = mmis.DebugFunctions.GETTransactions(0X14, self.chipselect, self.interruptpin, 30)
            print (mode.Received)

    def ON_MODULE_NAME(self, e):
        name = mmis.Functions.GETTransactions(0X0C, self.chipselect, self.interruptpin)
        print (name.Received)
        self.Module_Name.SetValue(name.String) 

    def ON_VERSION_REQUEST(self, e):
        Version = mmis.Functions.GETTransactions(0X0D, self.chipselect, self.interruptpin)
        print (Version.Version)
        self.Soft_Version.SetValue(Version.Version)

    def ON_SOFT_RESET(self, e):
        Reset = mmis.Functions.GETTransactions(0X0E, self.chipselect, self.interruptpin)
        print (Reset.Received)
        print (Reset.Character)
    
    def ON_ALARM_RESET(self, e):
        Reset = mmis.Functions.GETTransactions(0X0F, self.chipselect, self.interruptpin)
        print (Reset.Character)
    
    def OnCloseWindow(self, e):
        self.Destroy()

class Main(wx.Panel):

    def __init__(self, parent, Module, pubsub1, pubsub2):
        
        wx.Panel.__init__(self, parent = parent)

        """ SPI Communication port open"""
        #self.spi = spidev.SpiDev()
        #self.spi.open(0,0)
        #self.max_speed_hz = 4000000
        self.chipselect = Module[0]
        self.interruptpin = Module[1]

        pub.subscribe(self.OnBvalue, pubsub1)
        self.pubsub_logdata = pubsub2
        
        """ Initilize the lists to store the temperature data """
        self.data = []
        self.paused = True   # At start up data generation event is paused until user starts it
        self.BvalueSet = False
        
        """ Creating a Timer for updating the Frame rate of the real time graph displayed"""
        self.redraw_graph_timer = wx.Timer(self, id = 2000)      # this timer controls the frame rate of the graph display
        self.Bind(wx.EVT_TIMER, self.on_redraw_graph_timer, self.redraw_graph_timer)  

        self.get_data_timer = wx.Timer(self, id = 2001)          # this timer controls the sampling rate of the data
        self.Bind(wx.EVT_TIMER, self.on_get_data_timer, self.get_data_timer)

        self.get_read_timer = wx.Timer(self, id = 2002)          # this timer controls the sampling rate of the data
        self.Bind(wx.EVT_TIMER, self.on_get_read_timer, self.get_read_timer)
        self.get_read_timer.Start(200)
        
        """ Initializing the graph plot to display the temperatures"""
        self.init_plot()
        self.canvas = FigureCanvas(self, -1, self.fig)
        self.Xticks = 50

        """GRID and Font created"""
        self.grid = wx.GridBagSizer(hgap=5, vgap=5)
        self.font1 = wx.Font(14, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Consolas')
        self.font2 = wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Consolas')

        """Create Buttons and other and Bind their events"""

        """# Increase button - Temperature control
        self.button1 = wx.Button(self, label = '+', size = (40,40), id=1)
        self.button1.SetFont(self.font1)
        self.button1.Bind(wx.EVT_BUTTON, self.Increase)
        self.button1.SetForegroundColour('black')

        # Decrease button - Temperature control
        self.button2 = wx.Button(self, label = '-', size = (40,40), id=2)
        self.button2.SetFont(self.font1)
        self.button2.Bind(wx.EVT_BUTTON, self.Decrease)
        self.button2.SetForegroundColour('black')"""

        # Save Button - To save the graph in PNG format
        self.button3 = wx.Button(self, label = 'Save Graph', size = (120,40), id=3)
        self.button3.SetFont(self.font1)
        self.button3.Bind(wx.EVT_BUTTON, self.OnSave)
        self.button3.SetForegroundColour('black')
        self.button3.SetBackgroundColour('light green')

        # Stop/Start button - Data Acquisition
        self.button5 = wx.Button(self, label = 'Stop', size = (120, 40), id =12)
        self.button5.SetFont(self.font1)
        self.button5.Bind(wx.EVT_BUTTON, self.on_pause_button)     # this event changes the state of self.paused
        self.button5.Bind(wx.EVT_UPDATE_UI, self.on_update_pause_button) # this event updates buttons state between stop and start
        self.button5.SetForegroundColour('black')
        self.button5.SetBackgroundColour('Red')

        # Check box - to show/delete x labels
        self.cb_xlab = wx.CheckBox(self, -1, 
            "Show X label",
            style=wx.ALIGN_RIGHT)
        self.Bind(wx.EVT_CHECKBOX, self.on_cb_xlab, self.cb_xlab)        
        self.cb_xlab.SetValue(True)

        # Check box - to Show/delete the grid
        self.cb_grid = wx.CheckBox(self, -1, 
            "Show Grid",
            style=wx.ALIGN_RIGHT)
        self.Bind(wx.EVT_CHECKBOX, self.on_cb_grid, self.cb_grid)
        self.cb_grid.SetValue(True)

        # Static text and text control box - to display the current value of temperature
        self.lblname2 = wx.StaticText(self, label = "Temperature")
        self.grid.Add(self.lblname2, pos = (0,0))
        self.lblname2.SetFont(self.font2)
        self.two = wx.TextCtrl(self, id = 5, size=(135,40), style = wx.TE_READONLY)
        self.two.SetBackgroundColour('grey')
        self.two.SetFont(self.font1)
        self.grid.Add(self.two, pos=(0,1))

        # Static text and num control box -  to set the value of temperature
        self.button6 = wx.Button(self, label = 'Set Value', size = (100,50), id=5)
        self.button6.SetFont(self.font2)
        self.button6.Bind(wx.EVT_BUTTON, self.SetResistance)
        self.button6.SetBackgroundColour(wx.Colour(211,211,211))
        #self.one = NumCtrl(self, id = 4, value = 80.0,integerWidth=3, fractionWidth = 3, max = 800, size=(80,40), style = wx.TE_PROCESS_ENTER|wx.TE_PROCESS_TAB)
        self.one = wx.SpinCtrlDouble(self, size=(150,35), min =-300, max = 800, inc = 0.1, value='80.00')
        self.one.SetDigits(3)
        self.one.SetBackgroundColour('white')
        #self.grid.Add(self.one, pos=(1,1))

        # Static text and text control box - set the value to display the number of values on X -axis
        self.lblname3 = wx.StaticText(self, label = "X-Axis Length")
        self.grid.Add(self.lblname3, pos = (1,0))
        self.three = wx.TextCtrl(self, id = 6, size = (120,40), style = wx.TE_PROCESS_ENTER)
        self.three.Bind(wx.EVT_TEXT_ENTER, self.OnSetXLabelLength)
        self.three.SetBackgroundColour('white')
        self.three.SetFont(self.font1)
        self.grid.Add(self.three, pos=(1,1))

        # Set all the buttons, check boxes and text controls in a BOX
        self.hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox1.Add(self.button5, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox1.AddSpacer(20)
        self.hbox1.Add(self.button3, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)

        self.hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox2.Add(self.one, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        #self.hbox2.Add(self.button1, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox2.AddSpacer(10)
        self.hbox2.Add(self.button6, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)

        #self.hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        #self.hbox3.Add(self.button2, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        #self.hbox3.AddSpacer(40)
        #self.hbox3.Add(self.one, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)

        self.hbox4 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox4.Add(self.lblname2, border = 5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox4.AddSpacer(20)
        self.hbox4.Add(self.two, border = 5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)

        self.hbox5 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox5.Add(self.cb_xlab, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox5.Add(self.cb_grid, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)

        self.hbox6 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox6.Add(self.lblname3, border = 5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox6.AddSpacer(15)
        self.hbox6.Add(self.three, border = 5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        
        self.vbox = wx.BoxSizer(wx.VERTICAL)      
        self.vbox.Add(self.hbox1, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        self.vbox.Add(self.hbox2, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        #self.vbox.Add(self.hbox3, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        self.vbox.Add(self.hbox4, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        self.vbox.Add(self.hbox5, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        self.vbox.Add(self.hbox6, 0, flag=wx.ALIGN_LEFT | wx.TOP)

        self.hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox.Add(self.canvas, 3.0, flag=wx.LEFT | wx.TOP)  
        self.hbox.Add(self.vbox, 1.99, flag=wx.LEFT | wx.TOP)  
        
        self.SetSizer(self.hbox)
        self.hbox.Fit(self)

    def OnBvalue(self, value1, value2):
        self.BvalueSet = True
        self.A = value1
        self.B = value2
        print (self.A, self.B)
        self.Refresh()
    
    def Temperature_Acquisition(self):
        Temp = np.zeros(4)
        Resistance = mmis.Functions.GETTransactions(0X07, self.chipselect, self.interruptpin)
        Resistance_Data =  Resistance.Float.Float[0]
        self.Alarm = Resistance.Alarm
        Temperature_Data = ((Resistance_Data-self.B)/self.A)
        Voltage = mmis.Functions.GETTransactions(0X05, self.chipselect, self.interruptpin)
        Voltage_Data =  (Voltage.Float.Float[0]*5000.0)/(3.0*math.pow(2,24)) #in Volts
        Current = mmis.Functions.GETTransactions(0X06, self.chipselect, self.interruptpin)
        Current_Data =  (Current.Float.Float[0]*5000.0)/(3000*math.pow(2,24)) #in mA
        Temp[0] = Temperature_Data
        Temp[1] = Voltage_Data
        Temp[2] = Current_Data
        Temp[3] = Resistance_Data
        pub.sendMessage(self.pubsub_logdata, data = Temp, alarm = self.Alarm)
        return Temp

    def init_plot(self):

        self.dpi = 60
        self.fig = Figure((5.0, 5.1), dpi = self.dpi)

        self.axes = self.fig.add_subplot(111)
        self.axes.set_facecolor('black')
        self.axes.set_title('Temperature acquisition', size = 15)
        self.axes.set_xlabel('Samples', size = 12)
        self.axes.set_ylabel('Ambient Temperature (C)', size = 15)

        pylab.setp(self.axes.get_xticklabels(), fontsize=12)
        pylab.setp(self.axes.get_yticklabels(), fontsize=12)
        
        self.plot_data = self.axes.plot(
            self.data,
            linewidth=1,
            color=(1,1,0),
            )[0]

    def draw_plot(self):
        """ Redraws the plot
        """
        # when xmin is on auto, it "follows" xmax to produce a 
        # sliding window effect. therefore, xmin is assigned after
        # xmax.

        xmax = len(self.data) if len(self.data) > 50 else 50           
        xmin = xmax - self.Xticks

        # for ymin and ymax, find the minimal and maximal values
        # in the data set and add a mininal margin.
        # 
        # note that it's easy to change this scheme to the 
        # minimal/maximal value in the current display, and not
        # the whole data set.
        # 
        ymin = round(min(self.data[(-self.Xticks):]), 0) - 1
        ymax = round(max(self.data[(-self.Xticks):]), 0) + 1

        self.axes.set_xbound(lower=xmin, upper=xmax)
        self.axes.set_ybound(lower=ymin, upper=ymax)

        # Using setp here is convenient, because get_xticklabels
        # returns a list over which one needs to explicitly 
        # iterate, and setp already handles this.
        #
        if self.cb_grid.IsChecked():
            self.axes.grid(True, color='gray')
        else:
            self.axes.grid(False)
        
        pylab.setp(self.axes.get_xticklabels(), 
            visible=self.cb_xlab.IsChecked())
        
        self.plot_data.set_xdata(np.arange(len(self.data)))
        #self.plot_data.set_xdata(np.array(self.time))
        self.plot_data.set_ydata(np.array(self.data))
        #self.two.SetValue(str(self.x[0]))
        self.canvas.draw()
        
    def OnSetXLabelLength(self, e):
        Xtks = self.three.GetValue()
        self.Xticks = int(Xtks.encode())

    def on_cb_grid(self, event):
        self.draw_plot()

    def on_cb_xlab(self, event):
        self.draw_plot()

    def on_pause_button(self, e):
        self.paused = not self.paused
        
        if self.paused:
            mmis.Functions.GETTransactions(0X02, self.chipselect, self.interruptpin)
        else:
            mmis.Functions.GETTransactions(0X01, self.chipselect, self.interruptpin)
            self.redraw_graph_timer.Start(1000)
            self.get_data_timer.Start(200)
            

    def on_update_pause_button(self, e):
        if self.paused:
            label = "Start"
            color = "light green"
            self.redraw_graph_timer.Stop()
            self.get_data_timer.Stop()
            
            
        else:
            label = "Stop"
            color = "red"
    
        self.button5.SetLabel(label)
        self.button5.SetBackgroundColour(color)

    def on_redraw_graph_timer(self, e):
        self.draw_plot()

    def on_get_data_timer(self, e):
        if not self.paused:
            if len(self.data)<2100:
                #self.x = self.Temperature_Acquisition()
                self.data.append(self.x[0])
            else:
                del self.data[0]
                #self.x = self.Temperature_Acquisition()
                self.data.append(self.x[0])

    def on_get_read_timer(self, e):
        if self.BvalueSet == True:
            self.x = self.Temperature_Acquisition()
            self.two.SetValue(str(self.x[0])[:6])
        

    def SetResistance(self, e):
        temp = self.one.GetValue()
        print (temp)
        Rset = str(temp*self.A + self.B)
        set_rset = mmis.Functions.SETTransactions(0X03, Rset , self.chipselect, self.interruptpin)
        
    
    def Increase(self,e):
        self.pos = self.one.GetInsertionPoint()
        if self.pos == 4:
            self.temp = self.one.GetValue()
            self.temp = self.temp + 1.0
            self.one.SetValue(self.temp)
        elif self.pos == 3:
            self.temp = self.one.GetValue()
            self.temp = self.temp + 10.0
            self.one.SetValue(self.temp)
        elif self.pos == 2:
            self.temp = self.one.GetValue()
            self.temp = self.temp + 100.0
            self.one.SetValue(self.temp)
        elif self.pos == 6:
            self.temp = self.one.GetValue()
            self.temp = self.temp + 0.1
            self.one.SetValue(self.temp)
        elif self.pos == 7:
            self.temp = self.one.GetValue()
            self.temp = self.temp + 0.01
            self.one.SetValue(self.temp)
        elif self.pos == 8:
            self.temp = self.one.GetValue()
            self.temp = self.temp + 0.001
            self.one.SetValue(self.temp)
        else:
            print ('out of range')
        self.one.SetInsertionPoint(self.pos)
        
        return self.pos
        
    def Decrease(self,e):
        
        self.pos = self.one.GetInsertionPoint()
        if self.pos == 4:
            self.temp = self.one.GetValue()
            self.temp = self.temp - 1.0
            self.one.SetValue(self.temp)
        elif self.pos == 3:
            self.temp = self.one.GetValue()
            self.temp = self.temp - 10.0
            self.one.SetValue(self.temp)
        elif self.pos == 2:
            self.temp = self.one.GetValue()
            self.temp = self.temp - 100.0
            self.one.SetValue(self.temp)
        elif self.pos == 6:
            self.temp = self.one.GetValue()
            self.temp = self.temp - 0.1
            self.one.SetValue(self.temp)
        elif self.pos == 7:
            self.temp = self.one.GetValue()
            self.temp = self.temp - 0.01
            self.one.SetValue(self.temp)
        elif self.pos == 8:
            self.temp = self.one.GetValue()
            self.temp = self.temp - 0.001
            self.one.SetValue(self.temp)
        else:
            print ('out of range')

        return self.pos

    def OnSave(self,e):
        file_choices = "PNG (*.png)|*.png"
        dlg = wx.FileDialog(
            self,
            message = "Save plot as...",
            defaultDir=os.getcwd(),
            defaultFile="plot.png",
            wildcard=file_choices,
            style=wx.FD_SAVE)

        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.canvas.print_figure(path, dpi = 200)
        
    def OnClose(self):
        self.Destroy()
