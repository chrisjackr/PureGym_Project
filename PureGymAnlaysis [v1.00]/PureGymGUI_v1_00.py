# ------------------------------------------------------
# ------------------ PureGymGUI_v1_00.py -------------------
# ------------------------------------------------------

###GUI_IMPORT
from PyQt5.QtWidgets import *
#QWidget, QGridLayout, QPushButton, QSizePolicy, QApplication
from PyQt5.uic import loadUi
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtCore import *


###RANDOM_IMPORT
from PureGymFunctions_v1_00 import num2time, time2num
import sys
import numpy as np
from numpy import linspace
import random
import math
from math import cos,sin,pi
import time
import datetime

###PLOT_IMPORT
from matplotlib import pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_qt5agg import (NavigationToolbar2QT as NavigationToolbar)
from matplotlib.ticker import (AutoMinorLocator, AutoLocator, LinearLocator, FixedLocator,FormatStrFormatter,AutoMinorLocator)
from matplotlib.widgets import Cursor

from openpyxl import Workbook, load_workbook
import sqlite3

#---------------------------------------------------------
#---------------------------------------------------------
#---------------------------------------------------------




#-------------------------TIME SERIES--------------------------
# time_vec = []
# for i in range(1440):
#     time_vec.append(i)

time_vec = []
for i in range(1440):
    tdelta = datetime.timedelta(minutes=i)
    time_vec.append(datetime.datetime(2020,1,1,0,0,0,0)+tdelta)

x_label = []
x_list = []
for i in range(24):
    x_list.append(datetime.datetime(2020, 1, 1, i, 0, 0, 0))
    M = datetime.datetime(2020, 1, 1, i, 0, 0, 0).strftime('%M')
    H = datetime.datetime(2020, 1, 1, i, 0, 0, 0).strftime('%H')
    x_label.append(str(H+':'+M))


x_list.append(datetime.datetime(2020,1,2,0,0,0,0))
x_label.append('24:00')
#print(x_list)
#print(x_label)
#--------------------------------------------------------------





