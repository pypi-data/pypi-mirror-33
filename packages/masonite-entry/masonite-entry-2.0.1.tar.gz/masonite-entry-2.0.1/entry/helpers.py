import pendulum

def expiration_time(str_time, parse=None, subtract=False):
    """ str_time should be a string like "1 month" """

    if str_time is not 'expired':
        number = int(str_time.split(" ")[0])
        length = str_time.split(" ")[1]

        if parse:
            time_direction = pendulum.parse(parse, tz='GMT')
        else:
            time_direction = pendulum.now('GMT')
        
       

        if subtract:
            time_direction = time_direction.subtract
        else:
            time_direction = time_direction.add

        if length in ('second', 'seconds'):
            return time_direction(seconds=number)
        elif length in ('minute', 'minutes'):
            return time_direction(minutes=number)
        elif length in ('hour', 'hours'):
            return time_direction(hours=number)
        elif length in ('days', 'days'):
            return time_direction(days=number)
        elif length in ('week', 'weeks'):
            return time_direction(weeks=1).format('%a, %d %b %Y %H:%M:%S GMT')
        elif length in ('month', 'months'):
            return time_direction(months=number).format('%a, %d %b %Y %H:%M:%S GMT')
        elif length in ('year', 'years'):
            return time_direction(years=number).format('%a, %d %b %Y %H:%M:%S GMT')

        return None
    else:
        return pendulum.now('GMT').subtract(years=20).format('%a, %d %b %Y %H:%M:%S GMT')