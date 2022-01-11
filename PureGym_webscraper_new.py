# PureGym_webscraper.py

# This script runs 24/7 to parse the website for gym numbers and saves them to the SQL DATABASE.

###------------------IMPORTS-------------------###
import sqlite3
import time
import datetime
import os
import sys
import requests
from requests.exceptions import TooManyRedirects
from lxml import html
import re
import logging

from PureGym_credentials import EMAIL, PIN

#============LOGGER===============
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(name)s --- %(message)s')
#logger.setFormatter(formatter)

DIR_NAME = os.path.dirname(os.path.abspath(__file__))
file_handler = logging.FileHandler(DIR_NAME + '\logs\scraper_error.log')
file_handler.setLevel(logging.ERROR)
file_handler.setFormatter(formatter)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)
#=================================

LOGIN_PAGE   = 'https://www.puregym.com/Login/'
LOGOUT_PAGE  = 'https://www.puregym.com/logout/'
MEMBERS_PAGE = 'https://www.puregym.com/members/'

def check_status(code, msg):
    if code.status_code != 200:
        logger.warning(msg + 'failed.')
    else:
        logger.debug(msg + 'successful.')

def login_request(s):
    logger.info('LOGIN')
    login_result = s.get(LOGIN_PAGE)
    check_status(login_result, 'Login ')

    if b"The members area and class booking are currently unavailable" in login_result.content:
        print('The members area and class booking are currently unavailable')
        quit()

    tree = html.fromstring(login_result.text)
    token = tree.xpath("/html/body/div/main/div/form[2]/input/@value")[0]

    payload = {
        'username': EMAIL,
        'password': PIN,
        '__RequestVerificationToken': token
    }

    header = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebkit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36'
    }

    logger.debug(payload)

    #Post the data back to the same page
    login_result = s.post(login_result.url, data=payload, headers=header)
    check_status(login_result, 'Login ')

    # OIDC
    form = html.fromstring(login_result.text).forms[0]
    login_result = s.post(form.action, data=form.form_values())
    check_status(login_result, 'Login (OIDC) ')
    
def scrape_page(s):
    # Refresh members page
    members_result = s.get(MEMBERS_PAGE)
    logger.debug('Finding members page '+str(members_result.status_code))

    #Search for info using regex
    try:
        search_gym = re.findall(r'in.*href=\"/gyms/(.*)\">(.*)</a> right now', members_result.text)
        if len(search_gym) == 1 and len(search_gym[0]) == 2:
            (gym_ref, gym_nice) = search_gym[0]
            #(exeter-bishops-court, Exeter Bishops Court)
    except:
        logger.warning("Could not find gym name.")
        raise

    try:
        search_num = re.findall(r'there are.*\>(\d+) (?:or fewer )?(?:of \d+ )?people', members_result.text)
        if len(search_num) == 1 and int(search_num[0]) >= 0:
            gym_people = search_num[0]
            logger.debug("There are {} people in {}.".format(gym_people, gym_nice)) 
            return gym_people   
    except:
        logger.warning("Could not find number of poeple.")
        raise

def logout_request(s):
    # get logout page
    logger.info('LOGOUT')
    logout_result = s.get(LOGOUT_PAGE)
    logger.debug(logout_result.status_code)
    # which contains an iframe
    frame = html.fromstring(logout_result.text).xpath('//iframe')[0]
    logout_result = s.get(frame.attrib.get('src'))
    logger.debug(logout_result.status_code)
    # which also has an iframe
    frame = html.fromstring(logout_result.text).xpath('//iframe')[0]
    logout_result = s.get(frame.attrib.get('src'))
    logger.debug(logout_result.status_code)
    logger.info('LOGOUT complete')

def append_to_database(num, output, day, month, year):
    for database in DATABASES:
        logger.debug(DIR_NAME + database)
        try:
            conn_write = sqlite3.connect(os.path.join(DIR_NAME,database))
            curs_write = conn_write.cursor()
            curs_write.execute("PRAGMA journal_mode=WAL;") #Activate 'Write-Ahead Logging'

            curs_write.execute("UPDATE puregym_table SET t{} = {} WHERE Day = '{}/{}/{}'".format(num, output, day, month, year))
            conn_write.commit()

            curs_write.close()
            conn_write.close()
        except:
            conn_write.close()
            if not output:
                logger.error('Could not write {} to '.format(output)+database)
            else:
                logger.error('Could not write "None" to '+database)



if __name__ == "__main__":
    print('\n =============== START SCRAPE ============ \n')

    YEAR = input('Input database year: ')
    fails = 0
    DATABASES = [os.path.join('PureGymAnlaysis','PG{}_SQL.db'.format(YEAR)),
                os.path.join('PureGymAnlaysis','PG{}_SQL_CLEAN.db'.format(YEAR))] 

    secs = int(datetime.datetime.today().strftime('%S'))
    if secs>5:
        time.sleep(61-secs)

    while True:
        with requests.Session() as s:
            logger.info('Start new session.')
            login_request(s)

            run = True

            while run:
                try:
                    start = time.time()

                    try:
                        output = scrape_page(s)
                    except ConnectionError:
                        logger.error('ConnectionError when refreshing.')
                        output = None

                    now = datetime.datetime.today()
                    timee = now.time()
                    datee = now.date()
                    minute = int(timee.strftime('%M'))
                    hour = int(timee.strftime('%H'))
                    second = int(timee.strftime('%S'))
                    day = datee.strftime('%d')
                    month = datee.strftime('%m')
                    year =  datee.strftime('%y')

                    num = int((hour * 60) + minute) + 1 #plus 1 bc first time column in table is t1
                    append_to_database(num, output, day, month, year)
                    print('{}:{}:{} |{}| Count: {}'.format(str(hour).zfill(2), str(minute).zfill(2), str(second).zfill(2), fails, output))

                    end = time.time()
                    wait = 60.000000 - (end - start + 0.0065) % 60.000000
                    time.sleep(wait)
                    logger.debug('Wait {}s'.format(wait))
                    fails = 0
                except: 
                    run = False 
                    logger.info('FALSE')
                                         
                    if fails < 3:
                        fails += 1
                        logger.error('Did not save. FAILS = {}/3'.format(fails))
                    else:
                        logger.critical('SCRAPING TERMINATED.')
                        quit()


                # except: 
                #     try:
                #         logout_request(s)
                #     except ConnectionResetError:
                #         logger.error('ConnectionResetError, could not logout.')
                #         run = False
                        
                #     if fails < 3:
                #         fails += 1
                #         logger.error('Did not save. FAILS = {}/3'.format(fails))
                #         try:
                #             login_request(s)
                #         except TooManyRedirects:
                #             logger.error('TooManyRedirects when trying to login.')
                #             run = False
                #     else:
                #         logger.critical('SCRAPING TERMINATED.')
                #         quit()
                
            logger.info('End session.')
            time.sleep(5)