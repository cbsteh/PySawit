"""
SimWeather module.

Simulates daily weather for min. and max. air temperature, wind speed, and rainfall.

!!! warning "Required installation"
    * [Anaconda](https://www.continuum.io/downloads) for `scipy` for statistics

# Author - Christopher Teh Boon Sung
------------------------------------

"""


import json
import math
import random
from collections import namedtuple

from scipy.stats import exponweib
from scipy.stats import gamma

from annualweather import AnnualWeather

ParamRain = namedtuple('ParamRain', ['pww', 'pwd', 'shape', 'scale'])
ParamRain.__doc__ = '`' + ParamRain.__doc__
ParamRain.__doc__ += '`\r\nnamedtuple: Rain generation parameters'
ParamRain.pww.__doc__ = 'float: probability of two consecutive wet days'
ParamRain.pwd.__doc__ = 'float: probability of a wet day, followed by a dry day'
ParamRain.shape.__doc__ = 'float: shape factor of the gamma probability distribution'
ParamRain.scale.__doc__ = 'float: scale factor of the gamma probability distribution'

ParamTemp = namedtuple('ParamTemp', ['mean', 'amp', 'cv', 'ampcv', 'meanwet'])
ParamTemp.__doc__ = '`' + ParamTemp.__doc__
ParamTemp.__doc__ += '`\r\nnamedtuple: Air temperature generation parameters'
ParamTemp.mean.__doc__ = 'float: annual mean air temperature'
ParamTemp.amp.__doc__ = 'float: amplitude (highest value - mean value) of air temperature'
ParamTemp.cv.__doc__ = 'float: coefficient of variation of air temperature'
ParamTemp.ampcv.__doc__ = 'float: amplitude (smallest value - mean value) of cv'
ParamTemp.meanwet.__doc__ = 'float: mean air temperature on days that rained'

ParamWind = namedtuple('ParamWind', ['shape', 'scale'])
ParamWind.__doc__ = '`' + ParamWind.__doc__
ParamWind.__doc__ += '`\r\nnamedtuple: Wind generation parameters'
ParamWind.shape.__doc__ = 'float: shape factor of the Weibull probability distribution'
ParamWind.scale.__doc__ = 'float: scale factor of the Weibull probability distribution'


