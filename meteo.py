"""
Meteorological module.

Daily and hourly (instantaneous) meteorology properties.

# Author - Christopher Teh Boon Sung
------------------------------------

"""

import json
import math
import random
from collections import namedtuple

from simweather import SimWeather
from weatherfile import WeatherFile


SolarRadComponents = namedtuple('SolarRadComponents', ['total', 'direct', 'diffuse'])
SolarRadComponents.__doc__ = '`' + SolarRadComponents.__doc__
SolarRadComponents.__doc__ += '`\r\nnamedtuple: Solar radiation components'
SolarRadComponents.total.__doc__ = 'float: total solar radiation (direct + diffuse)'
SolarRadComponents.direct.__doc__ = 'float: direct solar radiation'
SolarRadComponents.diffuse.__doc__ = 'float: diffuse solar radiation'

SolarPos = namedtuple('SolarPos', ['inc', 'hgt', 'azi'])
SolarPos.__doc__ = '`' + SolarPos.__doc__
SolarPos.__doc__ += '`\r\nnamedtuple: Solar position'
SolarPos.inc.__doc__ = 'float: solar inclination (angle from vertical)'
SolarPos.hgt.__doc__ = 'float: solar elevation or height (angle from horizontal)'
SolarPos.azi.__doc__ = 'float: solar azimuth (angle from North in a clockwise direction)'


