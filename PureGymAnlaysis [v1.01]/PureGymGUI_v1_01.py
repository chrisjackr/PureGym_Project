# ============================================================================================================================================================================================================================================================== #
# --------------------------------------------------------------------------------------------------------------- PureGymGUI_v1_01.py -------------------------------------------------------------------------------------------------------------------------- #
# ============================================================================================================================================================================================================================================================== #

#GUI_IMPORT
from PyQt5.QtWidgets import *
#QWidget, QGridLayout, QPushButton, QSizePolicy, QApplication
from PyQt5.uic import loadUi
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtCore import *

#RANDOM_IMPORT
from PureGymFunctions import num2time, time2num
import sys
import numpy as np
from numpy import linspace
import random
import math
from math import cos,sin,pi
import time
import datetime

#PLOT_IMPORT
from matplotlib import pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_qt5agg import (NavigationToolbar2QT as NavigationToolbar)
from matplotlib.backend_tools import ToolToggleBase
from matplotlib.ticker import (AutoMinorLocator, AutoLocator, LinearLocator, MaxNLocator, FixedLocator,FormatStrFormatter,AutoMinorLocator)
from matplotlib.widgets import Cursor

#DATABASE_IMPORT
#from openpyxl import Workbook, load_workbook
import sqlite3

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- #






# -----------------------------------------------------------------------------------------------------------------TIME_SERIES--------------------------------------------------------------------------------------------------------------------------------- #
time_vec = []                                                                                                            # Creates a 1440 length vector with datetime entries between 00:00 and 23:59. Notes that the Year Day and Month are set to 01/01/2020.
for i in range(1440):                                                                                                    # This needs to be specified when plotting graphs, even though only HH:MM is shown on the x-axis
    tdelta = datetime.timedelta(minutes=i)
    time_vec.append(datetime.datetime(2020,1,1,0,0,0,0)+tdelta)

x_label = []                                                                                                             # x_list contains a list with the 24 hours in datetime format.
x_list = []                                                                                                              # x_label contains a list with the 24 hour labels: [00:00, 01:00, 02:00, ... , 23:00]
for i in range(24):
    x_list.append(datetime.datetime(2020, 1, 1, i, 0, 0, 0))
    M = datetime.datetime(2020, 1, 1, i, 0, 0, 0).strftime('%M')
    H = datetime.datetime(2020, 1, 1, i, 0, 0, 0).strftime('%H')
    x_label.append(str(H+':'+M))


x_list.append(datetime.datetime(2020,1,2,0,0,0,0))                                                                       # Adds midnight to list.
x_label.append('24:00')                                                                                                  # Adds 24:00 to list.
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- #


# ----------------------------------------------------------------------------------------------------------------LEGEND_PICKING------------------------------------------------------------------------------------------------------------------------------- #
def on_pick(event):                                                                                                      # Find the original line corresponding to the legend proxy line that was clicked and toggle its visibility.
    if window.rawdata_checkBox.isChecked():
        try:
            legline_raw = event.artist                                                                                       # Set legline to be the legend proxy line clicked.
            origline_raw = lined_raw[legline_raw]                                                                            # Set origline to be the proxy line's corresponding line on the graph.
            visible_raw = not origline_raw.get_visible()                                                                     # Set the visible variable to be the opposite of the line on the graph's current visibility.
            origline_raw.set_visible(visible_raw)                                                                            # Change the visibility of the line on the graph.
            alpha_raw[legline_raw] = visible_raw                                                                             # Set the alpha record of the proxy line to the new visibility of the line on the graph.
            legline_raw.set_alpha(1.0 if visible_raw else 0.2)                                                               # Change the alpha on the legend proxy line to correspond with the line on the graph.
        except:
            pass
    if window.smootheddata_checkBox.isChecked():
        try:
            legline_smooth = event.artist
            origline_smooth = lined_smooth[legline_smooth]
            visible_smooth = not origline_smooth.get_visible()
            origline_smooth.set_visible(visible_smooth)
            alpha_smooth[legline_smooth] = visible_smooth
            legline_smooth.set_alpha(1.0 if visible_smooth else 0.2)
        except:
            pass

    window.MplWidget.canvas.draw()
    window.update_bg()
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#