class SimWeather(AnnualWeather):
    """
    SimWeather class.

    Simulate daily weather for min. and max. air temperatures, wind speed, and rain.

    # CLASS ATTRIBUTES
        cumulative_days (tuple): cumulative number of days for every month

    # METHODS
        rnd: Random number generator [0-1)
        generate_rain: Daily rainfall amount (mm/day) based on a fitted inverse gamma CDF
        generate_temperature: Daily max. and min. air temperatures (deg. C)
        generate_wind: Mean daily wind speed (m/s) based on a fitted inverse Weibull distribution
        update: Generate (simulate) a new set of daily weather for one year

    """

    # cumulative no. of days in a month
    cumulative_days = (31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334, 365)

    # used for temperature and rain generation:
    __a = ((0.567, 0.086, -0.002),
           (0.253, 0.504, -0.050),
           (-0.006, -0.039, 0.244))
    __b = ((0.781, 0.000, 0.000),
           (0.328, 0.637, 0.000),
           (0.238, -0.341, 0.873))

    def __init__(self, infile, jsonformat=False):
        """
        Create and initialize the SimWeather object.

        # Arguments
            infile (str/json): path and filename of initialization text file
                               or a JSON-formatted string
            jsonformat (bool): `False` if `infile` is a plain text file, or
                               `True` if `infile` is a string in JSON format

        """
        AnnualWeather.__init__(self, 365, 'tmin', 'tmax', 'wind', 'rain')
        ini = infile
        if not jsonformat:
            with open(infile, 'rt') as fin:
                ini = json.loads(fin.read())  # read everything in the file

        self.__prain = ParamRain(*list(ini['rain'][field] for field in ParamRain._fields))
        self.__ptmin = ParamTemp(*list(ini['tmin'][field] for field in ParamTemp._fields))
        self.__ptmax = ParamTemp(*list(ini['tmax'][field] for field in ParamTemp._fields))
        self.__pwind = ParamWind(*list(ini['wind'][field] for field in ParamWind._fields))

        # each of the rain and wind parameters must have 12 and only 12 items in its list:
        for i in range(len(ParamRain._fields)):
            SimWeather.__fill_in(self.__prain[i])
        for i in range(len(ParamWind._fields)):
            SimWeather.__fill_in(self.__pwind[i])

        # internal use: temporarily stores values for internal calculations:
        self.__g = {'txm': 0.0, 'txs': 0.0, 'txm1': 0.0, 'txs1': 0.0, 'tnm': 0.0, 'tns': 0.0}
        self.__xim1 = [0.0, 0.0, 0.0]
        self.__iday = 0     # track number of generated days
        self.__imth = 0     # track number of generated months
        self.__is_rain = random.choice(['True', 'False'])     # rain or dry - random select

    @staticmethod
    def rnd():
        """
        !!! note
            `rnd` is a static method.

        Generate a uniform random number between the interval [0 - 1).

        # Returns
            float: random value [0-1)

        """
        return random.random()

    @staticmethod
    def __fill_in(lst):
        """
        !!! note
            `__fill_in` is a static method.

        Ensure list contains only 12 items (one item for each month).

        Makes copies of existing items to extend the list if less than 12 items.

        # Arguments
            lst (list): list to check and fill in with values

        # Returns
            None:

        """
        n = len(lst)
        if n < 12:
            lst.extend(lst[:n] * (12 // n))  # less than 12 items, so fill in with copies
            n = len(lst)  # need to check the length of new list
        if n > 12:
            del lst[12:]  # remove extraneous items from list (must have only 12 items in list)

    def generate_rain(self):
        """
        Determine the daily rainfall amount (mm/day) based on a fitted inverse gamma CDF.

        # Returns
            None:

        """
        day = self.__iday
        mth = self.__imth
        x = 1 - SimWeather.rnd()
        rain = self.table['rain']
        rain[day] = gamma.ppf(x, self.__prain.shape[mth], scale=self.__prain.scale[mth])
        self.__is_rain = rain[day] > 0.0

    def generate_temperature(self):
        """
        Determine the daily max. and min. air temperatures (deg. C).

        # Returns
            None:

        """
        day = self.__iday
        # daily min. and max. air temperatures (deg. C):
        if self.__is_rain:
            txxm = self.__g['txm1']
            txxs = self.__g['txs1']
        else:
            txxm = self.__g['txm']
            txxs = self.__g['txs']
        # random error generator:
        e = [0.0, 0.0, 0.0]
        for k in range(3):
            v = 3.0
            while math.fabs(v) > 2.5:
                rn1 = SimWeather.rnd()
                rn2 = SimWeather.rnd()
                v = math.sqrt(-2 * math.log(rn1)) * math.cos(2 * math.pi * rn2)
            e[k] = v
        r = [0.0, 0.0, 0.0]
        rr = [0.0, 0.0, 0.0]
        for i in range(3):
            for j in range(3):
                r[i] += SimWeather.__b[i][j] * e[j]
                rr[i] += SimWeather.__a[i][j] * self.__xim1[j]
        x = [0.0, 0.0, 0.0]
        for k in range(3):
            self.__xim1[k] = x[k] = r[k] + rr[k]
        self.table['tmax'][day] = x[0] * txxs + txxm
        self.table['tmin'][day] = x[1] * self.__g['tns'] + self.__g['tnm']
        if self.table['tmin'][day] > self.table['tmax'][day]:
            tmm = self.table['tmax'][day]
            self.table['tmax'][day] = self.table['tmin'][day]
            self.table['tmin'][day] = tmm

    def generate_wind(self):
        """
        Determine the mean daily wind speed (m/s) based on a fitted inverse Weibull distribution.

        # Returns
            None:

        """
        day = self.__iday
        mth = self.__imth
        pw = self.__pwind
        windspd = -1.0  # enter the below loop at least once to sample for wind speed
        while windspd < 0.2:
            # generated mean daily wind speed cannot be lower than that ever
            #    recorded in Malaysia (about 0.2 m/s)
            x = 1 - SimWeather.rnd()
            windspd = exponweib.ppf(x, a=1, c=pw.shape[mth], loc=0, scale=pw.scale[mth])
        self.table['wind'][day] = windspd

    def update(self):
        """
        Generate (simulate) one year of daily weather.

        # Returns
            None:

        """
        d1 = self.__ptmax.mean - self.__ptmax.meanwet
        mth = 0
        for day in range(365):
            dt = math.cos(0.0172 * (day + 1 - 200))
            self.__g['txm'] = self.__ptmax.mean + self.__ptmax.amp * dt
            xcr1 = self.__ptmax.cv + self.__ptmax.ampcv * dt
            if xcr1 < 0.0:
                xcr1 = 0.06
            self.__g['txs'] = self.__g['txm'] * xcr1
            self.__g['txm1'] = self.__g['txm'] - d1
            self.__g['txs1'] = self.__g['txm1'] * xcr1
            self.__g['tnm'] = self.__ptmin.mean + self.__ptmin.amp * dt
            xcr2 = self.__ptmin.cv + self.__ptmin.ampcv * dt
            if xcr2 < 0.0:
                xcr2 = 0.06
            self.__g['tns'] = self.__g['tnm'] * xcr2
            if (day + 1) > SimWeather.cumulative_days[mth]:
                mth += 1  # next month
            rn = SimWeather.rnd()
            prob = rn - (self.__prain.pwd[mth] if not self.__is_rain else self.__prain.pww[mth])

            self.__iday = day
            self.__imth = mth
            if prob <= 0.0:
                self.generate_rain()  # rains today, now generate its amount
            else:
                self.__is_rain = False
                self.table['rain'][day] = 0.0  # no rain today

            # generate other weather parameters:
            self.generate_temperature()  # generate min. and max. temperatures
            self.generate_wind()  # daily wind speed (m/s)
