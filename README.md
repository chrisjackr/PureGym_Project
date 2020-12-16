# PureGym_Project

> PureGym data acquisition and analysis.

## =================PureGymAnalysis[v1.01]=================

### ___UPDATES___

### ___FEATURES___

#### DATA TYPES:

 * Raw Data - display the raw data
 * Smoothed Data  - display the data averaged over a 15minute window
 * Mean Data - display the average line of the raw data



#### OPTIONS:

 * Gridlines - turn on/off gridlines
 * Legend - turn on/off legend
 * Analysis Window - display vertical lines at the start and end of the analysis window



#### ANNOTATIONS:

 * Time - display a vertical line at a specified time



#### SPECIFIC DAYS:

Select a single day to display.
 * Yesterday - set date to yesterday
 * Today - set date to today

Notes can be added to the selected day using the plain text editor.
When a day is loaded, its corresponding notes are displayed in the text editor.
If the notes are altered, the new notes can be saved.
 * Save - save altered notes

 * Update (press enter) - displays the selected day



#### SELECT DAYS:

Select a range of days to display.
Days can be filtered using the weekday checkboxes.

 * Start - select the start of the date range
 * End - select the end of the date range

 * Past week - sets the start and end dates to the previous 7 days
 * Past month - sets the start and end dates to the previous 28 days
 * +1 week - sets end date 7 days after end date
 * +1 month - sets end date 28 days after start date

 * Update (press enter) - displays the selected range of days



#### CALENDAR:
Work in progress



#### ANALYSIS:

The analysis window specifices the range of times between which some basic quantities are calclulated.
The start time cannot be after the end time.

 * Start - selects the start time of the analysis window
 * End - selects the end time of the analysis window

 * FullDay - sets (start,end) = (00:00,23:59)
 * Day - sets (start,end) = (04:30,23:30)
 * Morning - sets (start,end) = (04:30,09:00)
 * Evening - sets (start,end) = (16:00,21:00)
