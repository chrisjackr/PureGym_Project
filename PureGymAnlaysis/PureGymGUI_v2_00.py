# ============================================================================================================================================================================================================================================================== #
# --------------------------------------------------------------------------------------------------------------- PureGymGUII2.py ------------------------------------------------------------------------------------------------------------------------------ #
# ============================================================================================================================================================================================================================================================== #

#GUI_IMPORT
from PyQt5.uic import loadUi
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.Qt import QStandardItemModel, QStandardItem
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

#RANDOM_IMPORT
import sys
import numpy as np
from numpy import linspace
import random
import math
from math import cos,sin,pi
import time
import datetime
import pandas as pd

#PLOT_IMPORT
from matplotlib import pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_qt5agg import (NavigationToolbar2QT as NavigationToolbar)
from matplotlib.backend_tools import ToolToggleBase
from matplotlib.ticker import (AutoMinorLocator, AutoLocator, LinearLocator, MaxNLocator, FixedLocator,FormatStrFormatter,AutoMinorLocator)
from matplotlib.widgets import Cursor, SpanSelector, MultiCursor


#DATABASE_IMPORT
#from openpyxl import Workbook, load_workbook
import sqlite3

#MY_MODULES_AND_FUNCTIONS
from PureGymFunctions import num2time, time2num

#======================================================================================================================#


#===========================================AUXILARY_FUNCTIONS=========================================================#
# ----------------------------------------------------------TIME_SERIES
time_vec = []                                                                                                            # Creates a 1440 length vector with datetime entries between 00:00 and 23:59. Note that the Year Day and Month are set to 01/01/2020.
for i in range(1440):                                                                                                    # This needs to be specified when plotting graphs, even though only HH:MM is shown on the x-axis
    tdelta = datetime.timedelta(minutes=i)
    time_vec.append(datetime.datetime(2020,1,1,0,0,0,0)+tdelta)

# ----------------------------------------------------------X_AXIS_LABELS
x_label = []                                                                                                             # x_list contains a list with the 24 hours in datetime format.
x_list = []                                                                                                              # x_label contains a list with the 24 hour labels: [00:00, 01:00, 02:00, ... , 23:00]
for i in range(24):
    x_list.append(datetime.datetime(2020, 1, 1, i, 0, 0, 0))
    M = datetime.datetime(2020, 1, 1, i, 0, 0, 0).strftime('%M')
    H = datetime.datetime(2020, 1, 1, i, 0, 0, 0).strftime('%H')
    x_label.append(str(H+':'+M))

x_list.append(datetime.datetime(2020,1,2,0,0,0,0))                                                                       # Adds midnight to list.
x_label.append('24:00')                                                                                                  # Adds 24:00 to list.


# ----------------------------------------------------------TEST_FUNCTIONS
global alpha1
alpha1 = 0.2

# ----------------------------------------------------------LINE_PICKER

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

def editor_on_pick(event):
        try:
            editor_legline = event.artist

            editor_origline = editor_lined[editor_legline]
            editor_marker_line = editor_markerlined[editor_legline]

            editor_visible = not editor_origline.get_visible()  # equivalent for marker_line

            editor_alpha[editor_legline] = editor_visible
            editor_legline.set_alpha(1.0 if editor_visible else 0.2)

            editor_origline.set_visible(editor_visible)                                                                      # Change the visibility of the lines on the graph.
            if window.editor_marker_checkBox.isChecked():                                                                    # Change the visibility of the marker lines on the graph depending on toggle.
                editor_marker_line.set_visible(editor_visible)
            else:
                editor_marker_line.set_visible(False)

        except:
            pass
        window.MplWidget1.canvas.draw()

#======================================================================================================================#

