# PureGym_webscraper.py

# This script runs 24/7 to parse the website for gym numbers and saves them to the SQL DATABASE.
# Email address and pin must be added.
# A new database can be made if a gym other than Bishop's Court Exeter is being recorded.

###------------------IMPORTS-------------------###
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from pathlib import Path

#from openpyxl import Workbook, load_workbook
import sqlite3
import pyautogui

import time
import datetime
#import shutil
import os

#========================================================NEW_TABLE===================================================#
# ###--------------CREATE_TABLE------------------###
# conn = sqlite3.connect('PG2020_SQL.db_TABLENAME')
# c = conn.cursor()
#
# strvar = 'Day TEXT PRIMARY KEY, '
# for i in range(1439):
#     strvar = strvar + 't'+str(i+1)+' INTEGER, '
# strvar = strvar + 't1440 INTEGER'
# #print("CREATE TABLE test_table ({})".format(strvar))
#
# c.execute("CREATE TABLE test_table ({})".format(strvar))
# conn.commit()
#
# ###-----CREATE&INSERT NULL ROW--------------###
# numdays = 365
# date_list = [datetime.datetime(2020,10,1,0,0,0,0) + datetime.timedelta(days=x) for x in range(numdays)]
# date_list1 = ['{}/{}/{}'.format(d.strftime('%d'),d.strftime('%m'),d.strftime('%y')) for d in date_list] #dates from 01/10/20 to 30/09/21
# #print(date_list1)
#
# for j in range(numdays):
#     #strrow = "'01/11/20', "
#     strrow = "'{}', ".format(date_list1[j])
#     for i in range(1439):
#         strrow = strrow + 'NULL, '
#     strrow = strrow + 'NULL'
#     c.execute("INSERT INTO test_table VALUES ({})".format(strrow))
# conn.commit()
#
# ###---ADD COMMENTS COLUMN---###
# c.execute("ALTER TABLE test_table ADD Comments TEXT")
# conn.commit()
#====================================================================================================================#


#---------------------WEBSCRAPE------------------#
try:
    # PATH = "C:\Program Files (x86)\chromedriver.exe"
    #PATH = r"C:\Users\Owner\.wdm\drivers\chromedriver\win32\87.0.4280.20\chromedriver.exe"
    PATH = r"C:\Users\Owner\.wdm\drivers\chromedriver\win32\87.0.4280.88\chromedriver.exe"
    driver = webdriver.Chrome(PATH)
except:
    driver = webdriver.Chrome(ChromeDriverManager().install())
    print('NEW DRIVER CHANGE PATH')

driver.get('https://www.puregym.com/members/')
time.sleep(2.5)

#-----------ACCEPT COOKIES-------------#
try:
    accept = driver.find_element_by_class_name("coi-banner__accept")
    accept.click()
    time.sleep(2.5)
except:
    pass
#--------------------------------------#

#---------------LOGIN------------------#
try:
    email = driver.find_element_by_id("email")
    pin = driver.find_element_by_id("pin")
except:
    try:
        email = driver.find_element_by_name("username")
        pin = driver.find_element_by_name("password")
    except:
        print('Could not enter login details.')
        quit()

email.send_keys("email@hotmail.co.uk")                                             #!!!_ADD_EMAIL_ADDRESS_!!!#
pin.send_keys("8-digit-pin")                                                       #!!!_ADD_PIN_NUMBER_!!!#
pin.send_keys(Keys.ENTER)
#---------------------------------------#

#--------Driver 1 New tab--------------#
# Cannot seem to switch gym on website.
#--------------------------------------#

time.sleep(5)
driver.set_window_rect(527,974,953,520)
driver.minimize_window()

fails = 0

beg = datetime.datetime.today()
secs = int(beg.strftime('%S'))
if secs>10:
    time.sleep(61-secs)

