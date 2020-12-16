# PureGym_Project

> **Abstract:** The PureGym project contains tools for acquisition, visualisation and analysis of gym attendance data.

## Current Version: PureGymAnalysis[v1.01]
### _BUG FIXES_
#### [v1.01]
- Fixed ability to plot multiple analysis window lines by removing need to update plot manually.
- Window screen size is now dynamic to accomodate different screen sizes:
  - added a scroll bar to left hand menu.
  - graph widget now expands to maximise its size.
- Style set to 'Fusion' so as to avoid label/button sizing problems for different operating systems.
- Fixed inability to keep zoomed-in frame whilst also changing lines being viewed.

---

### _UPDATES_
#### [v1.01]

Annotations:  
- Number line: plot horizontal line for a constant number of people.
- Time annotation toggle: 
  - Time line can be toggled using checkbox without updating.
  - Interactive animated movement with sliers.
- Number annotation toggle: 
  -	Number line can be toggled using checkbox without updating.
  - Interactive animated movement with sliers.
  
Legend: 
- Split legend into smooth/raw so legend picking can be done.
- Legend picking - turn on & off lines using by clicking on corresponding legend line.
- Legends can be toggled using checkbox without updating.

Gridlines:
- Gridlines can be toggled using checkbox without updating.

Plot Lines: 
- Ability to toggle smooth, raw and mean lines using checkboxes without updating.
  
Time annotaion toggle: 
- Time line can be toggled using checkbox without updating.
- Interactive animated movement with sliers.

Number annotation toggle: 
- Number line can be toggled using checkbox without updating.
- Interactive animated movement with sliders.

Analysis window Toggle: 
- Analysis window can be toggled using checkbox without updating.
- Interactive animated movement with sliders.

Weekday toggle: 
- Can toggle lines in plot/legend using tab2 weekday checkboxes.
- Added 'Select All' and 'Deselect All' buttons for the weekday checkboxes.

---

### _FEATURES_
#### DATA TYPES:

 * Raw Data - display the raw data
 * Smoothed Data  - display the data averaged over a 15minute window
 * Mean Data - display the average line of the raw data



#### OPTIONS:

 * Gridlines - turn on/off gridlines
 * Legend - turn on/off legend
 * Analysis Window - display vertical lines at the start and end of the analysis window



#### ANNOTATIONS:

 * Time - display a vertical line at a specified time on the x-axis
 * People - display a horizontal line at a constant number of people on the y-axis



#### SPECIFIC DAY:

Select a single day to display:
 * Yesterday - set date to yesterday
 * Today - set date to today
 * Update (press enter) - displays the selected day

Notes can be added to the selected day using the plain text editor.
When a day is loaded, its corresponding notes are displayed in the text editor.
If the notes are altered, the new notes can be saved.
 * Save - save altered notes




#### SELECT DAYS:

Select a range of days to display:
Days can be filtered using the weekday checkboxes.

 * Start - select the start of the date range
 * End - select the end of the date range

 * Past week - sets the start and end dates to the previous 7 days
 * Past month - sets the start and end dates to the previous 28 days
 * +1 week - sets end date 7 days after end date
 * +1 month - sets end date 28 days after start date
 
 * Select All - select all check boxes
 * Deselect All - unselect all check boxes

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
 
 * Update Analysis - updates the calculated quantities if the analysis window has been changed.
 
---