class MatplotlibWidget(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)
        loadUi("PureGymGUI_v1_01.ui", self)                                                                              # Load GUI file.
        QMainWindow.showMaximized(self)                                                                                  # Fit window to full screen.

        self.setWindowTitle("PureGym Analytics GUI [v1.01]")
        self.label_title.setText('PureGym Analysis   [v1.01]')
        self.addToolBar(NavigationToolbar(self.MplWidget.canvas, self))                                                  # Add matplotlib graph toolbar to top of screen.
        self.showMaximized()
        #SET_WINDOW_SIZE_MANUALLY
        #self.line.setGeometry(QtCore.QRect(350, 10, 20, 1000))                                                           # Set size of userface within window?
        #self.MplWidget.setGeometry(QtCore.QRect(370, 10, 1530, 950))  #(xpos,ypos,xwidth,yheight)                        # Set size of userface within window?
        self.MplWidget.canvas.mpl_connect('pick_event', on_pick)
        self.cursor = Cursor(self.MplWidget.canvas.axes, alpha=0.2, color = 'grey', vertOn=True, horizOn=True, linewidth = 1, useblit=True)
        self.cursor_toggle = True

    #DATA_TYPES_BOX
        self.rawdata_checkBox.stateChanged.connect(self.raw_visiblility)
        self.smootheddata_checkBox.stateChanged.connect(self.smooth_visibility)
        self.rawdata_checkBox.stateChanged.connect(self.legend_visibility)
        self.smootheddata_checkBox.stateChanged.connect(self.legend_visibility)
        self.meandata_checkBox.stateChanged.connect(self.mean_visibility)

    #OPTIONS_BOX
        self.legend_checkBox.stateChanged.connect(self.legend_visibility)
        self.gridlines_checkBox.stateChanged.connect(self.gridlines_visibility)
        self.analysis_checkBox.stateChanged.connect(self.analine_visibility)

    #ANNOTATIONS_BOX
        #TIME
        self.time_checkBox.stateChanged.connect(self.time_visibility)
        self.time_checkBox.stateChanged.connect(self.update_bg)
        self.time_horizontalSlider.setRange(0,1439)
        self.time_horizontalSlider.setFocusPolicy(Qt.NoFocus)
        self.time_horizontalSlider.sliderPressed.connect(self.time_press)
        self.time_horizontalSlider.valueChanged.connect(self.time_slider)
        self.specifictime_timeEdit.timeChanged.connect(self.time_slider_update)
        self.time_horizontalSlider.sliderReleased.connect(self.time_release)
        #PEOPLE
        self.people_spinBox.setValue(0)
        self.people_spinBox.setRange(0,124)
        self.people_checkBox.stateChanged.connect(self.people_visibility)
        self.people_checkBox.stateChanged.connect(self.update_bg)
        self.people_horizontalSlider.setRange(0,124)
        self.people_horizontalSlider.setFocusPolicy(Qt.NoFocus)
        self.people_horizontalSlider.sliderPressed.connect(self.people_press)
        self.people_horizontalSlider.valueChanged.connect(self.people_slider)
        self.people_spinBox.valueChanged.connect(self.people_slider_update)
        self.people_horizontalSlider.sliderReleased.connect(self.people_release)


    #TAB1
        #------Tab1 Setup--------------------------------------------------------------
        # Set starting date and weekday label to today.
        self.t1_specificday_dateEdit.setDateTime(QDateTime(QDateTime.currentDateTime()))                                # Sets date_edit to today's date for initial setup.
        input = self.t1_specificday_dateEdit.dateTime().toPyDateTime().date()
        weekday = input.strftime('%a')
        self.t1_specificweekday_label.setText(weekday)                                                                  # Sets label to today's weekday for initial setup.

        self.t1_update_pushButton.setEnabled(False)                                                                     # Disables update pushButton.
        #-------------------------------------------------------------------------------

        #DATE_EDIT
        self.t1_specificday_dateEdit.dateChanged.connect(self.t1_date_label_change)
        #TODAY
        self.t1_today_pushButton.clicked.connect(self.today)
        #YESTERDAY
        self.t1_yesterday_pushButton.clicked.connect(self.yesterday)
        #NOTES
        self.plainTextEdit.modificationChanged.connect(self.notes_enable)
        self.t1_save_pushButton.clicked.connect(self.notes_save)
        #UPDATE_TAB1
        self.t1_update_pushButton.clicked.connect(lambda: self.t1_update_pushButton.setEnabled(False))
        self.t1_update_pushButton.clicked.connect(lambda: self.t2_update_pushButton.setEnabled(True))
        self.t1_update_pushButton.clicked.connect(self.update_specific_date)

        self.t1_specificday_dateEdit.dateChanged.connect(lambda: self.t1_update_pushButton.setEnabled(True))
        self.t1_today_pushButton.clicked.connect(lambda: self.t1_update_pushButton.setEnabled(True))
        self.t1_yesterday_pushButton.clicked.connect(lambda: self.t1_update_pushButton.setEnabled(True))

        self.time_press_toggle = False
        self.start_press_toggle = False
        self.end_press_toggle = False
        self.people_press_toggle = False




    #TAB2
        #------Tab2 Setup----------------------------------------------------------
        # Set start and end dates and weekday labels to today.
        self.t2_start_dateEdit.setDateTime(QDateTime(QDateTime.currentDateTime()))
        input = self.t2_start_dateEdit.dateTime().toPyDateTime().date()
        weekday = input.strftime('%a')
        self.t2_selectweekdaystart_label.setText(weekday)

        self.t2_end_dateEdit.setDateTime(QDateTime(QDateTime.currentDateTime()))
        input = self.t2_end_dateEdit.dateTime().toPyDateTime().date()
        weekday = input.strftime('%a')
        self.t2_selectweekdayend_label.setText(weekday)

        self.t2_update_pushButton.setEnabled(False)
        #---------------------------------------------------------------------------

        #ONE_WEEK
        self.t2_oneweek_pushButton.clicked.connect(self.one_week)
        #ONE_MONTH
        self.t2_onemonth_pushButton.clicked.connect(self.one_month)
        #PAST_WEEK
        self.t2_pastweek_pushButton.clicked.connect(self.past_week)
        #PAST_MONTH
        self.t2_pastmonth_pushButton.clicked.connect(self.past_month)

        #UPDATE_TAB2
        self.t2_start_dateEdit.dateChanged.connect(self.t2_start_date_label_change)
        self.t2_end_dateEdit.dateChanged.connect(self.t2_end_date_label_change)
        self.t2_update_pushButton.setEnabled(False)
        self.t2_update_pushButton.clicked.connect(lambda: self.t2_update_pushButton.setEnabled(False))
        self.t2_update_pushButton.clicked.connect(lambda: self.t1_update_pushButton.setEnabled(True))

        self.t2_start_dateEdit.dateChanged.connect(lambda: self.t2_update_pushButton.setEnabled(True))
        self.t2_end_dateEdit.dateChanged.connect(lambda: self.t2_update_pushButton.setEnabled(True))
        self.t2_monday_checkBox.stateChanged.connect(lambda : self.weekday_toggle(self.t2_monday_checkBox))
        self.t2_tuesday_checkBox.stateChanged.connect(lambda : self.weekday_toggle(self.t2_tuesday_checkBox))
        self.t2_wednesday_checkBox.stateChanged.connect(lambda : self.weekday_toggle(self.t2_wednesday_checkBox))
        self.t2_thursday_checkBox.stateChanged.connect(lambda : self.weekday_toggle(self.t2_thursday_checkBox))
        self.t2_friday_checkBox.stateChanged.connect(lambda : self.weekday_toggle(self.t2_friday_checkBox))
        self.t2_saturday_checkBox.stateChanged.connect(lambda : self.weekday_toggle(self.t2_saturday_checkBox))
        self.t2_sunday_checkBox.stateChanged.connect(lambda : self.weekday_toggle(self.t2_sunday_checkBox))

        self.t2_selectall_pushButton.clicked.connect(lambda: self.days_selection(True))
        self.t2_deselectall_pushButton.clicked.connect(lambda: self.days_selection(False))

        self.t2_update_pushButton.clicked.connect(self.update_range_dates)




    #TAB3
        #No functions yet



    #ANALYSIS_BOX
        self.analysis_checkBox.stateChanged.connect(self.analine_visibility)
        self.analysis_checkBox.stateChanged.connect(self.update_bg)
        #START WINDOW
        self.start_timeEdit.setDateTime(datetime.datetime(2020,1,1,0,0,0,0))
        self.start_horizontalSlider.setRange(0,1439)
        self.start_horizontalSlider.setValue(0)
        self.start_horizontalSlider.setFocusPolicy(Qt.NoFocus)
        self.start_horizontalSlider.sliderPressed.connect(self.start_press)
        self.start_horizontalSlider.valueChanged.connect(self.start_slider)
        self.start_timeEdit.timeChanged.connect(self.start_slider_update)
        self.start_horizontalSlider.sliderReleased.connect(self.start_release)
        #END WINDOW
        self.end_timeEdit.setDateTime(datetime.datetime(2020,1,1,23,59,0,0))
        self.end_horizontalSlider.setRange(0,1439)
        self.end_horizontalSlider.setValue(1439)
        self.end_horizontalSlider.setFocusPolicy(Qt.NoFocus)
        self.end_horizontalSlider.sliderPressed.connect(self.end_press)
        self.end_horizontalSlider.valueChanged.connect(self.end_slider)
        self.end_timeEdit.timeChanged.connect(self.end_slider_update)
        self.end_horizontalSlider.sliderReleased.connect(self.end_release)

        #BUTTONS
        self.fullday_pushButton.clicked.connect(self.fullday)
        self.day_pushButton.clicked.connect(self.day)
        self.morning_pushButton.clicked.connect(self.morning)
        self.evening_pushButton.clicked.connect(self.evening)

        #UPDATE ANALYSIS
        self.update_analysis_pushButton.clicked.connect(self.update_analysis)
        self.test_pushButton.clicked.connect(self.test)

    #Timer for continuous plotting cur_labels.......
        # self.timer = QtCore.QTimer()
        # self.timer.setInterval(1)
        # self.timer.timeout.connect(self.cur_labels)
        # self.timer.start()

    def cur_labels(self):
        props = dict(boxstyle = 'square', facecolor= 'white', edgecolor = 'white')
        cur_min = 5
        cur_max = 6
        cur_mean = 7
        self.MplWidget.canvas.axes.text(0.02, 1.01, '{}:{}:{}'.format(cur_min,cur_mean,cur_max),transform=self.MplWidget.canvas.axes.transAxes, fontsize=10, color = 'grey',  verticalalignment='bottom', bbox=props)

    def days_selection(self,bool):
        self.t2_monday_checkBox.setChecked(bool)
        self.t2_tuesday_checkBox.setChecked(bool)
        self.t2_wednesday_checkBox.setChecked(bool)
        self.t2_thursday_checkBox.setChecked(bool)
        self.t2_friday_checkBox.setChecked(bool)
        self.t2_saturday_checkBox.setChecked(bool)
        self.t2_sunday_checkBox.setChecked(bool)

    def weekday_toggle(self,checkBox):
        self.t2_update_pushButton.setEnabled(True)
        weekday_checkBox_dict = {self.t2_monday_checkBox:'Mon',self.t2_tuesday_checkBox:'Tue',self.t2_wednesday_checkBox:'Wed',self.t2_thursday_checkBox:'Thu',self.t2_friday_checkBox:'Fri',self.t2_saturday_checkBox:'Sat',self.t2_sunday_checkBox:'Sun'}
        if True:
        #for checkBox in list(weekday_checkBox_dict.keys()):
            if True:
                try:
                    for legline_raw in self.leg.get_lines():
                        if legline_raw.get_label()[0:3] == weekday_checkBox_dict[checkBox]:
                            origline_raw = lined_raw[legline_raw]
                            visible_raw = checkBox.isChecked()
                            # origline_raw.set_visible(visible_raw)
                            # alpha_raw[legline_raw] = visible_raw
                            legline_raw.set_alpha(1.0 if visible_raw else 0.2)
                            alpha_raw[legline_raw] = visible_raw
                            if self.rawdata_checkBox.isChecked():
                                origline_raw.set_visible(visible_raw)
                except:
                    pass
                try:
                    for legline_smooth in self.leg2.get_lines():
                        if legline_smooth.get_label()[0:3] == weekday_checkBox_dict[checkBox]:
                            origline_smooth = lined_smooth[legline_smooth]
                            visible_smooth = checkBox.isChecked()
                            # origline_smooth.set_visible(visible_smooth)
                            # alpha_raw[legline_smooth] = visible_smooth
                            legline_smooth.set_alpha(1.0 if visible_smooth else 0.2)
                            alpha_raw[legline_smooth] = visible_smooth
                            if self.smootheddata_checkBox.isChecked():
                                origline_smooth.set_visible(visible_smooth)
                except:
                    pass
        window.MplWidget.canvas.draw()
        window.update_bg()

    def legend_visibility(self):
        if self.legend_checkBox.isChecked():
            if self.rawdata_checkBox.isChecked() and self.smootheddata_checkBox.isChecked():
                self.leg.set_visible(True)
                self.leg2.set_visible(True)
            elif self.smootheddata_checkBox.isChecked():
                self.leg.set_visible(False)
                self.leg2.set_visible(True)
            elif self.rawdata_checkBox.isChecked():
                self.leg.set_visible(True)
                self.leg2.set_visible(False)
            else:
                self.leg.set_visible(False)
                self.leg2.set_visible(False)
        else:
            self.leg.set_visible(False)
            self.leg2.set_visible(False)

        self.MplWidget.canvas.draw()
        self.update_bg()

    def gridlines_visibility(self):
        if self.gridlines_checkBox.isChecked():
            self.MplWidget.canvas.axes.grid(True)
        else:
            self.MplWidget.canvas.axes.grid(False)
        self.MplWidget.canvas.draw()
        self.update_bg()

    def raw_visiblility(self):
        if self.rawdata_checkBox.isChecked():
            for legline_raw in self.leg.get_lines():
                if alpha_raw[legline_raw]:
                    origline_raw = lined_raw[legline_raw]
                    origline_raw.set_visible(True)
                    legline_raw.set_alpha(1.0)
                else:
                    legline_raw.set_alpha(0.2)
        else:
            for origline_raw in list(lined_raw.values()):
                origline_raw.set_visible(False)
            for legline_raw in self.leg.get_lines():
                legline_raw.set_alpha(0.2)

        self.MplWidget.canvas.draw()
        self.update_bg()

    def smooth_visibility(self):
        if self.smootheddata_checkBox.isChecked():
            for legline_smooth in self.leg2.get_lines():
                if alpha_smooth[legline_smooth]:
                    origline_smooth = lined_smooth[legline_smooth]
                    origline_smooth.set_visible(True)
                    legline_smooth.set_alpha(1.0)
                else:
                    legline_smooth.set_alpha(0.2)
        else:
            for origline_smooth in list(lined_smooth.values()):
                origline_smooth.set_visible(False)
            for legline_smooth in self.leg2.get_lines():
                legline_smooth.set_alpha(0.2)
        self.MplWidget.canvas.draw()
        self.update_bg()

    def mean_visibility(self):
        if self.meandata_checkBox.isChecked():
            self.line_mean.set_visible(True)
        else:
            self.line_mean.set_visible(False)
        self.MplWidget.canvas.draw()
        self.update_bg()

    def analine_visibility(self):
        if self.analysis_checkBox.isChecked():
            self.analine1.set_visible(True)
            self.analine2.set_visible(True)
        else:
            self.analine1.set_visible(False)
            self.analine2.set_visible(False)
        self.MplWidget.canvas.draw()
        self.update_bg()

    def time_visibility(self):
        if self.time_checkBox.isChecked():
            self.time_line.set_visible(True)
        else:
            self.time_line.set_visible(False)
        self.MplWidget.canvas.draw()
        self.update_bg()

    def people_visibility(self):
        if self.people_checkBox.isChecked():
            self.people_line.set_visible(True)
        else:
            self.people_line.set_visible(False)
        self.MplWidget.canvas.draw()
        self.update_bg()

    def test(self):
        tog = not self.cursor_toggle
        self.cursor = Cursor(self.MplWidget.canvas.axes, alpha=0.2, color = 'grey', vertOn=tog, horizOn=tog, linewidth = 1, useblit=True)
        self.cursor_toggle = tog
        #self.MplWudget.canvas.mpl_connect("axes_enter_event",self.update_bg)
        #self.update_bg()
        #self.MplWidget.canvas.restore_region(self.bg)


