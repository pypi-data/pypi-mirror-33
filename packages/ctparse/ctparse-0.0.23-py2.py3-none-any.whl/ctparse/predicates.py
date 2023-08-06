from . types import Time, Interval


def typeTime(t):
    return isinstance(t, Time)


def typeInterval(i):
    return isinstance(i, Interval)


def isDOY(t):
    return t._hasOnly('month', 'day')


def isDOM(t):
    '''isDayOfMonth <=> a dd but no month
    '''
    # return t._hasOnly('day')
    return type(t) is Time and t.day is not None and t.year is None and t.month is None and t.day is None and t.minute is None and t.DOW is None and t.POD is None


def isDOW(t):
    '''isDayOfWeek <=> DOW is the 0=Monday index; fragile test, as the DOW
    could be accompanied by e.g. a full date etc.; in practice,
    however, the production rules do not do that.

    '''
    return t._hasOnly('DOW')


def isMonth(t):
    return t._hasOnly('month')


def isPOD(t):
    '''isPartOfDay <=> morning, etc.; fragile, tests only that there is a
    POD and neither a full date nor a full time
    '''
    return t._hasOnly('POD')


def isTOD(t):
    '''isTimeOfDay - only a time, not date'''
    return t._hasOnly('hour') or t._hasOnly('hour', 'minute')


def isDate(t):
    '''isDate - only a date, not time'''
    return t._hasOnly('year', 'month', 'day')


def isDateTime(t):
    '''a date and a time'''
    return (t._hasOnly('year', 'month', 'day', 'hour') or
            t._hasOnly('year', 'month', 'day', 'hour', 'minute'))


def isYear(t):
    '''just a year'''
    return t._hasOnly('year')


def hasDate(t):
    '''at least a date'''
    return t._hasAtLeast('year', 'month', 'day')


def hasDOW(t):
    '''at least a day of week'''
    return t._hasAtLeast('DOW')


def hasTime(t):
    '''at least a time to the hour'''
    return t._hasAtLeast('hour')


def hasPOD(t):
    '''at least a part of day'''
    return t._hasAtLeast('POD')


def isClosedTimeInterval(i):
    return hasTFrom(i) and hasTTo(i) and isTOD(i.t_from) and isTOD(i.t_to)


def isTimeInterval(i):
    return (hasTFrom(i) and isTOD(i.t_from)) or (hasTTo(i)  and isTOD(i.t_to))


def hasTFrom(i):
    return i._hasAtLeast('t_from')


def hasTTo(i):
    return i._hasAtLeast('t_to')

