#Create New table
import sqlite3
import datetime
import os


YEAR = 2021
DATABASES = [f'\PureGymAnlaysis\PG{YEAR}_SQL.db',f'\PureGymAnlaysis\PG{YEAR}_SQL_CLEAN.db'] 

def main():
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
        date_list = [datetime.datetime(2020,12,31,0,0,0,0) + datetime.timedelta(days=x) for x in range(numdays)]
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

if __name__ == '__main__':
    print('\n =============== START ============ \n')
    main()
    print('\n ================ END ============= \n')