class HelpWindow(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        loadUi("HelpGUI.ui", self)
        self.setWindowTitle("Help")

class VisualProperties(QWidget):
    def __init__(self, window):
        QWidget.__init__(self)
        loadUi("VisualPropertiesGUI.ui", self)
        self.setWindowTitle("Visual Properties")
        # VISUAL PROPERTIES
        # self.vp_opacity_horizontalSlider.valueChanged.connect(self.alpha_slider)
        # self.vp_cursor_pushButton.clicked.connect(window.cursor_toggle)
        self.vp_test_pushButton.clicked.connect(window.test)

    def alpha_slider(self):
        print('dg')
        #self.vp_opacity_SpinBox.setValue(self.vp_opacity_horizontalSlider.value())

class MatplotlibWidget(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)
        loadUi("PureGymGUI.ui", self)                                                                                   # Load GUI file.
        QMainWindow.showMaximized(self)                                                                                  # Fit window to full screen.
        self.setWindowTitle("PureGym Analytics GUI [v2.00]")                                                             # Set window title.
        self.addToolBar(NavigationToolbar(self.MplWidget.canvas,self))                                                  # Add toolbars to window.
        self.addToolBar(NavigationToolbar(self.MplWidget1.canvas, self))                                                 #  "                   "
        #self.showMaximized()
        self.stackedWidget.setCurrentIndex(0)                                                                            # Set starting page to 'Analysis' page
        #SET_WINDOW_SIZE_MANUALLY
        # self.line.setGeometry(QtCore.QRect(350, 10, 20, 1000))
        # self.MplWidget.setGeometry(QtCore.QRect(370, 10, 1530, 950))  #(xpos,ypos,xwidth,yheight)
        self.MplWidget.canvas.mpl_connect('pick_event', on_pick)
        self.MplWidget1.canvas.mpl_connect('pick_event', editor_on_pick)
        self.attr = 'Hi'

    #CURSOR
        self.cursor = Cursor(self.MplWidget.canvas.axes, alpha=0.2, color = 'grey', vertOn=True, horizOn=True, linewidth = 1, useblit=True)                             # Add cursor to first plot.
        self.cursor1 = Cursor(self.MplWidget1.canvas.axes, alpha=0.2, color = 'grey', vertOn=False, horizOn=False, linewidth = 1, useblit=True)                         # Add cursor to first plot.
        self.cursor_toggle = True                                                                                                                                       # First plot cursor visibility variable (True = visible)
        self.spanselector = SpanSelector(self.MplWidget1.canvas.axes, self.span_select, 'horizontal', useblit = True, rectprops=dict(alpha=0.25,facecolor='yellow'))    # Add spanselector to second plot.

    #MENU
        self.actionAnalysis_0.triggered.connect(lambda: self.stackedWidget.setCurrentIndex(0))                           # Change page to 'Analysis'
        self.actionStatistics_0.triggered.connect(lambda: self.stackedWidget.setCurrentIndex(1))                         # Change page to 'Statistics'
        self.actionMachine_Learning_0.triggered.connect(lambda: self.stackedWidget.setCurrentIndex(2))                   # Change page to 'Machine Learning'
        self.actionDatabase_Editor_0.triggered.connect(lambda: self.stackedWidget.setCurrentIndex(3))                    # Change page to 'Data Editor'

        self.actionHelp.triggered.connect(self.help_popup)                                                               # Open up 'Help' window
        self.actionVisual_Properties.triggered.connect(lambda: self.visual_properties_popup(self))                                     # Open up 'Visual Properties' window

    #DATA_TYPES_BOX
        self.rawdata_checkBox.stateChanged.connect(self.raw_visiblility)                                                 # Update raw lines visibility when raw data checkbox is changed.
        self.smootheddata_checkBox.stateChanged.connect(self.smooth_visibility)                                          # Update smooth lines visibility when smooth data checkbox is changed.
        self.rawdata_checkBox.stateChanged.connect(self.legend_visibility)                                               # Update legend visibility when raw data checkbox is changed.
        self.smootheddata_checkBox.stateChanged.connect(self.legend_visibility)                                          # Update legend visibility when smooth data checkbox is changed.
        self.meandata_checkBox.stateChanged.connect(self.mean_visibility)                                                # Update mean line visibility when mean data checkbox is changed.

    #OPTIONS_BOX
        self.legend_checkBox.stateChanged.connect(self.legend_visibility)                                                # Update legend visibility when legend checkbox is changed.
        self.gridlines_checkBox.stateChanged.connect(self.gridlines_visibility)                                          # Update gridline visibility when gridline checkbox is changed.
        self.analysis_checkBox.stateChanged.connect(self.analine_visibility)                                             # Update analysis window line visibility when window analysis checkbox is changed.

    #SMOOTH_BOX
        self.smooth_horizontalSlider.setRange(1,30)                                                                      # Set slider length (increment = 2 so (1,30) =  1,3,5,...,59
        self.smooth_horizontalSlider.valueChanged.connect(self.smooth_slider)                                            # Change smoothing window length using slider.
        self.smooth_spinBox.valueChanged.connect(lambda: self.t1_update_pushButton.setEnabled(True))                     # If smoothing spinbox changed, enable update buttons.
        self.smooth_spinBox.valueChanged.connect(lambda: self.t2_update_pushButton.setEnabled(True))                     #  "                       "                        "

    #ANNOTATIONS_BOX
     # TIME
        self.time_checkBox.stateChanged.connect(self.time_visibility)                                                    # Update vertical time line annotation visibility when time checkbox is changed.
        self.time_horizontalSlider.sliderPressed.connect(self.time_press)                                                # When time slider pressed:
        self.time_horizontalSlider.valueChanged.connect(self.time_slider)                                                # Whilst time slider changed:
        self.specifictime_timeEdit.timeChanged.connect(self.time_slider_update)                                          # When slider value changed, change timeEdit to match.
        self.time_horizontalSlider.sliderReleased.connect(self.time_release)                                             # When time slider released:
     # PEOPLE
        self.people_checkBox.stateChanged.connect(self.people_visibility)                                                # Update horizontal people line annotation visibility when time checkbox is changed.
        self.people_horizontalSlider.sliderPressed.connect(self.people_press)                                            # When time slider pressed:
        self.people_horizontalSlider.valueChanged.connect(self.people_slider)                                            # Whilst time slider changed:
        self.people_spinBox.valueChanged.connect(self.people_slider_update)                                              # When slider value changed, change timeEdit to match.
        self.people_horizontalSlider.sliderReleased.connect(self.people_release)                                         # When time slider released:

    #-----------------------------------------------------------TAB1
     # SETUP
        self.t1_specificday_dateEdit.setDateTime(QDateTime(QDateTime.currentDateTime()))                                 # Sets date_edit to today's date for initial setup.

        input = self.t1_specificday_dateEdit.dateTime().toPyDateTime().date()                                            # Sets label to today's weekday for initial setup.
        weekday = input.strftime('%a')                                                                                   #  "
        self.t1_specificweekday_label.setText(weekday)                                                                   #  "

        self.t1_update_pushButton.setEnabled(False)                                                                      # Disables update pushButton.

     # DATE_EDIT
        self.t1_specificday_dateEdit.dateChanged.connect(self.t1_date_label_change)

     # TODAY
        self.t1_today_pushButton.clicked.connect(self.today)
     # YESTERDAY
        self.t1_yesterday_pushButton.clicked.connect(self.yesterday)
     # NOTES
        self.plainTextEdit.modificationChanged.connect(self.notes_enable)
        self.t1_save_pushButton.clicked.connect(self.notes_save)
     # UPDATE_TAB1
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


    #-----------------------------------------------------------TAB2
     # SETUP
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

     # ONE_WEEK
        self.t2_oneweek_pushButton.clicked.connect(self.one_week)
     # ONE_MONTH
        self.t2_onemonth_pushButton.clicked.connect(self.one_month)
     # PAST_WEEK
        self.t2_pastweek_pushButton.clicked.connect(self.past_week)
     # PAST_MONTH
        self.t2_pastmonth_pushButton.clicked.connect(self.past_month)

     # UPDATE_TAB2
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


    #-----------------------------------------------------------TAB3
        #No functions yet

    #-----------------------------------------------------------ANALYSIS_GROUPBOX
     # ANALYSIS
        self.analysis_checkBox.stateChanged.connect(self.analine_visibility)
        self.analysis_checkBox.stateChanged.connect(self.update_bg)

     # START WINDOW
        self.start_timeEdit.setDateTime(datetime.datetime(2020,1,1,0,0,0,0))
        self.start_horizontalSlider.setRange(0,1439)
        self.start_horizontalSlider.setValue(0)
        self.start_horizontalSlider.sliderPressed.connect(self.start_press)
        self.start_horizontalSlider.valueChanged.connect(self.start_slider)
        self.start_timeEdit.timeChanged.connect(self.start_slider_update)
        self.start_horizontalSlider.sliderReleased.connect(self.start_release)

     # END WINDOW
        self.end_timeEdit.setDateTime(datetime.datetime(2020,1,1,23,59,0,0))
        self.end_horizontalSlider.setRange(0,1439)
        self.end_horizontalSlider.setValue(1439)
        self.end_horizontalSlider.sliderPressed.connect(self.end_press)
        self.end_horizontalSlider.valueChanged.connect(self.end_slider)
        self.end_timeEdit.timeChanged.connect(self.end_slider_update)
        self.end_horizontalSlider.sliderReleased.connect(self.end_release)

     # BUTTONS
        self.fullday_pushButton.clicked.connect(self.fullday)
        self.day_pushButton.clicked.connect(self.day)
        self.morning_pushButton.clicked.connect(self.morning)
        self.evening_pushButton.clicked.connect(self.evening)

     # UPDATE ANALYSIS
        self.update_analysis_pushButton.clicked.connect(self.update_analysis)

    #Timer for continuous plotting cusor_lables.......
        # self.timer = QtCore.QTimer()
        # self.timer.setInterval(1)
        # self.timer.timeout.connect(self.cusor_lables)
        # self.timer.start

#=========================================================================================================================================================================================================
        # #TREE_WIDGET
        self.treeWidgetDict = {'10-20':0,'11-20':1,'12-20':2,'01-21':3,'02-21':4,'03-21':5,'04-21':6,'05-21':7,'06-21':8,'07-21':9,'08-21':10,'09-21':11,'10-21':12,'11-21':13,'12-21':14}
        d = datetime.datetime.today().date() - datetime.timedelta(days=1)
        day = int(d.strftime('%e').lstrip('0'))
        month_year = d.strftime('%m-%y')
        self.treeWidget.setCurrentItem(self.treeWidget.invisibleRootItem().child(self.treeWidgetDict[month_year]).child(day-1))

        #TABLE_WIDGET
        self.itemchangeconnected = True
        self.table_changed_col = []
        self.table_changed_row = []

        vert_table_labels = []
        for i in range(60):
            vert_table_labels.append(str(i))

        header = self.tableWidget.horizontalHeader()
        self.tableWidget.setHorizontalHeaderLabels(
            ['00:00', '01:00', '02:00', '03:00', '04:00', '05:00', '06:00', '07:00', '08:00', '09:00', '10:00', '11:00',
             '12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00', '19:00', '20:00', '21:00', '22:00', '23:00'])
        self.tableWidget.setVerticalHeaderLabels(vert_table_labels)
        for i in range(24):
            header.setSectionResizeMode(i, QtWidgets.QHeaderView.Stretch)

        #OTHER
        self.editor_dateEdit.setDateTime(QDateTime(QDateTime.currentDateTime()))  # Sets date_edit to today's date for initial setup.
        self.editor_date_label_change()
        self.editor_progressBar.setValue(1)

        #CONNECTIONS
        self.editor_dateEdit.dateChanged.connect(self.editor_date_label_change)
        self.editor_marker_checkBox.stateChanged.connect(self.editor_markers)
        self.editor_gridlines_checkBox.stateChanged.connect(self.editor_gridlines)
        self.showtable_checkBox.stateChanged.connect(self.editor_showtable)
        self.editor_singleinterp_pushButton.clicked.connect(self.short_interp)

        self.treeWidget.itemSelectionChanged.connect(self.tree_change)
        self.tableWidget.itemChanged.connect(self.table_change)

        self.editor_load_pushButton.clicked.connect(self.load_popup)
        self.editor_reset_pushButton.clicked.connect(self.reset_popup)

        self.editor_save_pushButton.clicked.connect(self.editor_save)

        self.editor_mlupdate_pushButton.clicked.connect(self.ml_checkbox)
        self.editor_testinterp_pushButton.clicked.connect(self.interp_tests)
        self.editor_constant_pushButton.clicked.connect(self.set_constant)

        self.editor_spline_spinBox.setVisible(False)
        self.editor_comboBox.currentTextChanged.connect(self.spline_box_visibility)
        self.editor_start_timeEdit.timeChanged.connect(self.constant_starttime_changed)
        self.editor_end_timeEdit.timeChanged.connect(self.constant_endtime_changed)
        self.editor_interpolate_pushButton.clicked.connect(self.interpolate)

        #GRAPH
        ax1 = self.MplWidget1.canvas.axes
        xfmt1 = mdates.DateFormatter('%H:%M')
        ax1.xaxis.set_minor_locator(AutoMinorLocator())
        ax1.xaxis.set_major_formatter(xfmt1)
        ax1.yaxis.set_major_locator(MaxNLocator(integer=True))

        self.MplWidget1.canvas.axes.set_xticks(x_list, minor=False)
        self.MplWidget1.canvas.axes.set_xlim((datetime.datetime(2020, 1, 1, 0, 0, 0, 0), datetime.datetime(2020, 1, 1, 23, 59, 0, 0)))
        self.MplWidget1.canvas.axes.set_ylim((0, 130))
        self.MplWidget1.canvas.axes.spines['top'].set_visible(False)
        self.MplWidget1.canvas.axes.spines['right'].set_visible(False)
        self.MplWidget1.canvas.axes.set_position([0.05, 0.11, 0.92, 0.85])

        self.MplWidget1.canvas.axes.set_xlabel('Time')
        self.MplWidget1.canvas.axes.set_ylabel('Number of People')
        self.MplWidget1.canvas.axes.locator_params(axis='y', nbins= 13)

        self.MplWidget1.canvas.axes.grid(alpha=0.25)
        self.editor_gridlines()
        self.editor_load()
#=========================================================================================================================================================================================================
#======================================================================================================================#

        conn = sqlite3.connect('PG2020_SQL_CLEAN.db')
        curs = conn.cursor()
        curs.execute("PRAGMA journal_mode=WAL;")
        curs.execute("SELECT Day, ML FROM puregym_table")
        self.ml_values = curs.fetchall()
        curs.close()
        conn.close()

        for pair in self.ml_values:
            date = pair[0]
            value = pair[1]
            month_year = str(date[3:5]+'-'+date[6:8])
            day = int(date[0:2].lstrip('0'))
            try:
                child = self.treeWidget.invisibleRootItem().child(self.treeWidgetDict[month_year]).child(day-1)
                if value == 0:
                    child.setCheckState(False, Qt.Unchecked)
                else:
                    child.setCheckState(False, Qt.Checked)
            except:
                pass

        self.ml_checkbox()


    #----------------------------------------------------------WINDOWS
    def test(self):
        pass

    def help_popup(self):
        self.w = HelpWindow()
        self.w.show()

    def visual_properties_popup(self,window):
        self.w = VisualProperties(window)
        self.w.show()

    #-----------------------------------------------------------MplWidget_ARTISTS_VISIBILITY
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

    #-----------------------------------------------------------OTHER
    def cursor_toggle(self):
        tog = not self.cursor_toggle
        self.cursor = Cursor(self.MplWidget.canvas.axes, alpha=0.2, color = 'grey', vertOn=tog, horizOn=tog, linewidth = 1, useblit=True)
        self.cursor_toggle = tog

    def update_bg(self):
        self.bg = self.MplWidget.canvas.copy_from_bbox(self.MplWidget.canvas.axes.bbox)
        #print('UpdateBackground')


#===================================================TAB1===============================================================#
    def t1_date_label_change(self):
        input = self.t1_specificday_dateEdit.dateTime().toPyDateTime().date() #get date from dateEdit
        weekday = input.strftime('%a')                                        #get weekday
        self.t1_specificweekday_label.setText(weekday)                        #change label to weekday
    
    #-----------------------------------------------------------TODAY
    def today(self):
        self.t1_specificday_dateEdit.setDateTime(QDateTime(QDateTime.currentDateTime()))

    #-----------------------------------------------------------YESTERDAY
    def yesterday(self):
        now = datetime.datetime.today()
        tdelta = datetime.timedelta(days=-1)
        yesterday = now + tdelta
        self.t1_specificday_dateEdit.setDateTime(QDateTime(yesterday))

    #-----------------------------------------------------------UPDATE_SPECIFIC_DATE
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

    #-----------------------------------------------------------NOTES
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
        self.t1_specificday_dateEdit.setEnabled(True)
        self.t1_yesterday_pushButton.setEnabled(True)
        self.t1_today_pushButton.setEnabled(True)

    def notes_enable(self):
        self.t1_save_pushButton.setEnabled(True)
        self.saved_label.setVisible(False)
        self.t1_specificday_dateEdit.setEnabled(False)
        self.t1_yesterday_pushButton.setEnabled(False)
        self.t1_today_pushButton.setEnabled(False)

    def notes_save(self):
        d = self.t1_specificday_dateEdit.dateTime().toPyDateTime().date()
        var0 = d.strftime('%d/%m/%y')
        update = self.plainTextEdit.toPlainText()

        databases = ['PG2020_SQL.db','PG2020_SQL_CLEAN.db']
        for database in databases:
            conn = sqlite3.connect(database)
            curs = conn.cursor()
            curs.execute("PRAGMA journal_mode=WAL;")

            curs.execute('UPDATE puregym_table SET Comments = "{}" WHERE Day = "{}"'.format(update,var0))
            conn.commit()

            curs.close()
            conn.close()

        self.notes()

        self.t1_save_pushButton.setEnabled(False)
        self.saved_label.setVisible(True)
        self.t1_specificday_dateEdit.setEnabled(True)
        self.t1_yesterday_pushButton.setEnabled(True)
        self.t1_today_pushButton.setEnabled(True)

#======================================================================================================================#



#===================================================TAB2===============================================================#
    #-----------------------------------------------------------TAB2_LABELS/DATES
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

    #-----------------------------------------------------------TAB2_BUTTONS
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

    def days_selection(self,bool):
        self.t2_monday_checkBox.setChecked(bool)
        self.t2_tuesday_checkBox.setChecked(bool)
        self.t2_wednesday_checkBox.setChecked(bool)
        self.t2_thursday_checkBox.setChecked(bool)
        self.t2_friday_checkBox.setChecked(bool)
        self.t2_saturday_checkBox.setChecked(bool)
        self.t2_sunday_checkBox.setChecked(bool)
    #-----------------------------------------------------------UPDATE_RANGE_OF_DATES
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

#======================================================================================================================#



#===================================================TAB3===============================================================#
    #No current functions
#======================================================================================================================#



#===============================================TIME_SLIDERS===========================================================#
    #-----------------------------------------------------------SMOOTHING_LENGTH_SLIDER
    def smooth_slider(self, value):
        if True:
        #if self.people_press_toggle:
            self.smooth_spinBox.setValue((value*2)-1)
    
    #-----------------------------------------------------------TIME_SLIDER
    def time_slider(self,value):
        if self.time_press_toggle:
            #print('Slider Changed - time')
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
            #print('Datechanged - time')
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
        #print('Slider released - time')
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
        #print('Slider pressed - time line remove')
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

    #-----------------------------------------------------------PEOPLE_SLIDER
    def people_slider(self, value):
        if self.people_press_toggle:
            #print('Slider Changed - people')
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
            #print('Numbeerchanged - people')
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
        #print('Slider released - people')
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
        #print('Slider pressed - people line remove')
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

    #-----------------------------------------------------------START_WINDOW_SLIDER
    def start_slider(self, value):
        if self.start_press_toggle:
            #print('Slider Changed - start')
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
            #print('Timechanged - start')
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
        #print('Slider released - start')
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
        #print('Slider pressed - start line remove')
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

    #-----------------------------------------------------------END_WINDOW_SLIDER
    def end_slider(self, value):
        if self.end_press_toggle:
            #print('Slider Changed - end')
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
            #print('Timechanged - end')
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
        #print('Slider released - end')
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
        #print('Slider pressed - end line remove')
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

#======================================================================================================================#



#=================================================ANALYSIS=============================================================#
    #-----------------------------------------------------------ANALYSIS_WINDOW_SIZES
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

    #-----------------------------------------------------------STATS
    def cusor_lables(self):
        props = dict(boxstyle = 'square', facecolor= 'white', edgecolor = 'white')
        cur_min = 5
        cur_max = 6
        cur_mean = 7
        self.MplWidget.canvas.axes.text(0.02, 1.01, '{}:{}:{}'.format(cur_min,cur_mean,cur_max),transform=self.MplWidget.canvas.axes.transAxes, fontsize=10, color = 'grey',  verticalalignment='bottom', bbox=props)

    def max_annotation(self,max_indices):
        for time in max_indices:
            self.MplWidget.canvas.axes.plot(time, 50, marker='o',linewidth=1, color='red', alpha=0.2, visible=True)
        
    #-----------------------------------------------------------UPDATES
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
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.xaxis.set_minor_locator(AutoMinorLocator())
        ax.xaxis.set_major_formatter(xfmt)
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))                                                            # So that y-axis is integer until scale is <1
        ax.set_position([0.05, 0.06,0.92,0.9])

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

        conn = sqlite3.connect('PG2020_SQL_CLEAN.db')
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

        #---------SMOOOTH-----------------------------------------------------------
        var = self.smooth_spinBox.value()
        var2 = int(np.floor(var/2))
        yourLists = [[]] * len(myLists)
        for index0 in range(len(myLists)):
            vec = [None] * 1440

            for index1 in range(1440-var+1):
                rolling_sum = 0
                rolling_list = []

                for value in myLists[index0][index1:index1 + var]:
                    if not value == None:
                        rolling_sum += value
                        rolling_list.append(value)

                if rolling_sum == 0:
                    vec[index1 + var2] = None
                else:
                    vec[index1 + var2] = round(sum(rolling_list)/len(rolling_list), 2)

            yourLists[index0] = vec
        #---------------------------------------------------------------------------

        #for day in range(len(myLists)):
            #print(myLists[day])
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
        #print('Before lines plot: ', self.days, self.months, self.week, self.years, self.dates)
        for index in range(len(myLists)):
            #print(myLists[index])

            if not myLists[index].count(None) == len(myLists[index]):
                labels.append(self.week[index] + ' ' + str(self.dates[index]))
                #print(myLists[index].count(None),len(myLists[index]),self.dates[index])
                line1, = self.MplWidget.canvas.axes.plot(time_vec, myLists[index], linewidth=1, label=self.week[index] + ' ' + str(self.dates[index])) #visible=self.rawdata_checkBox.isChecked()
                line2, = self.MplWidget.canvas.axes.plot(time_vec, yourLists[index], linewidth=1, label=self.week[index] + ' ' + str(self.dates[index])) #visible=smootheddata_checkBox.isChecked()
                #print(self.dates[index])
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
        # self.leg = self.MplWidget.canvas.axes.legend(raw_lines,labels,loc='upper left', title='Raw Data')
        # self.leg2 = self.MplWidget.canvas.axes.legend(smooth_lines,labels,loc='upper left', bbox_to_anchor=(0.11,1) , title='Smoothed Data')
        self.leg2 = self.MplWidget.canvas.axes.legend(smooth_lines,labels,loc='upper left' , title='Smoothed Data')
        self.leg = self.MplWidget.canvas.axes.legend(raw_lines,labels,loc='upper left', bbox_to_anchor=(0.11,1), title='Raw Data')

        # self.MplWidget.canvas.axes.add_artist(self.leg) #add back removed artist
        self.MplWidget.canvas.axes.add_artist(self.leg2) #add back removed artist

        #SET BOTH VISIBLE INITIALLY
        self.legend_visibility()
        #--------------------------------------------------------------------------------------

        self.update_bg()
        #---------------------ANNOTATIONS---------------------------------
        #VERTICAL_TIME_LINE
        try:
            annotate_time = self.specifictime_timeEdit.dateTime().toPyDateTime()#.time()
            self.time_line, = self.MplWidget.canvas.axes.plot([annotate_time,annotate_time],[0, 130], linewidth=1, color='#2989e1',alpha=alpha1)
        except:
            pass

        #HORIZONTAL_PEOPLE_LINE
        try:
            annotate_people = self.people_spinBox.value()
            self.people_line, = self.MplWidget.canvas.axes.plot([datetime.datetime(2020, 1, 1, 0, 0, 0, 0), datetime.datetime(2020, 1, 1, 23, 59, 0, 0)],[annotate_people, annotate_people], linewidth=1, color='#2989e1', alpha=alpha1)
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
                lined_raw[legline_raw] = origline_raw

            for legline_raw in self.leg.get_lines():
                alpha_raw[legline_raw] = True

            for legline_smooth, origline_smooth in zip(self.leg2.get_lines(), smooth_lines):
                legline_smooth.set_picker(True)
                lined_smooth[legline_smooth] = origline_smooth

            for legline_smooth in self.leg2.get_lines():
                alpha_smooth[legline_smooth] = True

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

        print('Graph updated sucessfully...')

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

        sm = {}
        rw = {}
        comb = {}
        for legline_smooth in self.leg2.get_lines():
            sm[legline_smooth] = alpha_smooth[legline_smooth]
        for legline_raw in self.leg.get_lines():
            rw[legline_raw] = alpha_raw[legline_raw]

        for legline_smooth, legline_raw in zip(self.leg2.get_lines(), self.leg.get_lines()):
            vis_raw = lined_raw[legline_raw].get_visible()
            vis_smooth = lined_smooth[legline_smooth].get_visible()
            if (rw[legline_raw] and vis_raw) or (sm[legline_smooth] and vis_smooth):
                comb[legline_smooth] = True
            else:
                comb[legline_smooth] = False

        for legline_smooth in self.leg2.get_lines():
            if not comb[legline_smooth]:
                del comb[legline_smooth]


        self.dates1 = []
        for i in list(comb.keys()):
            if comb[i]:
                self.dates1.append(i.get_label()[4:12])

        #print('self.dates',self.dates)
        #print('self.dates1',self.dates1)

        myLists=[]
        for index0 in range(len(self.dates1)):
            myLists.append([0]*analysis_range)

        conn = sqlite3.connect('PG2020_SQL_CLEAN.db')
        curs = conn.cursor()
        curs.execute("PRAGMA journal_mode=WAL;")

        for index in range(len(self.dates1)):
            curs.execute("SELECT * FROM puregym_table WHERE Day = '{}'".format(self.dates1[index]))
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

        try:
            #MEAN
            mean_var = int(round(sum(self.mean_list) / len(self.mean_list)))
            self.mean_var_label.setText(str(mean_var))
            #MIN
            min_var = int(round(min(self.mean_list)))
            min_indices = [num2time(i)[0] for i, x in enumerate(self.mean_list) if x == min_var and x>10]
            #print('min_indices: ',min_indices)
            self.min_var_label.setText(str(min_var))
            #MAX
            max_var = int(round(max(self.mean_list)))
            max_indices = [num2time(i)[0] for i, x in enumerate(self.mean_list) if x == max_var and x>10]
            #print('max_indices: ',max_indices)                                                                                          #WRONG BECAUSE MEANLIST SHIRTER THAN 1440
            self.max_var_label.setText(str(max_var))
            #RANGE
            range_var = max_var - min_var + 1
            self.range_var_label.setText(str(range_var))
        except:
            self.mean_var_label.setText('No Data')
            self.min_var_label.setText('No Data')
            self.max_var_label.setText('No Data')
            self.range_var_label.setText('No Data')

        print('Analysis updated sucessfully...')
        #self.max_annotation(max_indices)

