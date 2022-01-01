# SET-UP OPTIONS 

import datetime
from PyQt5.QtCore import *

#=== YEAR TO SHOW ===#
YEAR = 2022
MONTH = 12
DAY = 15
TODAY = True

if TODAY:
    YEAR = int(datetime.datetime.today().strftime('%Y'))
    TAB1 = QDateTime.currentDateTime()
    TAB2_START = QDateTime.currentDateTime()
    TAB2_END = QDateTime.currentDateTime()
    EDITOR_DATE = datetime.datetime.today().date() - datetime.timedelta(days=1) #(-1 DAY == YESTERDAY so full day of data)
else:
    if datetime.datetime(YEAR,MONTH,DAY) > datetime.datetime.today():
        MONTH = 1
        YEAR -= 1
    TAB1 = datetime.datetime(YEAR,MONTH,DAY) 
    TAB2_START = datetime.datetime(YEAR,MONTH,1) 
    TAB2_END = datetime.datetime(YEAR,MONTH,7) 
    EDITOR_DATE = datetime.datetime(YEAR,MONTH,DAY) 


#===TREE_WIDGET===#
months = [str(x+1).zfill(2) for x in range(MONTH)]
months_years = []

for m in months:
    months_years.append(m+'-'+str(YEAR)[2:4])
index = [x for x in range(len(months))]
TREE_DICT = dict(zip(months_years,index))


if __name__ == "__main__":
    print(TREE_DICT)
    print(int(datetime.datetime.today().strftime('%Y')))