import datetime
import pytz
from datetime import datetime
from timezonefinder import TimezoneFinder

from django.utils.functional import cached_property


class cached_classproperty(cached_property):
    def __init__(self, *args, **kwargs):
        super(cached_classproperty, self).__init__(*args, **kwargs)
        self.cache = {}

    def clear(self):
        self.cache.clear()

    def __get__(self, instance, cls=None):
        if cls is None:
            cls = type(instance)

        cache = self.cache
        if cls in cache:
            return cache[cls]

        res = self.func(cls)
        cache[cls] = res
        return res


def get_minutes_timedelta(coords_1, coords_2, dt_1, dt_2):
    """
    Get duration of a flight departing at coords_1 and arriving at coords_2
    at the given datetimes in different timezones
    :param coords_1: {'lat':x, 'long':y}
    :param coords_2: {'lat':x, 'long':y}
    :param dt_1: datetime
    :param dt_2: datetime
    :return:
    """
    tf = TimezoneFinder()
    tmz_1 = pytz.timezone(tf.timezone_at(lat=coords_1['lat'], lng=coords_1['long'])).utcoffset(datetime.now())
    tmz_2 = pytz.timezone(tf.timezone_at(lat=coords_2['lat'], lng=coords_2['long'])).utcoffset(datetime.now())
    if tmz_1 > tmz_2:
        timezone_diff = (tmz_1 - tmz_2).seconds // 60
    else:
        timezone_diff = (tmz_2 - tmz_1).seconds // 60
        timezone_diff = -timezone_diff
    dt_diff = dt_1 - dt_2
    if dt_diff.days == -1:
        dt_diff = dt_2 - dt_1
    dt_diff = dt_diff.seconds // 60
    return timezone_diff + dt_diff


def day_difference(daytime1, daytime2) -> bool:
    """
    Checks if the difference between the two daytime objects is greater than 15 days
    :param daytime1: datetime
    :param daytime2: datetime
    :return: boolean
    """
    if daytime1 > daytime2:
        daytime1, daytime2 = daytime2, daytime1
    return (daytime2 - daytime1).days