class Meteo(object):
    """
    Meteorology class.

    Daily and hourly (instantaneous) meteorology properties.

    Daily meteorological properties can either be read from a provided weather file, or have them
    simulated. If the latter, users can provide a specific seed number for deterministic runs,
    which means model output always returns the exact same results, provided model input do not
    change, or users can enter a zero or negative seed value, which means the model output would
    vary even though the model input remained the same.

    !!! important
        If the weather data are loaded from a file, ensure the weather file contains
        information on the minimum and maximum air temperature, wind speed, and rainfall.

    Based on daily values, hourly (instantaneous) meteorological properties are then simulated, as
    needed.

    !!! note
        Time is indicated by local solar hour (not local time). This class only allows
        the day of year (`doy`) to move forward a day at a time, where each time the day
        moves forward, the model is updated (see generator `next_day()`).

    # ATTRIBUTES
        seed (int): Random seed number
        lat (float): Site latitude (deg.)
        methgt (float)- Weather station height (m)
        doy (int): Day of year (Jan 1 = 1, Feb 1 = 32, ..., Dec 31 = 365)
        solarhour (float): Local solar hour (not local time!) (hours)
        dewtemp (float): Dew temperature (deg. C)
        lag (float): No. of hours after sunrise when air temperature
                     and wind speed are minimum (hours)
        is_generated (bool): `True` to generate daily weather or `False` to read in daily weather
        weatherfilename (str): Name of weather file
        annwthr (AnnualWeather): Annual daily weather data for current year
        nyears (int): Year number (number of years elapsed)
        decl (float): Solar declination (radians)
        sunrise (float): Local solar hour of sunrise (hour)
        sunset (float): Local solar hour of sunset (hour)
        daylen (float): Length of day (hour)
        solarconst (float): Solar constant (W/m2)
        dayetrad (float): Daily extra-terrestrial (ET) solar irradiance (MJ/m2)
        dayrad (SolarRadComponents): Daily solar rad components (MJ/m2)
        daytmin (float): Min. daily air temperature (deg. C)
        daytmax (float): Max. daily air temperature (deg. C)
        daytmean (float): Mean daily air temperature (deg. C)
        daywind (float): Daily wind speed (m/s)
        dayrain (float): Rainfall amount (mm/day)
        solarpos (SolarPos): Solar position (inclination and azimuth) (radians)
        etrad (float): Extra-terrestrial (ET) solar irradiance (W/m2)
        rad (SolarRadComponents): Solar radiation components (W/m2)
        airtemp (float): Air temperature (deg. C)
        slopesvp (float): Slope of the saturated air vapor pressure curve (mbar/K)
        svp (float): Saturated air vapor pressure (mbar)
        vp (float): Air vapor pressure (mbar)
        vpd (float): Vapor pressure deficit (mbar)
        rh (float): Air relative humidity (%)
        netrad (float): Net radiation (W/m2)
        windspd (float): Wind speed (m/s)

    # METHODS
        doy365: Forces the day of year to stay within 1 and 365 inclusive
        rnd: Random number, needs to be seeded by the user or computer
        svp_fn: Saturated air vapor pressure for a given air temperature (mbar)
        solar_declination: Solar declination (radians)
        sunrise_set_hour: Local solar hour of sunrise and sunset (hours)
        daylength: No. of hours between sunrise and sunset (hours)
        solar_constant: Solar irradiance outside Earth (W/m2)
        day_et_radiation: Daily total extraterrestrial solar irradiance (MJ/m2/day)
        day_radiation: Daily direct, diffuse, and total solar irradiance (MJ/m2/day)
        solar_position: Inclination, height, and azimuth of the Sun (radians)
        et_radiation: Instantaneous extraterrestrial solar irradiance (W/m2)
        radiation: Instantaneous direct, diffuse, and total solar irradiance (W/m2)
        air_temperature: Instantaneous air temperature (deg. C)
        svp: Saturated air vapor pressure (mbar)
        slope_svp: Slope of the saturated air vapor pressure (mbar/deg. C)
        vapor_pressure: Air vapor pressure (mbar)
        vapor_pressure_deficit: Vapor pressure deficit (mbar)
        relative_humidity: Relative humidity (%)
        net_radiation: Net radiation (W/m2)
        wind_speed: Wind speed (m/s)
        integrate: N-point numerical Gaussian integration
        update_weather: Update daily weather when day of year and/or local solr hour have changed
        next_day: Generator to increment DOY and then update the model properties

        doy_has_changed: To be implemented in descendant classes that day of year has changed
        update: To be implemented in descendant classes for updating model properties based on
                 current model settings or values

    """

    def __init__(self, fname_in):
        """
        Create and initialize the Weather object.

        # Arguments
            fname_in (str): path and filename of the model initialization file

        """
        with open(fname_in, 'rt') as fin:
            self.ini = json.loads(fin.read())    # read everything in the file

        ini = self.ini
        self.seed = ini['seed']
        self.lat = math.radians(ini['lat'])  # supplied site latitude (deg.) stored in radians
        self.methgt = ini['methgt']  # weather station height (m)
        doy = ini['doy']  # day of year (1 to 365)
        self.solarhour = ini['solarhour']   # local solar hour (not local time!) (hours)
        self.dewtemp = ini['dewtemp']  # dew temperature (deg. C)
        # no. of hours after sunrise when air temperature and wind speed begin to increase
        self.lag = ini['lag']
        self.is_generated = ini['is_generated']  # generate or read in daily weather?
        self.weatherfilename = ini['weatherfilename']  # name of weather file

        # seed for the random number generator:
        if self.seed <= 0:
            self.seed = random.randint(0, 10 ** 12)  # a random seed from 0 to a trillion
        random.seed(self.seed)

        # two options: either generate daily weather values or load them from weather file
        if self.is_generated:
            # simulate weather
            self.annwthr = SimWeather(ini, jsonformat=True)
        else:
            # use weather file
            self.annwthr = WeatherFile(self.weatherfilename)

        self.__a, self.__b = (0.0, 0.0)  # internal variables
        self.nyears = 0    # year number (number of years elapsed)

        # daily properties:
        self.decl = 0.0  # solar declination (radians)
        self.sunrise, self.sunset = (0.0, 0.0)  # hour of sunrise and sunset (hour)
        self.daylen = 0.0  # length of day (hour)
        self.solarconst = 0.0  # solar constant (W/m2)
        self.dayetrad = 0.0  # daily extra-terrestrial (ET) solar irradiance (MJ/m2)
        self.dayrad = SolarRadComponents(0.0, 0.0, 0.0)  # daily solar rad components (MJ/m2)
        self.daytmin = 0.0  # min. daily air temperature (deg. C)
        self.daytmax = 0.0  # max. daily air temperature (deg. C)
        self.daytmean = 0.0  # mean daily air temperature (deg. C)
        self.daywind = 0.0  # daily wind speed (m/s)
        self.dayrain = 0.0  # rainfall amount (mm/day)
        self.doy = doy + 1  # force a weather table update

        # hourly properties:
        self.solarpos = SolarPos(0.0, 0.0, 0.0)  # solar position
        self.etrad = 0.0  # extra-terrestrial (ET) solar irradiance (W/m2)
        self.rad = SolarRadComponents(0.0, 0.0, 0.0)  # solar radiation components (W/m2)
        self.airtemp = 0.0  # air temperature (deg. C)
        self.slopesvp = 0.0  # slope of the saturated air vapor pressure curve (mbar/K)
        self.svp = 0.0  # saturated air vapor pressure (mbar)
        self.vp = 0.0  # air vapor pressure (mbar)
        self.vpd = 0.0  # vapor pressure deficit (mbar)
        self.rh = 0.0  # air relative humidity (%)
        self.netrad = 0.0  # net radiation (W/m2)
        self.windspd = 0.0  # wind speed (m/s)

        # set the day of year and hour, then update the meteorological properties
        self.update_weather(nextdoy=doy, nexthour=self.solarhour)

    @staticmethod
    def rnd():
        """
        !!! note
            `rnd` is a static method.

        Generate a uniform random number between the interval [0 - 1).

        # Returns
            int: random value [0-1)

        """
        return random.random()

    @staticmethod
    def doy365(doy):
        """
        !!! note
            `doy365` is a static method.

        Return a given day of year so that it stays within 1 and 365 inclusive.

        # Returns
            int: day of year [1-365]

        """
        return ((doy - 1) % 365) + 1

    @staticmethod
    def svp_fn(temp):
        """
        !!! note
            `svp_fn` is a static method.

        Saturated vapor pressure (mbar) at a given air temperature (deg. C).

        # Arguments
            temp (float): air temperature (deg. C)

        # Returns
            float: saturated vapor pressure

        """
        return 6.1078 * math.exp(17.269 * temp / (temp + 237.3))

    def solar_declination(self):
        """
        Solar declination (radians).

        # Returns
            float: solar declination

        """
        return -0.4093 * math.cos(0.0172 * (self.doy + 10))

    def _calc_ab(self):
        """
        Internal variables that would be used repeatedly in calculations.

        # Returns
            tuple: intermediary values (`float`)

        """
        a = math.sin(self.lat) * math.sin(self.decl)
        b = math.cos(self.lat) * math.cos(self.decl)
        return a, b

    def sunrise_set_hour(self):
        """
        Hour of sunrise and sunset (hours).

        # Returns
            tuple: local solar hour of sunrise and sunset (`float`)

        """
        tss = 12 + (12 / math.pi) * math.acos(-self.__a / self.__b)  # sunset
        tsr = 24 - tss  # sunrise
        return tsr, tss

    def daylength(self):
        """
        Length of day, between sunrise and sunset (hours).

        # Returns
            float: day length

        """
        return self.sunset - self.sunrise

    def solar_constant(self):
        """
        Solar constant (W/m2), corrected for eccentricity.

        # Returns
            float: solar constant

        """
        return 1370 * (1 + 0.033 * math.cos(0.0172 * (self.doy - 10)))

    def day_et_radiation(self):
        """
        Extra-terrestrial (outside Earth) solar irradiance (MJ/m2/day).

        # Returns
            float: ET solar irradiance

        """
        a, b = self.__a, self.__b
        aob = a / b
        r = 0.027501974 * self.solarconst * (a * math.acos(-aob) + b * math.sqrt(1 - aob ** 2))
        return r

    def day_radiation(self):
        """
        Daily total solar irradiance and its direct and diffuse components (MJ/m2/day).

        # Returns
            SolarRadComponents: `namedtuple` containing the daily solar radiation components
                                (`float`)

        """
        # save the current hour; integration will alter the hour during its calculations
        hour = self.solarhour
        ret = self.integrate(5, self.sunrise, self.sunset, self.radiation)
        self.update_weather(nexthour=hour)  # reset the hour back to its previous value
        return SolarRadComponents(*[val * 3600 / 10 ** 6 for val in ret])  # in MJ/m2/day

    def solar_position(self):
        """
        Solar position: inclination, height (solar elevation), and azimuth (radians).

        # Returns
            SolarPos: `namedtuple` containing position of the sun (`float`)

        """
        ha = (math.pi / 12) * (self.solarhour - 12)  # hour angle
        # solar inclination (from vertical)
        inc = min(math.pi * 0.5, math.acos(self.__a + self.__b * math.cos(ha)))
        hgt = math.pi / 2 - inc  # solar height/elevation (from horizontal)
        a = (math.sin(self.lat) * math.sin(hgt) - math.sin(self.decl))
        a /= math.cos(self.lat) * math.cos(hgt)
        acosa = math.acos(max(-1.0, min(1.0, a)))
        # azimuth is the angle from North in a clockwise direction
        azi = math.pi - acosa if self.solarhour <= 12 else math.pi + acosa
        return SolarPos(inc, hgt, azi)

    def et_radiation(self):
        """
        Instantaneous extra-terrestrial solar irradiance (W/m2).

        # Returns
            float: ET solar radiation

        """
        return max(0.0, self.solarconst * math.cos(self.solarpos.inc))

    def radiation(self):
        """
        Instantaneous total solar irradiance and its direct and diffuse components (W/m2).

        # Returns
            SolarRadComponents: `namedtuple` containing solar radiation components (`float`)

        """
        tau = -0.0112 * self.rh + 1.1857  # atmospheric transmittance
        # optical air mass number (atm. pressure assumed 101 kPa)
        m = 101 / (101.3 * math.cos(self.solarpos.inc))
        kt = tau ** m
        idr = self.etrad * kt  # direct
        idf = 0.3 * (1 - kt) * self.etrad  # diffuse
        it = idr + idf  # total
        return SolarRadComponents(it, idr, idf)

    def air_temperature(self):
        """
        Instantaneous air temperature (deg. C).

        # Returns
            float: air temperature

        """
        # no. of hours after sunrise when air temperature starts to increase from minimum
        lag = self.lag
        tmin, tmax = self.daytmin, self.daytmax
        tsr, tss = self.sunrise, self.sunset
        tset = tmin + (tmax - tmin) * math.sin(math.pi * (tss - tsr - lag) / self.daylen)
        if self.solarhour < (tsr + lag):
            ta = tset + ((tmin - tset) * (self.solarhour + tsr)) / ((tsr + lag) + tsr)
        elif (tsr + lag) <= self.solarhour <= tss:
            n1 = math.pi * (self.solarhour - tsr - lag) / self.daylen
            ta = tmin + (tmax - tmin) * math.sin(n1)
        else:
            ta = tset + ((tmin - tset) * (self.solarhour - tss)) / ((tsr + lag) + tsr)
        return ta

    def saturated_vapor_presure(self):
        """
        Saturated air vapor pressure (mbar).

        # Returns
            float: saturated air vapor pressure

        """
        return Meteo.svp_fn(self.airtemp)

    def slope_svp(self):
        """
        Slope of the saturated air vapor pressure (SVP) against air temperature (mbar/deg. C).

        # Returns
            float: slope of the curve between SVP and air temperature

        """
        n1 = math.exp(17.269 * self.airtemp / (self.airtemp + 237.3))
        n2 = (self.airtemp + 237.3) ** 2
        return 25029.4 * n1 / n2

    def vapor_pressure(self):
        """
        Instantaneous air vapor pressure (mbar).

        # Returns
            float: air vapor pressure

        """
        tdcal = min(self.airtemp, self.dewtemp)
        return Meteo.svp_fn(tdcal)

    def vapor_pressure_deficit(self):
        """
        Air vapor pressure deficit (mbar).

        The difference between saturated air vapor pressure and current air vapor pressure.

        # Returns
            float: air vapor pressure deficit

        """
        return self.svp - self.vp

    def relative_humidity(self):
        """
        Air relative humidity (RH) (%).

        # Returns
            float: RH

        """
        return 100 * self.vp / self.svp

    def net_radiation(self):
        """
        Instantaneous net solar irradiance (W/m2).

        # Returns
            float: net solar radiation

        """
        p = 0.15  # reflection
        stefan_boltzman = 5.67 * 10 ** -8
        tak = self.airtemp + 273.15  # in Kelvin
        # net longwave
        rnl = 0.98 * stefan_boltzman * tak ** 4 * (1.31 * (self.vp / tak) ** (1 / 7) - 1)
        return (1 - p) * self.rad.total + rnl

    def wind_speed(self):
        """
        Instantaneous wind speed (m/s) based on a sine curve.

        # Returns
            float: wind speed

        """
        # no. of hours after sunrise when wind speed starts to increase from minimum
        lag = self.lag
        uday = self.daywind  # mean wind speed for the whole day
        umin = 0.559134814 * uday ** 1.25  # min. wind speed
        umax = 1.797613613 * uday ** 0.75  # max. wind speed
        udelta = umax - umin
        udelta *= math.sin(math.pi * (self.solarhour - self.sunrise - lag) / self.daylen)
        bwithin = (self.sunrise + lag) <= self.solarhour <= (self.sunset + lag)
        # wind speed is larger than the minimum wind speed between (tsr+lag) and (tss+lag) hours
        return (umin + udelta) if bwithin else umin

    def integrate(self, n, lower, upper, func, *args):
        """
        N-point numerical Gaussian integration.

        # Arguments
            n (int): no. of points for integration (min. 1, max, 9; typically, 3 or 5)
            lower (float): lower limit of integration
            upper (float): upper limit of integration
            func: function to be integrated
            args: variable length of function arguments to passed into `func()`

        # Returns
            tuple: results of integration

        """
        # abscissas and weights
        if n == 5:      # most common/used, so place those for n=5 first
            t = (-0.90617985, -0.53846931, 0.0, 0.53846931, 0.90617985)
            w = (0.23692689, 0.47862867, 0.56888888, 0.47862867, 0.23692689)
        elif n == 3:    # next are the odd number of integration points
            t = (-0.77459667, 0.0, 0.77459667)
            w = (0.55555556, 0.88888889, 0.55555556)
        elif n == 7:
            t = (-0.94910791, -0.74153119, -0.40584515, 0.0, 0.40584515, 0.74153119, 0.94910791)
            w = (0.12948497, 0.27970539, 0.38183005, 0.41795918, 0.38183005, 0.27970539, 0.12948497)
        elif n == 9:
            t = (-0.96816024, -0.83603111, -0.61337143, -0.32425342, 0.0,
                 0.32425342, 0.61337143, 0.83603111, 0.96816024)
            w = (0.08127439, 0.18064816, 0.2606107, 0.31234708, 0.33023936,
                 0.31234708, 0.2606107, 0.18064816, 0.08127439)
        elif n == 2:    # even number of integration points
            t = (-0.57735027, 0.57735027)
            w = (1.0, 1.0)
        elif n == 4:
            t = (-0.86113631, -0.33998104, 0.33998104, 0.86113631)
            w = (0.34785485, 0.65214515, 0.65214515, 0.34785485)
        elif n == 6:
            t = (-0.93246951, -0.66120939, -0.23861919, 0.23861919, 0.66120939, 0.93246951)
            w = (0.17132449, 0.36076157, 0.46791393, 0.46791393, 0.36076157, 0.17132449)
        elif n == 8:
            t = (-0.96028986, -0.79666648, -0.52553241, -0.18343464,
                 0.18343464, 0.52553241, 0.79666648, 0.96028986)
            w = (0.10122854, 0.22238103, 0.31370665, 0.36268378,
                 0.36268378, 0.31370665, 0.22238103, 0.10122854)
        else:
            t = (0.0,)  # n = 1 (expect inaccurate results!)
            w = (2.0,)

        alpha_a = (upper + lower) / 2
        alpha_b = (upper - lower) / 2
        total = tuple()
        for i in range(n):
            x = alpha_a + alpha_b * t[i]
            self.update_weather(nexthour=x)
            vals = tuple(v * w[i] * alpha_b for v in func(*args))
            total = tuple(sum(z) for z in zip(vals, total)) if i > 0 else vals
        return total

    def update_weather(self, nextdoy=None, nexthour=None, reuse=False):
        """
        Update the daily (and/or hourly) meteorological properties.

        # Arguments
            nextdoy (int): the new day of year
            nexthour (int/float): the new local solar hour
            reuse (bool): `False` by default so that annual weather will be updated
                          (i.e., regenerated) if the year end has been passed.
                          Set to `True` so that the same annual weather is used
                          regardless if the year end has been passed (i.e., always
                          use the same annual weather data).

        # Returns
            None:

        """
        # update daily properties:
        if nextdoy is not None:
            nextdoy = Meteo.doy365(nextdoy)  # force within [1 to 365]
            if nextdoy < self.doy and not reuse:
                # elapsed into the next/new year:
                self.annwthr.update()
                self.nyears += 1
            self.doy = nextdoy
            self.decl = self.solar_declination()
            self.__a, self.__b = self._calc_ab()
            self.sunrise, self.sunset = self.sunrise_set_hour()
            self.daylen = self.daylength()
            self.solarconst = self.solar_constant()
            self.dayetrad = self.day_et_radiation()
            self.daytmin = self.annwthr('tmin')[self.doy - 1]
            self.daytmax = self.annwthr('tmax')[self.doy - 1]
            self.daywind = self.annwthr('wind')[self.doy - 1]
            self.dayrain = self.annwthr('rain')[self.doy - 1]
            self.daytmean = (self.daytmin + self.daytmax) / 2
            self.dayrad = self.day_radiation()
        # update hourly properties:
        if nexthour is not None:
            self.solarhour = nexthour % 24    # force within [0 to 24)
            self.solarpos = self.solar_position()
            self.airtemp = self.air_temperature()
            self.slopesvp = self.slope_svp()
            self.svp = self.saturated_vapor_presure()
            self.vp = self.vapor_pressure()
            self.vpd = self.vapor_pressure_deficit()
            self.rh = self.relative_humidity()
            self.etrad = self.et_radiation()
            self.rad = self.radiation()
            self.netrad = self.net_radiation()
            self.windspd = self.wind_speed()

    def next_day(self, duration):
        """
        Generator to increment DOY and then update the model properties.

        This class only allows the day of year (DOY) to move forward a day at a time, where each
        time the day moves forward, the model properties are updated.

        # Arguments
            duration (int): number of daily cycles/steps to increment the DOY and model update

        # Yields
            int: current day run number

        """
        param = dict()      # dictionary of function arguments
        if duration > 0:
            # first run is to update the model based on current properties; no change in DOY
            self.update(param)
            yield 0
        # next call (second call onward) is to increment the DOY, then update all model properties
        for i in range(duration - 1):
            self.update_weather(nextdoy=self.doy + 1)  # move day forward by one day
            self.doy_has_changed()  # signal to descendant classes that DOY has changed
            self.update(param)  # now update model properties since DOY has changed
            yield i + 1

    def doy_has_changed(self):
        """
        To be implemented in descendant classes that the DOY has gone forward by a day.

        !!! note
            To be implemented by descendant classes on how the model will be updated when
            the DOY has changed.

        # Raises
            NotImplementedError: raised if this method is used at this base class level

        """
        raise NotImplementedError('Must be implemented by a descendant class.')

    def update(self, external_info):
        """
        To be implemented in descendant classes for updating model properties.

        !!! warning "Implementation"
            To be implemented by descendant classes on how the model will be updated.

        # Arguments
            external_info (dict): information determined from external sources

        # Raises
            NotImplementedError: thrown if this method is used at this base class level

        """
        raise NotImplementedError('Must be implemented by a descendant class.')