while True:

    try:
        #-------------------REFRESH PAGE---------------------#
        start = time.time()
        #print('\n')
        #print('Start time: ',datetime.datetime.today().time())
        #print('Start refresh: ',datetime.datetime.today().time())
        driver.set_page_load_timeout(10)  # 15
        driver.refresh()
        # driver.set_page_load_timeout(25) #15
        # time.sleep(25.1) #15
        # print('Refresh done')
        search = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "equal-height"	))
        ) #15
        #print('End search: ', datetime.datetime.today().time())
        #----------------------------------------------------#

        #---------------SAVE NUMBER OF PEOPLE TO SQL DATABASE-------------#
        output = search.text				# whole string from webpage
        output1 = output[29:32].strip()		# pick number & remove blank spaces
        output2 = int(output1)				# integer value of people in gym

        now = datetime.datetime.today()
        t = now.time()
        d = now.date()

        minute = int(t.strftime('%M'))
        hour = int(t.strftime('%H'))
        second = int(t.strftime('%S'))
        day = d.strftime('%d')
        month = d.strftime('%m')
        year =  d.strftime('%y')

        num = int((hour * 60) + minute) + 1 #plus 1 bc first time column in table is t1

        try:
            conn_write = sqlite3.connect('PG2020_SQL.db')
            curs_write = conn_write.cursor()
            curs_write.execute("PRAGMA journal_mode=WAL;") #Activate 'Write-Ahead Logging'

            curs_write.execute("UPDATE puregym_table SET t{} = {} WHERE Day = '{}/{}/{}'".format(num,output2,day,month,year))
            conn_write.commit()

            curs_write.close()
            conn_write.close()
        except:
            print('Err: Could not write to PG2020_SQL.db')
        try:
            conn_write = sqlite3.connect('PG2020_SQL_CLEAN.db')
            curs_write = conn_write.cursor()
            curs_write.execute("PRAGMA journal_mode=WAL;")  # Activate 'Write-Ahead Logging'

            curs_write.execute(
                "UPDATE puregym_table SET t{} = {} WHERE Day = '{}/{}/{}'".format(num, output2, day, month, year))
            conn_write.commit()

            curs_write.close()
            conn_write.close()
        except:
            print('Err: Could not write to PG2020_SQL_CLEAN.db')
        #-----------------------------------------------------------------#

        #-------------------------PRINT_UPDATE (safe to exit after print)---------------------------------------#
        if minute%1 == 0:
            print('{}:{}:{}   Count: {}'.format(str(hour).zfill(2),str(minute).zfill(2),str(second).zfill(2),output2))
            pass
        #-------------------------------------------------------------------------------------------------------#

        fails = 0

        end = time.time()
        #print('End time: ',datetime.datetime.today().time())
        #print('Time to sleep: ' + str(60.000000 - (end - start - 0.011) % 60.000000))
        time.sleep(60.000000 - (end - start + 0.0065) % 60.000000)

    except:
        fails = fails + 1
        print("Fail " + str(fails))

        if fails > 0:
            #------------RESTART_BROWSER--------------#
            driver.quit()

            try:
                try:
                    # PATH = "C:\Program Files (x86)\chromedriver.exe"
                    # PATH = r"C:\Users\Owner\.wdm\drivers\chromedriver\win32\87.0.4280.20\chromedriver.exe"
                    PATH = r"C:\Users\Owner\.wdm\drivers\chromedriver\win32\87.0.4280.88\chromedriver.exe"
                    driver = webdriver.Chrome(PATH)
                except:
                    driver = webdriver.Chrome(ChromeDriverManager().install())
                    driver.get('https://www.puregym.com/members/')
                    print('NEW DRIVER CHANGE PATH')

                driver.get('https://www.puregym.com/members/')
                time.sleep(2.5)
                try:
                    accept = driver.find_element_by_class_name("coi-banner__accept")
                    accept.click()
                    time.sleep(2.5)
                except:
                    pass
                email = driver.find_element_by_id("email")
                pin = driver.find_element_by_id("pin")
                email.send_keys("cjr1977@hotmail.co.uk")
                pin.send_keys("34308915")
                pin.send_keys(Keys.ENTER)

                driver.set_window_rect(527, 974, 953, 520)
                driver.set_window_position(953, 520)
                driver.minimize_window()

                end = time.time()
                #print(datetime.datetime.today().time())
                #Don't sleep: straight to next

            except:
                print('Browser failed to reopen.')


            #------------------------------------------#
    #
    # end = time.time()
    # print(datetime.datetime.today().time())
    # # print('Start of loop: '+str(start))
    # # print('End of Loop: '+str(end))
    # # print('Difference: '+str(end-start))
    # # print((end - start) % 60.000000)
    # print('Time to sleep: '+str(60.000000 - (end - start - 0.011) % 60.000000))
    # time.sleep(60.000000 - (end-start-0.001) % 60.000000)