#=============================TAB1================================================================================

    def t1_date_label_change(self):
        input = self.t1_specificday_dateEdit.dateTime().toPyDateTime().date() #get date from dateEdit
        weekday = input.strftime('%a')                                        #get weekday
        self.t1_specificweekday_label.setText(weekday)                        #change label to weekday

    #---------------------------------TODAY----------------------
    def today(self):
        self.t1_specificday_dateEdit.setDateTime(QDateTime(QDateTime.currentDateTime()))

    #---------------------------YESTERDAY-----------------------
    def yesterday(self):
        now = datetime.datetime.today()
        tdelta = datetime.timedelta(days=-1)
        yesterday = now + tdelta
        self.t1_specificday_dateEdit.setDateTime(QDateTime(yesterday))

    #------------------UPDATE_SPECIFIC_DATE-------------------
    def update_specific_date(self):
        #self.t1_update_pushButton.setEnabled(False)
        d = self.t1_specificday_dateEdit.dateTime().toPyDateTime().date()  # get date from dateEdit
        var0 = d.strftime('%d/%m/%y')
        var1 = int(d.strftime('%e').lstrip('0'))  # day
        var2 = int(d.strftime('%m').lstrip('0'))  # month
        var3 = int(d.strftime('%y'))              # year
        var4 = d.strftime('%a')                   # weekday

        dates = [var0]
        days = [(2 * var1)]
        months = [var2]
        years = [var3]
        week = [var4]

        output = [days, months, week, years, dates]
        #print('specific',output)
        self.update_graph(output)
        self.notes()#output)
        #self.notes_enable()

    #---------------NOTES---------------
    def notes(self):#,output):
        # self.days = output[0]
        # self.months = output[1]
        # self.week = output[2]
        # self.years = output[3]
        # self.dates = output[4]

        global text

        conn = sqlite3.connect('PG2020_SQL.db')
        curs = conn.cursor()
        curs.execute("PRAGMA journal_mode=WAL;")

        curs.execute("SELECT Comments FROM puregym_table WHERE Day = '{}'".format(self.dates[0]))
        text_tuple = curs.fetchall()
        text = text_tuple[0][0]

        curs.close()
        conn.close()

        self.plainTextEdit.setPlainText(text)

        if text == None:
            self.plainTextEdit.setPlainText('No comment.')
        else:
            self.plainTextEdit.setPlainText(text)

        self.t1_save_pushButton.setEnabled(False)
        self.saved_label.setVisible(True)

    def notes_enable(self):
        self.t1_save_pushButton.setEnabled(True)
        self.saved_label.setVisible(False)


    def notes_save(self):
        d = self.t1_specificday_dateEdit.dateTime().toPyDateTime().date()
        var0 = d.strftime('%d/%m/%y')

        conn = sqlite3.connect('PG2020_SQL.db')
        curs = conn.cursor()
        curs.execute("PRAGMA journal_mode=WAL;")

        update = self.plainTextEdit.toPlainText()
        curs.execute("UPDATE puregym_table SET Comments = '{}' WHERE Day = '{}'".format(update,var0))
        conn.commit()

        curs.close()
        conn.close()

        self.t1_save_pushButton.setEnabled(False)
        self.saved_label.setVisible(True)
        self.notes()


