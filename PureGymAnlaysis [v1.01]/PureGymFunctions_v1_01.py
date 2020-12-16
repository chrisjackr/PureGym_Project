#PureGymFunctions

def time2num(t):
#Takes a (date)time and converts it to a number of minutes index
    hour = t.hour
    minute = t.minute
    num = (hour * 60) + minute
    return num, hour, minute

def num2time(n):
#takes a number of minutes index and converts it to a (date)time
    minute = int(n%60)
    hour = int((n-m)/60)
    t = datetime.datetime(2020,11,19,h,m,0)
    return t, hour, minute
