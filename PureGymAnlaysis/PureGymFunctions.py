#PureGymFunctions
import datetime
import sqlite3

def time2num(t):
#Takes a (date)time and converts it to a number of minutes index
    hour = t.hour
    minute = t.minute
    num = (hour * 60) + minute
    return num, hour, minute

def num2time(n):
#takes a number of minutes index and converts it to a (date)time
    minute = int(n%60)
    hour = int((n-minute)/60)
    t = datetime.datetime(2020,1,1,hour,minute,0,0)
    return t, hour, minute



if __name__ == '__main__':
    databases = ['PG2020_SQL.db','PG2020_SQL_CLEAN.db']
    for db in databases:
        print(db)
        conn = sqlite3.connect(db)
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table';")
        print(c.fetchall())

        # strvar = 'Day TEXT PRIMARY KEY, '
        # for i in range(1439):
        #     strvar = strvar + 't'+str(i+1)+' INTEGER, '
        # strvar = strvar + 't1440 INTEGER'
        #print("CREATE TABLE test_table ({})".format(strvar))

        #c.execute("CREATE TABLE test_table ({})".format(strvar))
        #conn.commit()

        ###-----CREATE&INSERT NULL ROWS--------------###
        numdays = 365
        start_date = datetime.datetime(2021,10,1,0,0,0,0)
        date_list = [start_date + datetime.timedelta(days=x) for x in range(numdays)]
        date_list1 = ['{}/{}/{}'.format(d.strftime('%d'),d.strftime('%m'),d.strftime('%y')) for d in date_list] 
        #print(date_list1)

        for j in range(numdays):
            #strrow = "'01/11/20', "
            strrow = "'{}', ".format(date_list1[j])
            for i in range(1440):
                strrow = strrow + 'NULL, '
            strrow = strrow + 'NULL, 0' #COMMENT: NULL    ML:0
            #print(strrow)
            c.execute("INSERT INTO puregym_table VALUES ({})".format(strrow))
        conn.commit()
        
        ###---ADD COMMENTS COLUMN---###
        #c.execute("ALTER TABLE puregym_table ADD Comments TEXT")
        #conn.commit()

        conn.close()