#================================================================================================================








#=================================TAB2===========================================================================

    def t2_start_date_label_change(self):
        input1 = self.t2_start_dateEdit.dateTime().toPyDateTime().date()
        weekday1 = input1.strftime('%a')
        self.t2_selectweekdaystart_label.setText(weekday1)
        self.t2_start_dateEdit.setDateRange(QDate(2000, 1, 1), self.t2_end_dateEdit.date())

    def t2_end_date_label_change(self):
        input2 = self.t2_end_dateEdit.dateTime().toPyDateTime().date()
        weekday2 = input2.strftime('%a')
        self.t2_selectweekdayend_label.setText(weekday2)
        self.t2_end_dateEdit.setDateRange(self.t2_start_dateEdit.date(), QDate(QDateTime.currentDateTime().date()))

    #-------------------------TAB2_BUTTONS---------------------------------
    def one_week(self):
        input1 = self.t2_start_dateEdit.dateTime().toPyDateTime()
        tdelta = datetime.timedelta(days=6)
        new = input1+tdelta
        now = datetime.datetime.today()
        if new <= now:
            self.t2_end_dateEdit.setDateTime(new)
        else:
            self.t2_end_dateEdit.setDateTime(now)

    def one_month(self):
        input1 = self.t2_start_dateEdit.dateTime().toPyDateTime()
        tdelta = datetime.timedelta(days=27)
        new = input1+tdelta
        now = datetime.datetime.today()
        if new <= now:
            self.t2_end_dateEdit.setDateTime(new)
        else:
            self.t2_end_dateEdit.setDateTime(now)

    def past_week(self):
        now = datetime.datetime.today()
        tdelta = datetime.timedelta(days=-7)
        tdelta1 = datetime.timedelta(days=-1)
        new = now + tdelta
        now1 = now + tdelta1
        self.t2_start_dateEdit.setDateTime(new)
        self.t2_end_dateEdit.setDateTime(now1)

    def past_month(self):
        now = datetime.datetime.today()
        tdelta = datetime.timedelta(days=-28)
        tdelta1 = datetime.timedelta(days=-1)
        new = now + tdelta
        now1 = now + tdelta1
        self.t2_start_dateEdit.setDateTime(new)
        self.t2_end_dateEdit.setDateTime(now1)

    # ----------------------UPDATE_RANGE_DATES----------------------
    def update_range_dates(self):
        first_day = self.t2_start_dateEdit.dateTime().toPyDateTime().date()
        last_day = self.t2_end_dateEdit.dateTime().toPyDateTime().date()
        days_diff = (last_day - first_day).days

        dates = []
        days = []
        months = []
        years = []
        week = []
        for x in range(days_diff + 1):
            tdelta = datetime.timedelta(x)
            d = first_day + tdelta
            var0 = d.strftime('%d/%m/%y')
            var1 = int(d.strftime('%e').lstrip('0'))
            var2 = int(d.strftime('%m').lstrip('0'))
            var3 = int(d.strftime('%y'))
            var4 = d.strftime('%a')
            dates.append(var0)
            days.append((2 * var1))
            months.append(var2)
            years.append(var3)
            week.append(var4)

        output = [days, months, week, years, dates]
        #print('Range',output)
        self.update_graph(output)

#==================================================================================================================






#========================================TAB3======================================================================
    #No current functions
#==================================================================================================================







    def update_bg(self):
        self.bg = self.MplWidget.canvas.copy_from_bbox(self.MplWidget.canvas.axes.bbox)
        print('UpdateBackground')

