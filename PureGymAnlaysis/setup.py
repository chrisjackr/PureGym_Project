# SET-UP OPTIONS 

import datetime
from PyQt5.QtCore import *


#===TAB1===#
TAB1 = datetime.datetime(2020,12,15) #QDateTime.currentDateTime()

#===TAB2===#
TAB2_START = datetime.datetime(2020,12,15) #QDateTime.currentDateTime()
TAB2_END = datetime.datetime(2020,12,21) #QDateTime.currentDateTime()

#===EDITOR===#
EDITOR_DATE = datetime.datetime(2020,12,15) #datetime.datetime.today().date() - datetime.timedelta(days=1) #(-1 DAY == YESTERDAY so full day of data)
