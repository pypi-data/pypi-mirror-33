import datetime
import dateutil.tz
import os

__year_cache = {}
__tz_cache = {}
__utc = dateutil.tz.tzutc()

def __gettz(tz):
    if tz in __tz_cache:
        return __tz_cache[tz]
    z = dateutil.tz.gettz(tz)
    if z.__class__.__name__ != 'tzfile':
        raise ValueError("No such time zone: {}".format(tz))
    __tz_cache[tz] = z
    return(z)

def __year2datetime(y):
    if y in __year_cache:
        return __year_cache[y]
    z = datetime.datetime(y, 1, 1, 0, 0, 0, 0, tzinfo=__utc)
    __year_cache[y] = z
    return z

def datetime2stardate(x):
    a = x.astimezone(__utc)
    y0 = a.year
    t0 = __year2datetime(y0)
    t1 = __year2datetime(y0 + 1)
    sd = y0 + (a - t0)/(t1 - t0)
    return sd    

def stardate2datetime(x, tz):
    y0 = int(x)
    t0 = __year2datetime(y0)
    t1 = __year2datetime(y0 + 1)
    return (t0 + (x - y0) * (t1 - t0)).astimezone(__gettz(tz))

def timestamp2stardate(x):
    return datetime2stardate(datetime.datetime.fromtimestamp(x))

def getmtime(p):
    m = os.path.getmtime(p)
    return timestamp2stardate(m)

def now():
    dt = datetime.datetime.utcnow().replace(tzinfo=dateutil.tz.tzutc())
    return datetime2stardate(dt)

def timestampedfilename(p):
    x, y = os.path.splitext(p)
    return "{0}-{1:0.15f}{2}".format(x, getmtime(p), y)

def rename(p):
    os.rename(p, timestampedfilename(p))

def short(s):
    return "{0:0.3f}".format(s)

def canonical(s):
    return "{0:0.15f}".format(s)

def stardate(*,
        year, month, day,
        hour=12, minute=0, second=0, microsecond=0,
        digits=None,
        tz):
    x = datetime.datetime(
        int(year),
        int(month),
        int(day),
        int(hour),
        int(minute),
        int(second),
        int(microsecond),
        tzinfo = __gettz(tz))
    sd = datetime2stardate(x)
    if not digits:
        return sd
    if digits == "short":
        digits = 3
    elif digits == "canonical":
        digits = 15
    fmt = "{0:0." + str(digits) + "f}"
    return fmt.format(sd)

millisecond = 1.0/31556952000.0
second = 1.0/31556952.0
minute = 1.0/525949.2
hour = 1.0/8765.82
day = 1.0/365.2425
week = 7.0/365.2425
fortnight = 14.0/365.2425
month = 1.0/12.0