#-----------------------------TIME_SLIDER-----------------------------------------------------------------------------
    def time_slider(self,value):
        if self.time_press_toggle:
            print('Slider Changed - time')
            minute = value%60
            hour = int((value - minute)/60)
            hourdelta = datetime.timedelta(hours = hour, minutes = minute)
            self.specifictime_timeEdit.setDateTime(datetime.datetime(2020,1,1,0,0,0)+hourdelta)
            self.MplWidget.canvas.blit(self.MplWidget.canvas.axes.bbox)

            if self.time_checkBox.isChecked():
                self.MplWidget.canvas.restore_region(self.bg)
                annotate_time = self.specifictime_timeEdit.dateTime().toPyDateTime()
                self.time_line, = self.MplWidget.canvas.axes.plot([annotate_time, annotate_time], [0, 130],
                                                                  linewidth=1,color='#2989e1', alpha=0.2, animated = True, visible=True)
                self.MplWidget.canvas.axes.draw_artist(self.time_line)
        else:
            print('Datechanged - time')
            try:
                self.time_line.remove()
            except:
                pass
            annotate_time = self.specifictime_timeEdit.dateTime().toPyDateTime()
            if self.time_checkBox.isChecked():
                self.time_line, = self.MplWidget.canvas.axes.plot([annotate_time, annotate_time], [0, 130],
                                                                  linewidth=1, color='#2989e1', alpha=0.2, visible=True)
            else:
                self.time_line, = self.MplWidget.canvas.axes.plot([annotate_time, annotate_time], [0, 130],
                                                                  linewidth=1, color='#2989e1', alpha=0.2, visible=False)
            self.MplWidget.canvas.draw()
            self.update_bg()

    def time_release(self):
        print('Slider released - time')
        self.time_press_toggle = False
        self.MplWidget.canvas.restore_region(self.bg)
        annotate_time = self.specifictime_timeEdit.dateTime().toPyDateTime()
        if self.time_checkBox.isChecked():
            self.time_line, = self.MplWidget.canvas.axes.plot([annotate_time, annotate_time], [0, 130],
                                                              linewidth=1, color='#2989e1', alpha=0.2, visible=True)
        else:
            self.time_line, = self.MplWidget.canvas.axes.plot([annotate_time, annotate_time], [0, 130],
                                                              linewidth=1, color='#2989e1', alpha=0.2, visible=False)
        self.MplWidget.canvas.draw()
        self.update_bg()

    def time_press(self):
        self.time_press_toggle = True
        print('Slider pressed - time line remove')
        try:
            self.time_line.remove()
            self.MplWidget.canvas.draw()
            self.update_bg()
        except:
            pass
        self.MplWidget.canvas.axes.draw_artist(self.time_line) #replace plotted line with animated line

    def time_slider_update(self):
        dt = self.specifictime_timeEdit.dateTime().toPyDateTime()
        self.time_horizontalSlider.setValue(time2num(dt)[0])
# ----------------------------------------------------------------------------------------------------------------------
# -----------------------------PEOPLE_SLIDER---------------------------------------------------------------------------
    def people_slider(self, value):
        if self.people_press_toggle:
            print('Slider Changed - people')
            self.people_spinBox.setValue(value)
            self.MplWidget.canvas.blit(self.MplWidget.canvas.axes.bbox)

            if self.people_checkBox.isChecked():
                self.MplWidget.canvas.restore_region(self.bg)
                annotate_people = self.people_spinBox.value()
                self.people_line, = self.MplWidget.canvas.axes.plot([datetime.datetime(2020, 1, 1, 0, 0, 0, 0), datetime.datetime(2020, 1, 1, 23, 59, 0, 0)],
                                                                    [annotate_people, annotate_people],
                                                                    linewidth=1, color='#2989e1', alpha=0.2, animated=True, visible=True)
                self.MplWidget.canvas.axes.draw_artist(self.people_line)
        else:
            print('Numbeerchanged - people')
            try:
                self.people_line.remove()
            except:
                pass
            annotate_people = self.people_spinBox.value()
            if self.people_checkBox.isChecked():
                self.people_line, = self.MplWidget.canvas.axes.plot([datetime.datetime(2020, 1, 1, 0, 0, 0, 0), datetime.datetime(2020, 1, 1, 23, 59, 0, 0)],
                                                                    [annotate_people, annotate_people],
                                                                    linewidth=1, color='#2989e1', alpha=0.2, visible=True)
            else:
                self.people_line, = self.MplWidget.canvas.axes.plot([datetime.datetime(2020, 1, 1, 0, 0, 0, 0), datetime.datetime(2020, 1, 1, 23, 59, 0, 0)],
                                                                    [annotate_people, annotate_people],
                                                                    linewidth=1, color='#2989e1', alpha=0.2, visible=False)
            self.MplWidget.canvas.draw()
            self.update_bg()

    def people_release(self):
        print('Slider released - people')
        self.people_press_toggle = False
        self.MplWidget.canvas.restore_region(self.bg)
        annotate_people = self.people_spinBox.value()
        if self.people_checkBox.isChecked():
            self.people_line, = self.MplWidget.canvas.axes.plot([datetime.datetime(2020, 1, 1, 0, 0, 0, 0), datetime.datetime(2020, 1, 1, 23, 59, 0, 0)],
                                                                [annotate_people, annotate_people],
                                                                linewidth=1, color='#2989e1', alpha=0.2, visible=True)
        else:
            self.people_line, = self.MplWidget.canvas.axes.plot([datetime.datetime(2020, 1, 1, 0, 0, 0, 0), datetime.datetime(2020, 1, 1, 23, 59, 0, 0)],
                                                                [annotate_people, annotate_people],
                                                                linewidth=1, color='#2989e1', alpha=0.2, visible=False)
        self.MplWidget.canvas.draw()
        self.update_bg()

    def people_press(self):
        self.people_press_toggle = True
        print('Slider pressed - people line remove')
        try:
            self.people_line.remove()
            self.MplWidget.canvas.draw()
            self.update_bg()
        except:
            pass
        self.MplWidget.canvas.axes.draw_artist(self.people_line)  # replace plotted line with animated line

    def people_slider_update(self):
        annotate_people = self.people_spinBox.value()
        self.people_horizontalSlider.setValue(annotate_people)
