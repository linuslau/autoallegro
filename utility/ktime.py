#from datetime import datetime, timedelta
#from pytz import utc

import time
import datetime
from pytz import timezone
from tzlocal import get_localzone

'''
# https://www.cnblogs.com/lucktomato/p/16708797.html
def get_utc_time():
    now_time = datetime.now()
    utc_time = now_time - timedelta(hours=8)  # 减去8小时
    utc_time = utc_time.strftime("%Y-%m-%d %H:%M:%S")
    print(utc_time)

def get_utc_time_2():
    # 本地时间
    dt_loc = datetime.strptime("2020-07-09 18:21:17", "%Y-%m-%d %H:%M:%S")
    print(type(dt_loc))
    print(dt_loc)

    # 本地时间转UTC时间
    dt_utc = dt_loc.astimezone(utc)

    # UTC时间转本地时间
    dt_loc1 = dt_utc.astimezone()

    print(dt_utc)
    print(dt_loc1)
# https://www.cnblogs.com/lucktomato/p/16708797.html

# https://cloud.tencent.com/developer/article/1569918
def utc2local( utc_dtm ):
    # UTC 时间转本地时间（ +8:00 ）
    local_tm = datetime.fromtimestamp( 0 )
    utc_tm = datetime.utcfromtimestamp( 0 )
    offset = local_tm - utc_tm
    return utc_dtm + offset

def local2utc( local_dtm ):
    # 本地时间转 UTC 时间（ -8:00 ）
    return datetime.utcfromtimestamp( local_dtm.timestamp() )
# https://cloud.tencent.com/developer/article/1569918
'''

# https://blog.csdn.net/qq_19446965/article/details/112154864
def utc2local(utc_st):
    """UTC时间转本地时间（+8:00）"""
    now_stamp = time.time()
    local_time = datetime.datetime.fromtimestamp(now_stamp)
    utc_time = datetime.datetime.utcfromtimestamp(now_stamp)
    offset = local_time - utc_time
    local_st = utc_st + offset
    return local_st

def local2utc(local_st):
    """本地时间转UTC时间（-8:00）"""
    time_struct = time.mktime(local_st.timetuple())
    utc_st = datetime.datetime.utcfromtimestamp(time_struct)
    return utc_st

def get_local_time_zone():
    """获取本地时区"""
    try:
        return get_localzone()
    except pytz.UnknownTimeZoneError:
        return timezone("Asia/Shanghai")

def calculate_offset(now_stamp):
    """计算时区偏移量"""
    local_time = datetime.datetime.fromtimestamp(now_stamp, tz=get_local_time_zone())
    utc_time = datetime.datetime.utcfromtimestamp(now_stamp)
    offset = int(local_time.hour - utc_time.hour) * 3600
    return offset
# https://blog.csdn.net/qq_19446965/article/details/112154864

if __name__ == '__main__':
    t1 = datetime.datetime(2021, 11, 6, 1,1,1,123)
    datetime_stamp = datetime.datetime.timestamp(t1)
    print(datetime_stamp)

    '''
    get_utc_time()
    get_utc_time_2()

    # utc_tm = datetime.utcnow()
    utc_tm = datetime( 2012, 10, 26, 10, 00, 00 )

    print( "src utc time:\t", utc_tm.strftime("%Y-%m-%d %H:%M:%S") )

    # UTC 转本地
    local_tm = utc2local(utc_tm)
    print( "tran loc time:\t", local_tm.strftime("%Y-%m-%d %H:%M:%S") )

    # 本地转 UTC
    utc_tran = local2utc(local_tm)
    print( "tran utc time:\t", utc_tran.strftime("%Y-%m-%d %H:%M:%S") )
    '''

    now_stamp = time.time()
    print('now_stamp: ' + str(now_stamp))
    local_time = datetime.datetime.fromtimestamp(now_stamp)
    print('local_time: ' + str(local_time))
    utc_time = datetime.datetime.utcfromtimestamp(now_stamp)
    print('utc_time: ' + str(utc_time))