class MatplotlibWidget(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)
        loadUi("PureGymGUI_v1_00.ui", self)
        QMainWindow.showMaximized(self)

        self.setWindowTitle("PureGym Analytics GUI [v1.00]")
        self.label_title.setText('PureGym Analysis    [v1.00]')
        self.addToolBar(NavigationToolbar(self.MplWidget.canvas, self))
        self.line.setGeometry(QtCore.QRect(350, 10, 20, 1000))
        self.MplWidget.setGeometry(QtCore.QRect(370, 10, 1530, 950))  #(xpos,ypos,xwidth,yheight)
        self.cursor = Cursor(self.MplWidget.canvas.axes, alpha=0.2, color = 'grey', linewidth = 1, useblit=True)




    #DATA_TYPES_BOX
        self.rawdata_checkBox.stateChanged.connect(lambda: self.t1_update_pushButton.setEnabled(True))
        self.smootheddata_checkBox.stateChanged.connect(lambda: self.t1_update_pushButton.setEnabled(True))
        self.meandata_checkBox.stateChanged.connect(lambda: self.t1_update_pushButton.setEnabled(True))
        self.rawdata_checkBox.stateChanged.connect(lambda: self.t2_update_pushButton.setEnabled(True))
        self.smootheddata_checkBox.stateChanged.connect(lambda: self.t2_update_pushButton.setEnabled(True))
        self.meandata_checkBox.stateChanged.connect(lambda: self.t2_update_pushButton.setEnabled(True))

    #OPTIONS_BOX
        self.gridlines_checkBox.stateChanged.connect(lambda: self.t1_update_pushButton.setEnabled(True))
        self.legend_checkBox.stateChanged.connect(lambda: self.t1_update_pushButton.setEnabled(True))
        self.analysis_checkBox.stateChanged.connect(lambda: self.t1_update_pushButton.setEnabled(True))
        self.gridlines_checkBox.stateChanged.connect(lambda: self.t2_update_pushButton.setEnabled(True))
        self.legend_checkBox.stateChanged.connect(lambda: self.t2_update_pushButton.setEnabled(True))
        self.analysis_checkBox.stateChanged.connect(lambda: self.t2_update_pushButton.setEnabled(True))

    #ANNOTATIONS_BOX
        self.time_checkBox.stateChanged.connect(lambda: self.t1_update_pushButton.setEnabled(True))
        self.time_checkBox.stateChanged.connect(lambda: self.t2_update_pushButton.setEnabled(True))
        self.time_horizontalSlider.setRange(0,1439)
        self.time_horizontalSlider.setFocusPolicy(Qt.NoFocus)
        self.time_horizontalSlider.valueChanged.connect(self.time_slider)
        self.specifictime_timeEdit.timeChanged.connect(self.time_slider1)

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

        self.legend_checkBox.stateChanged.connect(lambda: self.t2_update_pushButton.setEnabled(True))
        self.t2_start_dateEdit.dateChanged.connect(lambda: self.t2_update_pushButton.setEnabled(True))
        self.t2_end_dateEdit.dateChanged.connect(lambda: self.t2_update_pushButton.setEnabled(True))
        self.t2_monday_checkBox.stateChanged.connect(lambda: self.t2_update_pushButton.setEnabled(True))
        self.t2_tuesday_checkBox.stateChanged.connect(lambda: self.t2_update_pushButton.setEnabled(True))
        self.t2_wednesday_checkBox.stateChanged.connect(lambda: self.t2_update_pushButton.setEnabled(True))
        self.t2_thursday_checkBox.stateChanged.connect(lambda: self.t2_update_pushButton.setEnabled(True))
        self.t2_friday_checkBox.stateChanged.connect(lambda: self.t2_update_pushButton.setEnabled(True))
        self.t2_saturday_checkBox.stateChanged.connect(lambda: self.t2_update_pushButton.setEnabled(True))
        self.t2_sunday_checkBox.stateChanged.connect(lambda: self.t2_update_pushButton.setEnabled(True))

        self.t2_update_pushButton.clicked.connect(self.update_range_dates)




    #TAB3
        #No functions yet



    #ANALYSIS_BOX
        #START WINDOW
        self.start_horizontalSlider.setRange(0,1439)
        self.start_horizontalSlider.setFocusPolicy(Qt.NoFocus)
        self.start_horizontalSlider.valueChanged.connect(self.start_slider)
        self.start_horizontalSlider.setValue(0)
        self.start_timeEdit.timeChanged.connect(self.start_slider1)

        #END WINDOW
        self.end_horizontalSlider.setRange(0,1439)
        self.end_horizontalSlider.setFocusPolicy(Qt.NoFocus)
        self.end_horizontalSlider.valueChanged.connect(self.end_slider)
        self.end_horizontalSlider.setValue(1439)
        self.end_timeEdit.timeChanged.connect(self.end_slider1)

        #BUTTONS
        self.fullday_pushButton.clicked.connect(self.fullday)
        self.day_pushButton.clicked.connect(self.day)
        self.morning_pushButton.clicked.connect(self.morning)
        self.evening_pushButton.clicked.connect(self.evening)

        #UPDATE ANALYSIS
        #self.update_pushButton.clicked.connect(self.update_options)
        #self.update_pushButton.clicked.connect(self.update_analysis)


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

        conn = sqlite3.connect('PG2020_SQL_v1_00.db')
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

        conn = sqlite3.connect('PG2020_SQL_v1_00.db')
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




    #-----------------------------SLIDERS---------------------------------------------------
    def time_slider(self,value):
        if self.time_checkBox.isChecked():
            self.t1_update_pushButton.setEnabled(True)
            self.t2_update_pushButton.setEnabled(True)
        minute = value%60
        hour = int((value - minute)/60)
        #print(value,hour,minute)
        hourdelta = datetime.timedelta(hours = hour, minutes = minute)
        self.specifictime_timeEdit.setDateTime(datetime.datetime(2020,1,1,0,0,0)+hourdelta)

    def time_slider1(self):
        if self.time_checkBox.isChecked():
            self.t1_update_pushButton.setEnabled(True)
            self.t2_update_pushButton.setEnabled(True)
        dt = self.specifictime_timeEdit.dateTime().toPyDateTime()
        #print(time2num(dt)[0])
        self.time_horizontalSlider.setValue(time2num(dt)[0])

    def start_slider(self,value):
        minute = value%60
        hour = int((value - minute)/60)
        #print(value,hour,minute)
        hourdelta = datetime.timedelta(hours = hour, minutes = minute)
        self.start_timeEdit.setDateTime(datetime.datetime(2020,1,1,0,0,0)+hourdelta)
        if self.start_horizontalSlider.value() > self.end_horizontalSlider.value():
            self.end_timeEdit.setDateTime(datetime.datetime(2020,1,1,0,0,0)+hourdelta)
            self.end_horizontalSlider.setValue(value)

    def start_slider1(self):
        dt = self.start_timeEdit.dateTime().toPyDateTime()
        #print(time2num(dt)[0])
        self.start_horizontalSlider.setValue(time2num(dt)[0])

    def end_slider(self,value):
        minute = value%60
        hour = int((value - minute)/60)
        #print(value,hour,minute)
        hourdelta = datetime.timedelta(hours = hour, minutes = minute)
        self.end_timeEdit.setDateTime(datetime.datetime(2020,1,1,0,0,0)+hourdelta)
        if self.end_horizontalSlider.value() < self.start_horizontalSlider.value():
            self.start_timeEdit.setDateTime(datetime.datetime(2020,1,1,0,0,0)+hourdelta)
            self.start_horizontalSlider.setValue(value)

    def end_slider1(self):
        dt = self.end_timeEdit.dateTime().toPyDateTime()
        #print(time2num(dt)[0])
        self.end_horizontalSlider.setValue(time2num(dt)[0])


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
        #print('Start of update_graph: ', self.days, self.months, self.week, self.years, self.dates)

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

        #print('After deletion in update_graph: ', self.days, self.months, self.week, self.years, self.dates)
        #-------------------------------------------------

        #----------------ADAPTIVE LEGEND--------------------
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

        conn = sqlite3.connect('PG2020_SQL_v1_00.db')
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

        #print('myLists: ',len(myLists))
        #print(myLists)
        #print('yourLists: ',len(yourLists))
        #print(yourLists)

        for index in range(len(myLists)):
            #print(myLists[index])

            dict_raw = {1: '_nolegend_',
                        2: '_nolegend_',
                        3: self.week[index] + ' ' + str(self.dates[index]),
                        4: '_nolegend_'}
            dict_smooth = {1: self.week[index] + ' ' + str(self.dates[index]),
                           2: self.week[index] + ' ' + str(self.dates[index]),
                           3: '_nolegend_',
                           4: '_nolegend_'}

            if state == 1 and not myLists[index].count(None) == len(myLists[index]):
                self.MplWidget.canvas.axes.plot(time_vec, myLists[index], linewidth=1, label=dict_raw[1], visible=self.rawdata_checkBox.isChecked())
                self.MplWidget.canvas.axes.plot(time_vec, yourLists[index], linewidth=1, label=dict_smooth[1], visible=self.smootheddata_checkBox.isChecked())
            elif state == 2 and not myLists[index].count(None) == len(myLists[index]):
                self.MplWidget.canvas.axes.plot(time_vec, yourLists[index], linewidth=1, label=dict_smooth[2], visible=self.smootheddata_checkBox.isChecked())
            elif state == 3 and not myLists[index].count(None) == len(myLists[index]):
                self.MplWidget.canvas.axes.plot(time_vec, myLists[index], linewidth=1, label=dict_raw[3], visible=self.rawdata_checkBox.isChecked())
            elif state == 4:
                pass
            self.progressBar.setValue(round((index + 1) * 100 / (len(myLists)), 2))


        #---------------------ANNOTATIONS---------------------------------
        if self.time_checkBox.isChecked():
            try:
                annotate_time = self.specifictime_timeEdit.dateTime().toPyDateTime()#.time()
                # hour = annotate_time.hour
                # minute = annotate_time.minute
                # minutes = (hour * 60) + minute
                # self.MplWidget.canvas.axes.plot([time_vec[minutes],time_vec[minutes]], [0,130], linewidth=1, color='r')
                self.MplWidget.canvas.axes.plot([annotate_time, annotate_time], [0, 130], linewidth=1, color='r',alpha=0.2)
            except:
                pass

        if self.meandata_checkBox.isChecked():
            for index in range(1440):
                if not none_index[index] == 0:
                    mean_data[index] = (mean_data[index]/none_index[index])
                else:
                    mean_data[index] = None
            try:
                self.MplWidget.canvas.axes.plot(time_vec,mean_data, linewidth=2, color='r')
            except:
                pass

        #-----------------------GRIDLINES/LEGEND---------------------------
        if self.gridlines_checkBox.isChecked() == True:
            self.MplWidget.canvas.axes.grid(True)
        else:
            self.MplWidget.canvas.axes.grid(False)

        if self.legend_checkBox.isChecked() == True:
            self.MplWidget.canvas.axes.legend()
        else:
            self.MplWidget.canvas.axes.legend().remove()
        #-----------------------------------------------------------



        self.MplWidget.canvas.draw()
        self.update_analysis()


    def update_options(self):
        #self.update_analysis()
        pass
        ##########BUG############::::Analysis window prints multiple (from self.update_analysis)

        '''
        #For future updates when automatic line updates used.
        #self.line.remove()
        print(self.MplWidget.canvas.axes.lines)
        self.MplWidget.canvas.axes.lines[-3].remove()
        self.MplWidget.canvas.draw()
        '''

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
        analysis_range = end[0]-start[0]+1
        if self.analysis_checkBox.isChecked():
            # self.MplWidget.canvas.axes.plot([start[0], start[0]], [0, 130], linewidth=1, color='g')
            # self.MplWidget.canvas.axes.plot([end[0],end[0]], [0, 130], linewidth=1, color='g')
            self.analine1 = self.MplWidget.canvas.axes.plot([start_datetime, start_datetime], [0, 130], linewidth=1, color='g', alpha=0.2)
            self.analine2 = self.MplWidget.canvas.axes.plot([end_datetime,end_datetime], [0, 130], linewidth=1, color='g', alpha=0.2)
            self.MplWidget.canvas.draw()

        #----------------------LOAD_DATA_SQL----------------------------------------------------
        self.mean_list = []

        myLists=[]
        for index0 in range(len(self.dates)):
            myLists.append([0]*analysis_range)

        conn = sqlite3.connect('PG2020_SQL_v1_00.db')
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
window = MatplotlibWidget()
window.show()
window.today()
window.update_specific_date()
app.exec_()

#if __name__ == '__main__':
   #main()