# ----------------------------------------------------------------------------------------------------------------------
# -----------------------------START_SLIDER-----------------------------------------------------------------------------
    def start_slider(self, value):
        if self.start_press_toggle:
            print('Slider Changed - start')
            minute = value % 60
            hour = int((value - minute) / 60)
            hourdelta = datetime.timedelta(hours=hour, minutes=minute)
            self.start_timeEdit.setDateTime(datetime.datetime(2020,1,1,0,0,0)+hourdelta)
            ######
            if self.start_horizontalSlider.value() > self.end_horizontalSlider.value():
                self.end_timeEdit.setDateTime(datetime.datetime(2020,1,1,0,0,0)+hourdelta)
                self.end_horizontalSlider.setValue(value)
            ######
            self.MplWidget.canvas.blit(self.MplWidget.canvas.axes.bbox)

            if self.analysis_checkBox.isChecked():
                self.MplWidget.canvas.restore_region(self.bg)
                start_time = self.start_timeEdit.dateTime().toPyDateTime()
                self.analine1, = self.MplWidget.canvas.axes.plot([start_time, start_time], [0, 130],
                                                                  linewidth=1, color='g', alpha=0.2, animated=True, visible=True)
                self.MplWidget.canvas.axes.draw_artist(self.analine1)
        else:
            print('Timechanged - start')
            try:
                self.analine1.remove()
            except:
                pass
            start_time = self.start_timeEdit.dateTime().toPyDateTime()
            if self.analysis_checkBox.isChecked():
                self.analine1, = self.MplWidget.canvas.axes.plot([start_time, start_time], [0, 130],
                                                                  linewidth=1, color='g', alpha=0.2, visible=True)
            else:
                self.analine1, = self.MplWidget.canvas.axes.plot([start_time, start_time], [0, 130],
                                                                  linewidth=1, color='g', alpha=0.2, visible=False)
            self.MplWidget.canvas.draw()
            self.update_bg()

    def start_release(self):
        print('Slider released - start')
        self.start_press_toggle = False
        self.MplWidget.canvas.restore_region(self.bg)
        start_time = self.start_timeEdit.dateTime().toPyDateTime()
        if self.analysis_checkBox.isChecked():
            self.analine1, = self.MplWidget.canvas.axes.plot([start_time, start_time], [0, 130],
                                                              linewidth=1, color='g', alpha=0.2, visible=True)
        else:
            self.analine1, = self.MplWidget.canvas.axes.plot([start_time, start_time], [0, 130],
                                                              linewidth=1, color='g', alpha=0.2, visible=False)
        self.MplWidget.canvas.draw()
        self.update_bg()

    def start_press(self):
        self.start_press_toggle = True
        print('Slider pressed - start line remove')
        try:
            self.analine1.remove()
            self.MplWidget.canvas.draw()
            self.update_bg()
        except:
            pass
        self.MplWidget.canvas.axes.draw_artist(self.analine1)  # replace plotted line with animated line

    def start_slider_update(self):
        dt = self.start_timeEdit.dateTime().toPyDateTime()
        self.start_horizontalSlider.setValue(time2num(dt)[0])
        ######
        if self.start_timeEdit.dateTime().toPyDateTime() > self.end_timeEdit.dateTime().toPyDateTime():
            self.end_timeEdit.setDateTime(dt)
            self.end_horizontalSlider.setValue(time2num(dt)[0])
        ######
# ----------------------------------------------------------------------------------------------------------------------
# -----------------------------END_SLIDER-----------------------------------------------------------------------------
    def end_slider(self, value):
        if self.end_press_toggle:
            print('Slider Changed - end')
            minute = value % 60
            hour = int((value - minute) / 60)
            hourdelta = datetime.timedelta(hours=hour, minutes=minute)
            self.end_timeEdit.setDateTime(datetime.datetime(2020,1,1,0,0,0)+hourdelta)
            ######
            if self.end_horizontalSlider.value() < self.start_horizontalSlider.value():
                self.start_timeEdit.setDateTime(datetime.datetime(2020,1,1,0,0,0)+hourdelta)
                self.start_horizontalSlider.setValue(value)
            ######
            self.MplWidget.canvas.blit(self.MplWidget.canvas.axes.bbox)

            if self.analysis_checkBox.isChecked():
                self.MplWidget.canvas.restore_region(self.bg)
                end_time = self.end_timeEdit.dateTime().toPyDateTime()
                self.analine2, = self.MplWidget.canvas.axes.plot([end_time, end_time], [0, 130],
                                                                  linewidth=1, color='g', alpha=0.2, animated=True, visible=True)
                self.MplWidget.canvas.axes.draw_artist(self.analine2)
        else:
            print('Timechanged - end')
            try:
                self.analine2.remove()
            except:
                pass
            end_time = self.end_timeEdit.dateTime().toPyDateTime()
            #end_time = datetime.datetime(2020,1,1,5,0,0,0)
            if self.analysis_checkBox.isChecked():
                self.analine2, = self.MplWidget.canvas.axes.plot([end_time, end_time], [0, 130],
                                                                  linewidth=1, color='g', alpha=0.2, visible=True)
            else:
                self.analine2, = self.MplWidget.canvas.axes.plot([end_time, end_time], [0, 130],
                                                                  linewidth=1, color='g', alpha=0.2, visible=False)
            self.MplWidget.canvas.draw()
            self.update_bg()

    def end_release(self):
        print('Slider released - end')
        self.end_press_toggle =  False
        self.MplWidget.canvas.restore_region(self.bg)
        end_time = self.end_timeEdit.dateTime().toPyDateTime()
        if self.analysis_checkBox.isChecked():
            self.analine2, = self.MplWidget.canvas.axes.plot([end_time, end_time], [0, 130],
                                                              linewidth=1, color='g', alpha=0.2, visible=True)
        else:
            self.analine2, = self.MplWidget.canvas.axes.plot([end_time, end_time], [0, 130],
                                                              linewidth=1, color='g', alpha=0.2, visible=False)
        self.MplWidget.canvas.draw()
        self.update_bg()

    def end_press(self):
        self.end_press_toggle = True
        print('Slider pressed - end line remove')
        try:
            self.analine2.remove()
            self.MplWidget.canvas.draw()
            self.update_bg()
        except:
            pass
        self.MplWidget.canvas.axes.draw_artist(self.analine2)  # replace plotted line with animated line

    def end_slider_update(self):
        dte = self.end_timeEdit.dateTime().toPyDateTime()
        self.end_horizontalSlider.setValue(time2num(dte)[0])
        ######
        if self.end_timeEdit.dateTime().toPyDateTime() < self.start_timeEdit.dateTime().toPyDateTime():
            self.start_timeEdit.setDateTime(dte)
            self.start_horizontalSlider.setValue(time2num(dte)[0])
        ######


# ----------------------------------------------------------------------------------------------------------------------

    #-------------------ANALYSIS_BUTTONS-------------------------------------
    def fullday(self):
        self.start_timeEdit.setDateTime(datetime.datetime(2020, 1, 1, 0, 0, 0))
        self.start_horizontalSlider.setValue(0)
        self.end_timeEdit.setDateTime(datetime.datetime(2020, 1, 1, 23, 59, 0))
        self.end_horizontalSlider.setValue(1439)

    def day(self):
        self.start_timeEdit.setDateTime(datetime.datetime(2020, 1, 1, 4, 30, 0))
        self.start_horizontalSlider.setValue(270)
        self.end_timeEdit.setDateTime(datetime.datetime(2020, 1, 1, 23, 30, 0))
        self.end_horizontalSlider.setValue(1410)

    def morning(self):
        self.start_timeEdit.setDateTime(datetime.datetime(2020, 1, 1, 4, 30, 0))
        self.start_horizontalSlider.setValue(270)
        self.end_timeEdit.setDateTime(datetime.datetime(2020, 1, 1, 9, 0, 0))
        self.end_horizontalSlider.setValue(540)

    def evening(self):
        self.start_timeEdit.setDateTime(datetime.datetime(2020, 1, 1, 16, 0, 0))
        self.start_horizontalSlider.setValue(960)
        self.end_timeEdit.setDateTime(datetime.datetime(2020, 1, 1, 21, 00, 0))
        self.end_horizontalSlider.setValue(1260)