#======================================================================================================================#



#==============================================DATABASE_EDITOR=========================================================#
    #-----------------------------------------------------------TABLE/TREE/GRAPH
    def table_change(self):
        if self.itemchangeconnected:
            self.editor_save_pushButton.setEnabled(True)
            self.table_change = True
            column = self.tableWidget.currentColumn()
            row = self.tableWidget.currentRow()
            self.table_changed_col.append(column)
            self.table_changed_row.append(row)
            # print(self.table_changed_col,self.table_changed_row)
            self.tableWidget.item(row,column).setBackground(QtGui.QColor(225,225,0))
    
    def tree_change(self):
        pass

    def tree_popup(self):
        msg = QMessageBox()
        msg.setWindowTitle('Error loading')
        msg.setText('A day must be selected to be loaded. It cannot be today or in the future.')
        msg.setIcon(QMessageBox.Critical)
        msg.setStandardButtons(QMessageBox.Cancel)
        msg.setDefaultButton(QMessageBox.Cancel)
        showmsg = msg.exec_()

    def ml_checkbox(self):
        self.editor_progressBar.setValue(0)
        ml_checkbox_dict = {}
        ml_used = 0
        ml_total = 0
        for pair in self.ml_values:
            date = pair[0]
            value = pair[1]
            month_year = str(date[3:5].lstrip('0')+'-'+date[6:8])
            day = int(date[0:2].lstrip('0'))
            try:
                child = self.treeWidget.invisibleRootItem().child(self.treeWidgetDict[month_year]).child(day-1)
                ml_total += 1
                if child.checkState(0) == Qt.Checked:
                    ml_checkbox_dict[date] = 1
                    ml_used += 1
                else:
                    ml_checkbox_dict[date] = 0

            except:
                pass
        #print(ml_checkbox_dict)
        self.ml_lineEdit.setText(str(ml_used)+'/'+str(ml_total))
        conn = sqlite3.connect('PG2020_SQL_CLEAN.db')
        curs = conn.cursor()
        curs.execute("PRAGMA journal_mode=WAL;")
        for key in list(ml_checkbox_dict.keys()):
            #print(ml_checkbox_dict[key], key)
            curs.execute("UPDATE puregym_table SET ML = '{}' WHERE Day = '{}'".format(ml_checkbox_dict[key],key))
        conn.commit()
        curs.close()
        conn.close()
        self.editor_progressBar.setValue(1)
        print('ML date selection saved...')

    def span_select(self, xmin, xmax):
        self.tableWidget.setRangeSelected(QTableWidgetSelectionRange(0, 0, 59, 23), False)
        xmin = int(np.floor((xmin-18262)*1440))
        xmax = int(np.ceil((xmax-18262)*1440))
        xrange = xmax-xmin+1
        # print(xmin,xmax,xrange)

        cols=[]
        for i in range(xrange):
            number = i + xmin
            row = int(number % 60)
            column = int((number - row) / 60)
            cols.append(column)

        unique_cols = list(set(cols))
        dict = {}
        for col in unique_cols:
            dict[col] = []

        for i in range(xrange):
            number = i + xmin
            row = int(number % 60)
            column = int((number - row) / 60)
            dict[column].append(row)

        for i in list(dict.keys()):
            #print(dict[i])
            y1=dict[i][0]
            y2=dict[i][-1]
            self.tableWidget.setRangeSelected(QTableWidgetSelectionRange(y1,i,y2,i),True)
    
    #-----------------------------------------------------------OPTIONS
    def editor_date_label_change(self):
        input = self.editor_dateEdit.dateTime().toPyDateTime().date()
        weekday = input.strftime('%a')
        self.editor_weekday_label.setText(weekday)

    def editor_gridlines(self):
        if self.editor_gridlines_checkBox.isChecked():
            self.MplWidget1.canvas.axes.grid(True)
        else:
            self.MplWidget1.canvas.axes.grid(False)
        self.MplWidget1.canvas.draw()

    def editor_showtable(self):
        if self.showtable_checkBox.isChecked():
            self.MplWidget1.canvas.axes.set_position([0.05, 0.11, 0.92, 0.85])
            self.tableWidget.setMaximumHeight(470)
            self.tableWidget.setMinimumHeight(470)
        else:
            self.MplWidget1.canvas.axes.set_position([0.05, 0.06, 0.92, 0.9])
            self.tableWidget.setMaximumHeight(20)
            self.tableWidget.setMinimumHeight(20)

    def editor_markers(self):
        if self.editor_marker_checkBox.isChecked():
            if editor_alpha[self.leg3.get_lines()[0]]:
                self.dline1.set_visible(False)
                self.dline3.set_visible(True)
            else:
                self.dline1.set_visible(False)
                self.dline3.set_visible(False)
    
            if editor_alpha[self.leg3.get_lines()[1]]:
                self.dline2.set_visible(False)
                self.dline4.set_visible(True)
            else:
                self.dline2.set_visible(False)
                self.dline4.set_visible(False)
        else:
            if editor_alpha[self.leg3.get_lines()[0]]:
                self.dline1.set_visible(True)
                self.dline3.set_visible(False)
            else:
                self.dline1.set_visible(False)
                self.dline3.set_visible(False)
    
            if editor_alpha[self.leg3.get_lines()[1]]:
                self.dline2.set_visible(True)
                self.dline4.set_visible(False)
            else:
                self.dline2.set_visible(False)
                self.dline4.set_visible(False)
    
        self.MplWidget1.canvas.draw()

    #-----------------------------------------------------------LOAD
    def editor_load(self):
        self.itemchangeconnected = False
        selected = self.treeWidget.selectedItems()
        #if selected:
        basenode = selected[0]
        childnode = basenode.text(0)
        if not childnode[-4:-2] == '20':
            self.datestr = childnode[-8:]
            y = int('20' + self.datestr[-2:])
            m = int(self.datestr[-5:-3].lstrip('0'))
            d = int(self.datestr[-8:-6].lstrip('0'))
            # print(self.datestr, y, m, d)
            selected_datetime = datetime.datetime(y,m,d,23,59,59,0)
            current_datetime = datetime.datetime.today()

            if selected_datetime >= current_datetime:
                self.tree_popup()
            else:
                self.editor_dateEdit.setDateTime(datetime.datetime(y, m, d, 0, 0, 0, 0))
            # try:
            #     selected = self.treeWidget.selectedItems()
            #     if selected:
            #         basenode = selected[0]
            #         childnode = basenode.text(0)
            #         if not childnode[-4:-2] == '20':
            #             self.datestr = childnode[-8:]
            #             y = int('20' + self.datestr[-2:])
            #             m = int(self.datestr[-5:-3].lstrip('0'))
            #             d = int(self.datestr[-8:-6].lstrip('0'))
            #             print(self.datestr, y, m, d)
            #             self.editor_dateEdit.setDateTime(datetime.datetime(y, m, d, 0, 0, 0, 0))
            # except:
            #     print('Error in tree item selection')

                databases = ['PG2020_SQL.db', 'PG2020_SQL_CLEAN.db']
                # global raw_data, clean_data
                self.clean_data = [None] * 1440
                self.raw_data = [None] * 1440
                output_vectors = [self.raw_data, self.clean_data]
                input = self.editor_dateEdit.dateTime().toPyDateTime().date()
                self.var0 = input.strftime('%d/%m/%y')
                weekday = input.strftime('%a')
                none_tally = {'PG2020_SQL.db': 0, 'PG2020_SQL_CLEAN.db': 0}
                for database, output in zip(databases, output_vectors):
                    conn = sqlite3.connect(database)
                    curs = conn.cursor()
                    curs.execute("PRAGMA journal_mode=WAL;")
                    curs.execute("SELECT * FROM puregym_table WHERE Day = '{}'".format(self.var0))

                    values = curs.fetchall()
                    for index1 in range(1440):
                        entry = values[0][index1 + 1]
                        output[index1] = entry
                        col = int((index1 - index1 % 60) / 60)
                        row = int(index1 % 60)
                        if entry is None:
                            none_tally[database] += 1
                        if database == 'PG2020_SQL_CLEAN.db':
                            self.tableWidget.setItem(row, col, QTableWidgetItem(str(entry)))

                    curs.close()
                    conn.close()

                global editor_alpha, editor_lined, editor_lines, editor_markerlined
                editor_lined = {}
                editor_alpha = {}
                editor_lines = []
                editor_markerlined = {}

                try:
                    self.dline1.remove()
                    self.dline2.remove()
                    self.dline3.remove()
                    self.dline4.remove()
                except:
                    # Removes lines if there are some already plotted.
                    pass

                self.dline1, = self.MplWidget1.canvas.axes.plot(time_vec, self.clean_data, linewidth=1, color='#3bfb00',
                                                                label='Clean Data')
                self.dline2, = self.MplWidget1.canvas.axes.plot(time_vec, self.raw_data, linewidth=1, color='#e51a1a',
                                                                label='Raw Data')
                editor_lines.append(self.dline1)
                editor_lines.append(self.dline2)

                # -------------------LEGEND_PICKING-------------------------------------------------
                self.leg3 = self.MplWidget1.canvas.axes.legend(loc='upper left', title=weekday + ' ' + self.var0)
                try:
                    for editor_legline, editor_origline in zip(self.leg3.get_lines(), editor_lines):
                        editor_legline.set_picker(True)
                        editor_lined[editor_legline] = editor_origline

                    for editor_legline in self.leg3.get_lines():
                        editor_alpha[editor_legline] = True
                except:
                    # There are no lines/legends (no data).
                    pass

                self.dline3, = self.MplWidget1.canvas.axes.plot(time_vec, self.clean_data, linewidth=1, marker='.', markersize=5,
                                                                color='#3bfb00', label='Clean Data',
                                                                visible=self.editor_marker_checkBox.isChecked())
                self.dline4, = self.MplWidget1.canvas.axes.plot(time_vec, self.raw_data, linewidth=1, marker='.', markersize=5,
                                                                color='#e51a1a', label='Raw Data',
                                                                visible=self.editor_marker_checkBox.isChecked())

                # MARKER_LINES
                # editor_markers(self,time_vec)
                for editor_legline, editor_marker_line in zip(self.leg3.get_lines(), self.MplWidget1.canvas.axes.get_lines()[4:6]):
                    editor_markerlined[editor_legline] = editor_marker_line

                # GRIDLINES
                self.editor_gridlines()
                # NONE_COUNT
                self.none_lineEdit.setText(str(none_tally['PG2020_SQL.db']))
                self.none_lineEdit_2.setText(str(none_tally['PG2020_SQL_CLEAN.db']))

                #self.editor_reset_pushButton.setEnabled(True)
                if none_tally['PG2020_SQL.db'] == none_tally['PG2020_SQL_CLEAN.db']:
                    self.editor_reset_pushButton.setEnabled(False)
                else:
                    self.editor_reset_pushButton.setEnabled(True)

                self.MplWidget1.canvas.draw()

                self.editor_save_pushButton.setEnabled(False)
                self.table_change = False
        else:
            self.tree_popup()

        self.table_changed_col = []
        self.table_changed_row = []
        self.itemchangeconnected = True
        print('Table and graph loaded...')

    def load_popup(self):
        if self.table_change:
            msg = QMessageBox()
            msg.setWindowTitle('Save warning')
            msg.setText('Changes have been made to the table which will be lost. Do you want to continue?')
            msg.setIcon(QMessageBox.Warning)
            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            msg.setDefaultButton(QMessageBox.Cancel)
            msg.buttonClicked.connect(self.load_popup_okay)
            showmsg = msg.exec_()
        else:
            self.editor_load()

    def load_popup_okay(self, button):
        if button.text() == 'OK':
            self.editor_load()

    #-----------------------------------------------------------RESET
    def editor_reset(self):
        self.table_changed_col = []
        self.table_changed_row = []
        self.itemchangeconnected = False
        self.clean_data = [None] * 1440
        input = self.editor_dateEdit.dateTime().toPyDateTime().date()
        var0 = input.strftime('%d/%m/%y')
        # weekday = input.strftime('%a')
    
        conn = sqlite3.connect('PG2020_SQL.db')
        curs = conn.cursor()
        curs.execute("PRAGMA journal_mode=WAL;")
        curs.execute("SELECT * FROM puregym_table WHERE Day = '{}'".format(var0))
    
        values = curs.fetchall()
        for index1 in range(1440):
            entry = values[0][index1 + 1]
            self.clean_data[index1] = entry
            col = int((index1 - index1 % 60) / 60)
            row = int(index1 % 60)
            self.tableWidget.setItem(row, col, QTableWidgetItem(str(entry)))
    
        curs.close()
        conn.close()

        print('Table reset...')

        self.itemchangeconnected = False
        self.table_change = False
        self.editor_save_pushButton.setEnabled(False)
        self.editor_progressBar.setValue(0)

        table_list = []  # get list of all values (changed) in table
        for i in range(24):
            for j in range(60):
                cell = self.tableWidget.item(j, i).text()
                if cell == 'None':
                    table_list.append(None)
                else:
                    table_list.append(int(cell))

        # print(table_list)

        conn_write = sqlite3.connect('PG2020_SQL_CLEAN.db')
        curs_write = conn_write.cursor()
        curs_write.execute("PRAGMA journal_mode=WAL;")

        for num in range(1440):
            if table_list[num] is None:
                curs_write.execute("UPDATE puregym_table SET t{} = NULL WHERE Day = '{}'".format(num + 1, var0))
            else:
                curs_write.execute(
                    "UPDATE puregym_table SET t{} = {} WHERE Day = '{}'".format(num + 1, table_list[num], var0))
            conn_write.commit()

        curs_write.close()
        conn_write.close()

        self.table_changed_col = []
        self.table_changed_row = []
        self.editor_load()
        self.editor_progressBar.setValue(1)
        self.itemchangeconnected = True
        print('Table saved...')

    def reset_popup(self):
        msg = QMessageBox()
        msg.setWindowTitle('Reset warning')
        msg.setText(
            'This will reset the clean data for the currently selected day back to its raw data. Do you want to continue?')
        msg.setIcon(QMessageBox.Warning)
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msg.setDefaultButton(QMessageBox.Cancel)
        msg.buttonClicked.connect(self.reset_popup_okay)
        showmsg = msg.exec_()
    
    def reset_popup_okay(self, button):
        if button.text() == 'OK':
            self.editor_reset()

    #-----------------------------------------------------------SAVE
    def editor_save(self):
        self.itemchangeconnected = False
        self.table_change = False
        self.editor_save_pushButton.setEnabled(False)
        self.editor_progressBar.setValue(0)

        table_list = []                                                     #get list of all values (changed) in table
        # for i in range(24):
        #     for j in range(60):
        #         cell = self.tableWidget.item(j, i).text()
        #         if cell == 'None':
        #             table_list.append(None)
        #         else:
        #             table_list.append(int(cell))

        for i, j in zip(self.table_changed_col,self.table_changed_row):
            self.tableWidget.item(j, i).setBackground(QtGui.QColor(225, 225, 225))
            cell = self.tableWidget.item(j, i).text()
            print(cell)
            if cell == 'None':
                table_list.append(None)
            else:
                table_list.append(int(cell))

        #print(table_list)
    
        input = self.editor_dateEdit.dateTime().toPyDateTime().date()
        var0 = input.strftime('%d/%m/%y')
    
        conn_write = sqlite3.connect('PG2020_SQL_CLEAN.db')
        curs_write = conn_write.cursor()
        curs_write.execute("PRAGMA journal_mode=WAL;")
    
        # for num in range(1440):
        #     self.editor_progressBar.setValue(num / 1440)
        #     QApplication.processEvents()  # doesn't work
        #     print(num)
        #     if table_list[num] is None:
        #         curs_write.execute("UPDATE puregym_table SET t{} = NULL WHERE Day = '{}'".format(num + 1, var0))
        #     else:
        #         curs_write.execute(
        #             "UPDATE puregym_table SET t{} = {} WHERE Day = '{}'".format(num + 1, table_list[num], var0))
        #     conn_write.commit()

        for num in range(len(table_list)):
            tposition = (self.table_changed_col[num]*60)+self.table_changed_row[num]+1
            print('num: ',num)
            print('tposition: ',tposition)
            if table_list[num] is None:
                curs_write.execute("UPDATE puregym_table SET t{} = NULL WHERE Day = '{}'".format(tposition, var0))
            else:
                curs_write.execute(
                    "UPDATE puregym_table SET t{} = {} WHERE Day = '{}'".format(tposition, table_list[num], var0))
            conn_write.commit()

        curs_write.close()
        conn_write.close()

        self.table_changed_col = []
        self.table_changed_row = []
        self.editor_load()
        self.editor_progressBar.setValue(1)
        self.itemchangeconnected = True
        print('Table saved...')

    #-----------------------------------------------------------INTERPOLATION
    def short_interp(self):
        self.editor_progressBar.setValue(0)
        self.itemchangeconnected = False

        self.table_changed_col = []
        self.table_changed_row = []

        #SINGLE GAP INTERP
        for i in range(1438):
            if self.clean_data[i + 1] is None:
                if not self.clean_data[i] is None:
                     if not self.clean_data[i+2] is None:
                         self.clean_data[i+1] = int(np.ceil((self.clean_data[i]+self.clean_data[i+2])/2))
                         row = int((i + 1) % 60)
                         column = int(((i+1)-row)/60)
                         self.table_changed_col.append(column)
                         self.table_changed_row.append(row)

        #SAVE TO TABLE
        for i,j in zip(self.table_changed_col,self.table_changed_row):
            index1 = (i*60)+j
            print(i,j,index1,str(self.clean_data[index1]))
            self.tableWidget.setItem(j,i,QTableWidgetItem(str(self.clean_data[index1])))
            self.tableWidget.item(j,i).setBackground(QtGui.QColor(225,225,0))
        # for index1 in range(1440):
        #     col = int((index1 - index1 % 60) / 60)
        #     row = int(index1 % 60)
        #     print(self.clean_data[index1])
        #     self.tableWidget.setItem(row, col, QTableWidgetItem(str(self.clean_data[index1])))

        #self.table_change = False
        self.editor_save_pushButton.setEnabled(True)
        self.editor_progressBar.setValue(1)
        self.itemchangeconnected = True
        print('Table saved...')

    def interp_tests(self):
        # ===SINGLE DAY INTERPOLATION TEST===#
        self.editor_progressBar.setValue(0)

        time_vec_strf = []
        for i in range(1440):
            tdelta = datetime.timedelta(minutes=i)
            dt = (datetime.datetime(2020, 1, 1, 0, 0, 0, 0) + tdelta).time()
            t = dt.strftime('%H:%M')
            time_vec_strf.append(t)

        conn = sqlite3.connect('PG2020_SQL_CLEAN.db')
        curs = conn.cursor()
        curs.execute("PRAGMA journal_mode=WAL;")

        num_vec = [None] * 1440
        curs.execute("SELECT * FROM puregym_table WHERE Day = '{}'".format(self.var0))
        values = curs.fetchall()

        for index1 in range(1440):
            entry = values[0][index1 + 1]
            num_vec[index1] = entry

        curs.close()
        conn.close()

        dict = {'Time': time_vec_strf, 'Number': num_vec}
        df0 = pd.DataFrame(dict)

        # num_vec[200:300] = [None] * 100
        # num_vec[700:800] = [None] * 100
        # num_vec[1100:1200] = [None] * 100
        df1 = pd.DataFrame(dict)

        df2 = df1.interpolate().round(decimals=0)
        #SPLINE
        df3 = df1.interpolate(method='spline', order=1).round(decimals=0)
        df4 = df1.interpolate(method='spline', order=2).round(decimals=0)
        df5 = df1.interpolate(method='spline', order=3).round(decimals=0)
        df6 = df1.interpolate(method='spline', order=4).round(decimals=0)
        df7 = df1.interpolate(method='spline', order=5).round(decimals=0)
        #POLY
        df8 = df1.interpolate(method='polynomial', order=1).round(decimals=0)
        df9 = df1.interpolate(method='polynomial', order=3).round(decimals=0)
        #OTHER
        #df10 = df1.interpolate(method='nearest').round(decimals=0)
        df11 = df1.interpolate(method='slinear').round(decimals=0)
        df12 = df1.interpolate(method='quadratic').round(decimals=0)
        df13 = df1.interpolate(method='cubic').round(decimals=0)
        # df14 = df1.interpolate(method='barycentric').round(decimals=0)
        # df15 = df1.interpolate(method='time').round(decimals=0)
        #RANDOM
        df16 = df1.interpolate(method='krogh').round(decimals=0)
        df17 = df1.interpolate(method='piecewise_polynomial').round(decimals=0)
        df18 = df1.interpolate(method='pchip').round(decimals=0)
        df19 = df1.interpolate(method='akima').round(decimals=0)
        df20 = df1.interpolate(method='cubicspline').round(decimals=0)
        self.editor_progressBar.setValue(1)

        fig, ax = plt.subplots(nrows = 1, ncols = 2, sharex=True, sharey=True)
        #fig.suptitle('Interpolation Tests')
        figmanager = plt.get_current_fig_manager()
        figmanager.window.showMaximized()
        fig.canvas.set_window_title('Interpolation Tests Figure')
        for axis in ax.flat:
            axis.set(xlabel='Time',ylabel='Number of People')
            axis.set_ylim([0,130])
            axis.set_xlim([0, 1439])

        df11.plot(ax=ax[0], color='black') #slinear
        df3.plot(ax=ax[0],color='#68a6d5') #spl1
        df4.plot(ax=ax[0],color='#28c361') #spl2
        df5.plot(ax=ax[0],color='#f6cb16') #spl3
        df6.plot(ax=ax[0],color='#e73f22') #spl4
        df7.plot(ax=ax[0],color='#ff6700') #spl5
        df0.plot(ax=ax[0],color='#e7e7e7') #raw
        # df1.plot(ax=ax[0][0], color='grey')

        df12.plot(ax=ax[1],color='#68a6d5') #quad
        df13.plot(ax=ax[1],color='#28c361') #cubic
        df16.plot(ax=ax[1], color='#e73f22') #krogh
        df17.plot(ax=ax[1], color='#ff6700') #piecewisepoly
        df18.plot(ax=ax[1], color='purple') #pchip
        df19.plot(ax=ax[1], color='#f6cb16') #akima
        df0.plot(ax=ax[1],color='#e7e7e7') #raw
        # df1.plot(ax=ax[0][1], color='grey')
        # df14.plot(ax=ax[1]) #barycentric
        # df15.plot(ax=ax[1]) #time
        #df20.plot(ax=ax[1], color='black') #cubicspline

        ax[0].legend(['Slinear','Spline1','Spline2','Spline3','Spline4','Spline5','Raw'])
        ax[1].legend(['Quadratic', 'Cubic','Krogh', 'PiecewisePoly', 'Pchip','Akima','Raw'])

        plt.show()

    def interpolate(self, method):
        self.itemchangeconnected = False
        method_dict = {'Linear':'linear','Spline':'spline','Quadratic':'quadratic','Cubic':'cubic','Krogh':'krogh','Piecewise-Poly':'piecewise_polynomial','Pchip':'pchip','Akima':'akima'}
        self.editor_progressBar.setValue(0)

        time_vec_strf = []
        for i in range(1440):
            tdelta = datetime.timedelta(minutes=i)
            dt = (datetime.datetime(2020, 1, 1, 0, 0, 0, 0) + tdelta).time()
            t = dt.strftime('%H:%M')
            time_vec_strf.append(t)

        conn = sqlite3.connect('PG2020_SQL_CLEAN.db')
        curs = conn.cursor()
        curs.execute("PRAGMA journal_mode=WAL;")

        num_vec = [None] * 1440
        curs.execute("SELECT * FROM puregym_table WHERE Day = '{}'".format(self.var0))
        values = curs.fetchall()

        for index1 in range(1440):
            entry = values[0][index1 + 1]
            num_vec[index1] = entry

        curs.close()
        conn.close()

        dict = {'Time': time_vec_strf, 'Number': num_vec}
        df1 = pd.DataFrame(dict)
        print(df1)
        print(self.editor_comboBox.currentText())
        if self.editor_comboBox.currentText() == 'Spline':
            print('Spline')
            df1 = df1.interpolate(method='spline',order=int(self.editor_spline_spinBox.value())).round(decimals=0)
        else:
            print('Other')
            print(self.editor_comboBox.currentText())
            df1 = df1.interpolate(method=method_dict[self.editor_comboBox.currentText()]).round(decimals=0)

        #SEE INTERPOLATED GRAPH
        # df1.plot()
        # plt.show()

        for index, row in df1.iterrows():
            j = int(index%60)
            i = int((index - j)/60)
            self.table_changed_row.append(j) #Adds all cell rows and columns to changed... compare before and after and see which index is different?
            self.table_changed_col.append(i)
            self.tableWidget.setItem(j, i, QTableWidgetItem(str(int(row['Number']))))

        # for i, j in zip(self.table_changed_row,self.table_changed_col):                                                  # DOES NOT WORK CHANGES ALL CELLS
        #     self.tableWidget.item(j, i).setBackground(QtGui.QColor(225, 225, 0))
        print(self.table_changed_col)
        self.itemchangeconnected = True
        self.editor_save_pushButton.setEnabled(True)

    def spline_box_visibility(self,value):
        if value == 'Spline':
            self.editor_spline_spinBox.setVisible(True)
        else:
            self.editor_spline_spinBox.setVisible(False)

    #-----------------------------------------------------------SET CONSTANT
    def set_constant(self):
        self.itemchangeconnected = False
        start_index = time2num(self.editor_start_timeEdit.dateTime().toPyDateTime().time())
        end_index = time2num(self.editor_end_timeEdit.dateTime().toPyDateTime().time())
        print(start_index,end_index)

        xmin = start_index[0]
        xmax = end_index[0]
        xrange = xmax - xmin + 1
        print(xmin, xmax, xrange)

        cols = []
        for i in range(xrange):
            number = i + xmin
            row = int(number % 60)
            column = int((number - row) / 60)
            cols.append(column)

        unique_cols = list(set(cols))
        dict = {}
        for col in unique_cols:
            dict[col] = []

        for i in range(xrange):
            number = i + xmin
            row = int(number % 60)
            column = int((number - row) / 60)
            dict[column].append(row)

        for i in list(dict.keys()):
            for j in dict[i]:
                self.tableWidget.setItem(j, i, QTableWidgetItem(str(self.editor_constant_spinBox.value())))
                self.tableWidget.item(j, i).setBackground(QtGui.QColor(225, 225, 0))

        self.itemchangeconnected = True

    def constant_starttime_changed(self):                                                                                # If start time changed and bigger than end time, change end time to match
        if self.editor_start_timeEdit.dateTime().toPyDateTime().time() > self.editor_end_timeEdit.dateTime().toPyDateTime().time():
            self.editor_end_timeEdit.setDateTime(self.editor_start_timeEdit.dateTime().toPyDateTime())                                                                             #                                                                             #

    def constant_endtime_changed(self):                                                                                  # If end time changed and smaller than start time, change start time to match
        if self.editor_start_timeEdit.dateTime().toPyDateTime().time() > self.editor_end_timeEdit.dateTime().toPyDateTime().time():
            self.editor_start_timeEdit.setDateTime(self.editor_end_timeEdit.dateTime().toPyDateTime())

#======================================================================================================================#

#-------------DRIVER_CODE-----------------#|
#def main():                              #|
app = QApplication([])                    #|
app.setStyle('Fusion')                    #|
window = MatplotlibWidget()               #|
window.show()                             #|
window.today()                            #|
window.update_specific_date()             #|
app.exec_()                               #|
                                          #|
#if __name__ == '__main__':               #|
   #main()                                #|
#-----------------------------------------#|
