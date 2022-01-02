#Create New table
import sqlite3
import datetime
import os

def main(YEAR):
    for database in DATABASES:
        ###--------------CREATE TABLE------------------###
        DIR_NAME = os.path.dirname(os.path.abspath(__file__))
        conn = sqlite3.connect(DIR_NAME+f'{database}')
        c = conn.cursor()

        strvar = 'Day TEXT PRIMARY KEY, '
        for i in range(1440):
            strvar = strvar + 't'+str(i+1)+' INTEGER, '
        strvar = strvar + 'Comments TEXT, ML INTEGER' 
        #print("CREATE TABLE test_table ({})".format(strvar))

        c.execute("CREATE TABLE puregym_table ({})".format(strvar))
        conn.commit()

        ###-----CREATE & INSERT NULL ROWS--------------###
        numdays = 367
        date_list = [datetime.datetime(YEAR-1,12,31,0,0,0,0) + datetime.timedelta(days=x) for x in range(numdays)]
        date_list1 = ['{}/{}/{}'.format(d.strftime('%d'),d.strftime('%m'),d.strftime('%y')) for d in date_list] 
        #print(date_list1)

        for j in range(numdays):
            strrow = "'{}', ".format(date_list1[j]) #strrow = "'01/01/20', "
            for i in range(1440):
                strrow = strrow + 'NULL, '
            strrow = strrow + 'NULL, 0'
            c.execute("INSERT INTO puregym_table VALUES ({})".format(strrow))
        conn.commit()

        print(database+' created.')

        ###---ADD COMMENTS & ML COLUMNS---###
        # c.execute("ALTER TABLE puregym_table ADD Comments TEXT")
        # c.execute("ALTER TABLE puregym_table ADD ML INTEGER")
        # conn.commit()

def insert(YEAR):
    for database in DATABASES:
        ###--------------CREATE TABLE------------------###
        DIR_NAME = os.path.dirname(os.path.abspath(__file__))
        conn = sqlite3.connect(DIR_NAME+f'{database}')
        c = conn.cursor()

        ###-----CREATE & INSERT NULL ROWS--------------###
        CALENDAR = []
        tdelta = datetime.timedelta(days=1)
        sdate = datetime.date(YEAR-1,12,31)
        edate = datetime.date(YEAR+1,1,1)
        delta = edate-sdate
        for i in range(delta.days+1):
            date = sdate + datetime.timedelta(days=i)
            CALENDAR.append(date.strftime('%d/%m/%y'))

        #print(CALENDAR)
        for date in CALENDAR:
            print(date)
            strrow = "'{}', ".format(date) #strrow = "'01/01/20', "
            for i in range(1440):
                strrow = strrow + 'NULL, '
            strrow = strrow + 'NULL, 0'
            c.execute("INSERT INTO puregym_table VALUES ({})".format(strrow))
        conn.commit()

        print(database+' updated.')


if __name__ == '__main__':
    print('\n =============== START ============ \n')
    YEAR = 2022
    DATABASES = [f'\PureGymAnlaysis\PG{YEAR}_SQL_.db',f'\PureGymAnlaysis\PG{YEAR}_SQL_CLEAN_.db'] 
    #CHOSE EITHER main OR insert
    #   - main: makes whole new year database from 31/12/YEAR-1 to 1/1/YEAR+1 (367 days, overlap by 2 days)
    main(YEAR)
    #insert(YEAR)
    print('\n ================ END ============= \n')