#==============================================UPDATES=================================================================

    def update_graph(self,output):
        #print('update',output)
        self.days = output[0]
        self.months = output[1]
        self.week = output[2]
        self.years = output[3]
        self.dates = output[4]
        print('Start of update_graph: ', self.days, self.months, self.week, self.years, self.dates)

        self.MplWidget.canvas.axes.clear()
        self.progressBar.setValue(0)

        #---------------WEEKDAY_CHECKBOXES-----------------
        check_mon = self.t2_monday_checkBox.isChecked() # True = KEEP   #False = REMOVE
        check_tue = self.t2_tuesday_checkBox.isChecked()
        check_wed = self.t2_wednesday_checkBox.isChecked()
        check_thu = self.t2_thursday_checkBox.isChecked()
        check_fri = self.t2_friday_checkBox.isChecked()
        check_sat = self.t2_saturday_checkBox.isChecked()
        check_sun = self.t2_sunday_checkBox.isChecked()

        mon = [i for i, x in enumerate(self.week) if x == 'Mon' and not check_mon]  # List of indices which are to be removed
        tue = [i for i, x in enumerate(self.week) if x == 'Tue' and not check_tue]
        wed = [i for i, x in enumerate(self.week) if x == 'Wed' and not check_wed]
        thu = [i for i, x in enumerate(self.week) if x == 'Thu' and not check_thu]
        fri = [i for i, x in enumerate(self.week) if x == 'Fri' and not check_fri]
        sat = [i for i, x in enumerate(self.week) if x == 'Sat' and not check_sat]
        sun = [i for i, x in enumerate(self.week) if x == 'Sun' and not check_sun]

        weekdays_list = mon + tue + wed + thu + fri + sat + sun
        #print(weekdays_list)
        weekdays_list.sort(reverse=True)
        #print(weekdays_list)
        for value in weekdays_list:
            del self.days[value]
            del self.months[value]
            del self.week[value]
            del self.years[value]
            del self.dates[value]

        print('After deletion in update_graph: ', self.days, self.months, self.week, self.years, self.dates)
        #-------------------------------------------------

        #----------------ADAPTIVE LEGEND--------------------
        global state
        if self.rawdata_checkBox.isChecked() and self.smootheddata_checkBox.isChecked():
            state = 1
        elif self.smootheddata_checkBox.isChecked():
            state = 2
        elif self.rawdata_checkBox.isChecked():
            state = 3
        else:
            state = 4
        #--------------------------------------------------

        #----------------------------AXES-----------------------------------
        ax = self.MplWidget.canvas.axes
        xfmt = mdates.DateFormatter('%H:%M')
        ax.xaxis.set_minor_locator(AutoMinorLocator())
        ax.xaxis.set_major_formatter(xfmt)
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))                                                            # So that y-axis is integer until scale is <1


        #SET X_AXIS
        self.MplWidget.canvas.axes.set_xticks(x_list, minor=False) #could set up 15min list for minors
        #self.MplWidget.canvas.axes.set_xlim((datetime.datetime(2020, 1, 1, 0, 0, 0, 0), datetime.datetime(2020, 1, 2, 0, 0, 0, 0)))  # x-axis end lim 00:00
        self.MplWidget.canvas.axes.set_xlim((datetime.datetime(2020, 1, 1, 0, 0, 0, 0), datetime.datetime(2020, 1, 1, 23, 59, 0, 0))) # x-axis end lim 23:59
        #self.MplWidget.canvas.axes.axis([0, 1440, 0, 130])
        self.MplWidget.canvas.axes.set_ylim((0, 130))                                                                          # set x_lim for old time_vec

        #OTHER PLOT DETAILS
        self.MplWidget.canvas.axes.set_xlabel('Time')
        self.MplWidget.canvas.axes.set_ylabel('Number of People')
        self.MplWidget.canvas.axes.locator_params(axis='y', nbins=13)
        # --------------------------------------------------------------------

        #----------------------LOAD_DATA_SQL----------------------------------------------------
        myLists = []
        for index0 in range(len(self.dates)):
            myLists.append([0] * 1440)

        conn = sqlite3.connect('PG2020_SQL.db')
        curs = conn.cursor()
        curs.execute("PRAGMA journal_mode=WAL;")

        mean_data = [0] * 1440
        none_index = [0] * 1440
        for index in range(len(myLists)):
            curs.execute("SELECT * FROM puregym_table WHERE Day = '{}'".format(self.dates[index]))
            values = curs.fetchall()
            for index1 in range(1440):
                entry = values[0][index1 + 1]
                myLists[index][index1] = entry
                if not entry == None:
                    mean_data[index1] += entry
                    none_index[index1] += 1

        curs.close()
        conn.close()

        yourLists = [[]] * len(myLists)
        for index0 in range(len(myLists)):
            vec = [None] * 1440

            for index1 in range(1426):  # 0,...,1425
                rolling_sum = 0
                rolling_list = []

                for value in myLists[index0][index1:index1 + 15]:
                    if not value == None:
                        rolling_sum += value
                        rolling_list.append(value)

                if rolling_sum == 0:
                    vec[index1 + 7] = None
                else:
                    vec[index1 + 7] = round(sum(rolling_list)/len(rolling_list), 2)

            yourLists[index0] = vec

        for day in range(len(myLists)):
            print(myLists[day])
            #print(yourLists[day])

        global lines, lined_raw, lined_smooth, raw_lines, smooth_lines, alpha_raw, alpha_smooth
        #lines = [] #all lines
        raw_lines = [] #raw lines
        smooth_lines = [] #smooth lines
        lined_raw = {}
        lined_smooth = {}
        alpha_smooth = {}
        alpha_raw = {}

        labels = []
        print('Before lines plot: ', self.days, self.months, self.week, self.years, self.dates)
        for index in range(len(myLists)):
            #print(myLists[index])

            if not myLists[index].count(None) == len(myLists[index]):
                labels.append(self.week[index] + ' ' + str(self.dates[index]))
                print(myLists[index].count(None),len(myLists[index]),self.dates[index])
                line1, = self.MplWidget.canvas.axes.plot(time_vec, myLists[index], linewidth=1, label=self.week[index] + ' ' + str(self.dates[index])) #visible=self.rawdata_checkBox.isChecked()
                line2, = self.MplWidget.canvas.axes.plot(time_vec, yourLists[index], linewidth=1, label=self.week[index] + ' ' + str(self.dates[index])) #visible=smootheddata_checkBox.isChecked()
                print(self.dates[index])
                #lines.append(line1)
                #lines.append(line2)
                raw_lines.append(line1)
                smooth_lines.append(line2)

            self.progressBar.setValue(round((index + 1) * 100 / (len(myLists)), 2))

        #-----------------GRIDLINES-------------------
        self.MplWidget.canvas.axes.grid(alpha = 0.25)
        self.gridlines_visibility()
        #---------------------------------------------

        #------------------------------LEGENDS-------------------------------------------------
        self.leg = self.MplWidget.canvas.axes.legend(raw_lines,labels,loc='upper left', title='Raw Data')
        self.leg2 = self.MplWidget.canvas.axes.legend(smooth_lines,labels,loc='upper left', bbox_to_anchor=(0.13,1) , title='Smoothed Data')

        self.MplWidget.canvas.axes.add_artist(self.leg) #add back removed artist
        #SET BOTH VISIBLE INITIALLY
        self.legend_visibility()
        #--------------------------------------------------------------------------------------

        self.update_bg()
        #---------------------ANNOTATIONS---------------------------------
        #VERTICAL_TIME_LINE
        try:
            annotate_time = self.specifictime_timeEdit.dateTime().toPyDateTime()#.time()
            self.time_line, = self.MplWidget.canvas.axes.plot([annotate_time,annotate_time],[0, 130], linewidth=1, color='#2989e1',alpha=0.2)
        except:
            pass

        #HORIZONTAL_PEOPLE_LINE
        try:
            annotate_people = self.people_spinBox.value()
            self.people_line, = self.MplWidget.canvas.axes.plot([datetime.datetime(2020, 1, 1, 0, 0, 0, 0), datetime.datetime(2020, 1, 1, 23, 59, 0, 0)],[annotate_people, annotate_people], linewidth=1, color='#2989e1', alpha=0.2)
        except:
            pass

        #MEAN_RAW_DATA_LINE
        for index in range(1440):
            if not none_index[index] == 0:
                mean_data[index] = (mean_data[index]/none_index[index])
            else:
                mean_data[index] = None
        try:
            self.line_mean, = self.MplWidget.canvas.axes.plot(time_vec,mean_data, linewidth=2, color='r')
        except:
            print('No data to create mean line.')
        #----------------------------------------------------------------------

        #-------------------LEGEND_PICKING-------------------------------------------------
        try:
            for legline_raw, origline_raw in zip(self.leg.get_lines(), raw_lines):
                legline_raw.set_picker(True)  # Enable picking on the legend line.
                print('picker')
                lined_raw[legline_raw] = origline_raw

            for legline_raw in self.leg.get_lines():
                alpha_raw[legline_raw] = True
                #=====If want non-selected data at time of update to not automatically be shown when turned on======#
                # if self.rawdata_checkBox.isChecked():
                #     alpha_raw[legline_raw] = True
                # else:
                #     alpha_raw[legline_raw] = False

            for legline_smooth, origline_smooth in zip(self.leg2.get_lines(), smooth_lines):
                legline_smooth.set_picker(True)
                lined_smooth[legline_smooth] = origline_smooth

            for legline_smooth in self.leg2.get_lines():
                alpha_smooth[legline_smooth] = True
                #=====If want non-selected data at time of update to not automatically be shown when turned on======#
                # if self.smootheddata_checkBox.isChecked():
                #     alpha_smooth[legline_smooth] = True
                # else:
                #     alpha_smooth[legline_smooth] = False
        except:
            # There are no lines/legends (no data).
            pass

        #True if visible when line updated and False if invisible when line updated.
        #print(alpha_raw)    # Dictionary {legline_raw: {True/False}}
        #print(alpha_smooth) # Dictionary {legline_smooth: {True/False}}

        self.raw_visiblility()
        self.smooth_visibility()
        self.mean_visibility()
        self.time_visibility()
        self.people_visibility()


        #----------------------------------------------------------------------------------

        #self.MplWidget.canvas.draw()
        self.update_analysis()

        #DRAW ANIMATED LINES
        self.MplWidget.canvas.axes.draw_artist(self.time_line)
        self.MplWidget.canvas.axes.draw_artist(self.people_line)
        self.MplWidget.canvas.axes.draw_artist(self.analine1)
        self.MplWidget.canvas.axes.draw_artist(self.analine2)



    def update_analysis(self):
        #print('Start of update_analysis: ', self.days , self.months, self.week, self.years, self.dates)
        self.mean_var_label.setText('Calculating')
        self.min_var_label.setText('Calculating')
        self.max_var_label.setText('Calculating')
        self.range_var_label.setText('Calculating')

        start_datetime = self.start_timeEdit.dateTime().toPyDateTime()
        end_datetime = self.end_timeEdit.dateTime().toPyDateTime()
        start = time2num(start_datetime) #(num,hour,min)
        end = time2num(end_datetime)     #(num,hour,min)
        print(start,end)
        analysis_range = end[0]-start[0]+1
        try:
            self.analine1.remove()
            self.analine2.remove()
        except:
            pass
        self.analine1, = self.MplWidget.canvas.axes.plot([start_datetime,start_datetime],[0, 130], linewidth=1, color='g', alpha=0.2)
        self.analine2, = self.MplWidget.canvas.axes.plot([end_datetime,end_datetime],[0, 130], linewidth=1, color='g', alpha=0.2)

        self.analine_visibility()
        #----------------------LOAD_DATA_SQL----------------------------------------------------
        self.mean_list = []

        myLists=[]
        for index0 in range(len(self.dates)):
            myLists.append([0]*analysis_range)

        conn = sqlite3.connect('PG2020_SQL.db')
        curs = conn.cursor()
        curs.execute("PRAGMA journal_mode=WAL;")

        for index in range(len(myLists)):
            curs.execute("SELECT * FROM puregym_table WHERE Day = '{}'".format(self.dates[index]))
            values = curs.fetchall()
            for index1 in range(analysis_range): #+- 1 out????
                myLists[index][index1] = values[0][start[0] + index1 + 1]
                if not myLists[index][index1] == None:
                    self.mean_list.append(values[0][start[0] + index1 + 1])

        curs.close()
        conn.close()

        # print('myLists : ',myLists)
        # print('Number of days in myLists :',len(myLists))
        # print('Length of analysis window: ',len(myLists[0]))
        # print('Analysis range: ',analysis_range)
        # print('Mean list: ', self.mean_list)
        #-----------------------------------------------------------------------------------

        try:
            mean_var = int(round(sum(self.mean_list) / len(self.mean_list)))
            self.mean_var_label.setText(str(mean_var))
            min_var = int(round(min(self.mean_list)))
            max_var = int(round(max(self.mean_list)))
            range_var = max_var - min_var + 1
            self.min_var_label.setText(str(min_var))
            self.max_var_label.setText(str(max_var))
            self.range_var_label.setText(str(range_var))
        except:
            self.mean_var_label.setText('No Data')
            self.min_var_label.setText('No Data')
            self.max_var_label.setText('No Data')
            self.range_var_label.setText('No Data')


#====================================================================================================================




#-------------DRIVER_CODE------------------
#def main():
app = QApplication([])
app.setStyle('Fusion')
window = MatplotlibWidget()
window.show()
window.today()
window.update_specific_date()
app.exec_()

#if __name__ == '__main__':
   #main()
