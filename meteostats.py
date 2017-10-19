"""
Weather statistics module.

Descriptive statistics of annual and monthly weather data.

!!! warning "Required installation"
    * [Anaconda](https://www.continuum.io/downloads) for `scipy` for statistics

# Author - Christopher Teh Boon Sung
------------------------------------

"""


import math
from collections import OrderedDict

from scipy.stats import exponweib
from scipy.stats import gamma
from scipy.stats import rv_continuous

from simweather import SimWeather


class MeteoStats(object):
    """
    Descriptive statistics of annual and monthly weather data.

    Calculate several basic descriptive statistics on the weather parameters:
    ```text
        count
        total
        minimum
        maximum
        average
        amplitude
        standard deviation
        cv (coeff. of variation)
    ```

    The rain parameter has additional statistics:
    ```text
        no. of wet and dry days
    ```

    and the probability of having:

    ```text
        two consecutive dry days P(D|D),
        two consecutive wet days P(W|W),
        a dry day, then a wet day P(W|D),
        a wet day, then a dry day P(D|W),
        a dry day P(D)
        a wet day P(W)
    ```

    This class also fits a gamma probabilty distribution function to the rainfall data, and
    returns the shape and scale of the rainfall distribution. Likewise, this class also fits
    the Weibull probability distribution function to the windspeed data, and returns the
    Weibull shape and scale factors for the windspeed distribution.

    # ATTRIBUTES
        metdata (list): Annual weather data (list of `OrderedDict` objects)
        statdict (list): 3-D dictionary that hold the results of the statistical values
                         (list of `OrderedDict` objects).

    # Example

    ```python
    statdict[month][param][stat] = value
    ```
    thus,

    ```python
    statdict[2]['wind']['avg']
    ```

    returns the average (`avg`) wind speed (`wind`) for `month` = 2.
    Use the `collect()` method to retrieve all statistical values for a given
    condition. See the `collect()` method docmentation on how to use it.

    # METHODS
        slice: Extract a given month's weather data
        collect: Create a list that contain all statistical values for a given month,
                 parameter, or statistic
        output_stats: Print the weather data and their descriptive statistics to file
                      (can append data and descriptive statistics to file).
        annual_weather: Return the daily weather for the entire current year

    """

    def __init__(self, met):
        """
        Create and initialize the MeteoStats object.

        # Arguments
            met (Meteo): the Meteo object

        """
        self.__met = met        # the Meteo object
        self.metdata = None     # list of annual weather data for 1 or more years
        self.statdict = None    # statistical analysis of the annual weather (list)

    @staticmethod
    def slice(month):
        """
        Return the start and end positions in the weather data list for a given month.

        # Arguments
            month (int): 0 to 11 for Jan to Dec, and 12 for whole year

        # Returns
            tuple: start and end positions (`int`)

        """
        s = 0 if (month == 0 or month == 12) else SimWeather.cumulative_days[month - 1]
        e = 365 if month == 12 else SimWeather.cumulative_days[month]
        return s, e

    def _basic_stats(self, field, start_slice, end_slice, exclude_0=False):
        """
        Calculate weather statistics.

        The following statistics are determined

        ```text
            count, sum, min., max., mean, amplitude, standard deviation, and CV
        ```

        # Arguments
            field (str): name of weather parameter
            start_slice (int): start index of weather data (starting day of month)
            end_slice (int): end index of weather data (ending day of month)
            exclude_0 (bool): `True` to remove 0 from weather data (used for rain statistics),
                              else `False` to extract all values including 0

        # Returns
            OrderedDict: weather statistics of given month

        """
        lst = self.metdata[-1][field][start_slice:end_slice]
        # filter out zeroes if instructed
        #    note: the list can be empty or contain only 1 value after filtering (for rain data)
        ar = [val for val in lst if val > 0] if exclude_0 else lst
        n = len(ar)
        # need to check if sufficient data: -999 code means not enough data
        total = sum(ar) if n > 0 else -999      # sum, mean, and range need at least 1 value
        avg = total / n if n > 0 else -999
        ssd = [(val - 1) ** 2 for val in ar] if n > 1 else -999   # variance needs at least 2 values
        stdev = math.sqrt(sum(ssd) / (n - 1)) if n > 1 else -999
        cv = stdev / avg if n > 1 else -999
        mn = min(ar) if n > 0 else -999
        mx = max(ar) if n > 0 else -999
        amp = mx - avg if n > 0 else -999
        return OrderedDict([('count', n), ('total', total), ('min', mn), ('max', mx),
                            ('avg', avg), ('amp', amp), ('sd', stdev), ('cv', cv)])

    def _rain_probs(self, start_slice, end_slice):
        """
        Rain probability statistics.

        Calculate the no. of wet and dry days, the probability of two consecutive
        dry days (PDD), two consecutive wet days (PWW), a dry day, then a wet day (PWD),
        a wet day, then a dry day (PDW), and the probability of a dry day (PD) and a
        wet day (PW).

        # Arguments
            start_slice (int): start index of weather data (starting day of month)
            end_slice (int): end index of weather data (ending day of month)

        # Returns
            OrderedDict: rain statistics

        """
        lst = self.metdata[-1]['rain'][start_slice:end_slice]
        nwd, nww, nd, nw = 0, 0, 0, 0  # no. of wet-dry, wet-wet, dry, and wet days
        numdays = len(lst)  # number of days in a year (365)
        nday = 0
        # count number of dry and wet days; checks two consecutive days per loop cycle
        while nday + 1 < numdays:
            # a rain day if rainfall > 0.0
            rain1 = lst[nday] > 0.0  # any rain on day (t)?
            rain2 = lst[nday + 1] > 0.0  # any rain on the next day (t+1)?
            if not rain1 and rain2:  # a dry day, followed by a wet day
                nwd += 1
            if rain1 and rain2:  # a wet day, followed by another wet day
                nww += 1
            if not rain1:  # count the number of dry days
                nd += 1
            # need to check the rain status on the last day of the year
            #   because this loop checks every two consecutive days (not every day)
            if (nday + 1) == (numdays - 1) and not rain2:
                nd += 1  # the last day of the year is a dry day
            nday += 1
        # finished counting the number of dry and wet days, so now calculate the probabilities:
        nw = numdays - nd
        pwd = nwd / nd  # P(W|D) - dry then wet day
        pww = nww / nw  # P(W|W) - both wet days
        pdd = 1 - pwd  # P(D|D) - both dry days
        pdw = 1 - pww  # P(D|W) - wet then dry day
        pw = nw / numdays  # P(W) - a wet day
        pd = nd / numdays  # P(D) - a dry day
        return OrderedDict([('wetdays', nw), ('drydays', nd), ('p(w|d)', pwd),
                            ('p(d|w)', pdw), ('p(w|w)', pww), ('p(d|d)', pdd),
                            ('p(w)', pw), ('p(d)', pd)])

    def _fit_gamma(self, *args):
        """
        Fit a gamma probability distribution to the rainfall data.

        Estimate the shape and scale parameters for a two-parameter gamma distribution.

        !!! note
            The location gamma parameter is set to zero.

        # Arguments
            args (list): start and end of list (to obtain monthly values, for example)
                        (default is empty to fit the whole wind speed data)

        # Returns
             OrderedDict: shape and scale of the gamma function

        """
        raindata = self.metdata[-1]['rain']
        x = raindata if len(args) == 0 else raindata[args[0]:args[1]]
        x = [v for v in x if v > 0.0]   # fit only to non-zero values (rainfall days)
        # can only fit a gamma function with 2 or more values:
        if len(x) > 1:
            shape, scale = rv_continuous.fit(gamma, x, floc=0)[::2]  # location set to zero
        else:
            shape, scale = (-999, -999)     # error codes
        return OrderedDict([('gamma_shape', shape), ('gamma_scale', scale)])

    def _fit_weibull(self, *args):
        """
        Fit a Weibull probability distribution to the wind speed data.

        Estimate the shape and scale parameters for a two-parameter Weibull distribution.

        # Arguments
            args (list): start and end of list (to obtain monthly values, for example)
                        (default is empty to fit the whole wind speed data)

        # Returns
             OrderedDict: shape and scale of the Weibull function

        """
        winddata = self.metdata[-1]['wind']
        x = winddata if len(args) == 0 else winddata[args[0]:args[1]]
        shape, scale = rv_continuous.fit(exponweib, x, fa=1, floc=0)[1::2]
        return OrderedDict([('weibull_shape', shape), ('weibull_scale', scale)])

    def _collect_months(self, find_param, find_stat):
        """
        Return all the monthly values for a given parameter and statistic.

        # Arguments
            find_param (str): name of weather parameter
            find_stat (str): name of weather statistic

        # Returns
            list: monthly values for a given parameter and statistic

        """
        lst = []
        for params in self.statdict[-1].values():
            for param, stats in params.items():
                for stat, val in stats.items():
                    if param == find_param and stat == find_stat:
                        lst.append(val)
        return lst

    def _collect_stats(self, find_month, find_param):
        """
        Return all the statistical values for a given month and parameter.

        # Arguments
            find_month (int): month number
            find_param (str): name of weather parameter

        # Returns
            list: statistical values for a given month and parameter

        """
        lst = []
        for month, params in self.statdict[-1].items():
            for param, stats in params.items():
                if month == find_month and param == find_param:
                    for val in stats.values():
                        lst.append(val)
        return lst

    def _collect_params(self, find_month, find_stat):
        """
        Return all the parameter values for a given month and statistic.

        # Arguments
            find_month (int): month number
            find_stat (str): name of statistic

        # Returns
            list: statistical values for a given month and statistic

        """
        lst = []
        for month, params in self.statdict[-1].items():
            for stats in params.values():
                for stat, val in stats.items():
                    if month == find_month and stat == find_stat:
                        lst.append(val)
        return lst

    def collect(self, find_month=None, find_param=None, find_stat=None):
        """
        Collect all values for a given/specified condition.

        # Arguments
            find_month (int/None): month number
            find_param (str/None): name of the weather parameter
            find_stat (str/None): name of the statistic

        !!! note
            The `month` list is an zero-based index, so this means
            `month`=0 is Jan, `month`=1 is Feb.,..., `month`=11 is Dec, and
            `month`=12 is for the whole year.

        # Returns
            list: a list of values, depending on the following example

        # Example

        ```text
        Specified                   Returns (as a list)
        ------------------------------------------------------------------------------
        parameter and statistic     all monthly values
          e.g.,
          find_param = 'tmin'         returns every month's average (find_stat='avg')
          find_stat = 'avg'           min. air temperature (find_param='tmin')

        month and parameter         all statistical values
          e.g.,
          find_month = 1              returns all the statistical values for max.
          find_param = 'tmax'         air temperature (find_param='tmax') for Feb.
                                      (note: zero-based index, so, find_month=1 is Feb.).

                                      Statistics related to max. air temperature are:
                                      count, total, min., max., avg, amp, and cv (those
                                      returned by function _basic_stats), but for
                                      find_param='rain', the statistics related to rain
                                      are those returned by functions _basic_stats and
                                      _rain_stats (i.e., rain has more statistics than
                                      max. air temperature).

        month and stat              all parameter values
          e.g.,
          find_month = 3              returns the minimum (find_stat='min') values for
          find_stat = 'min'           all of April's (find_month=3) parameters,
                                      such as: 'tmin', 'tmax', 'wind', and 'rain'.
        ```

        # Raises
            ValueError: raised when the no. of arguments passed into this function is not two

        """
        # Two (and only two) arguments must be supplied
        if [find_month, find_param, find_stat].count(None) != 1:
            raise ValueError('Requires two (and only two) arguments.')

        if [find_month, find_param].count(None) == 0:
            return self._collect_stats(find_month, find_param)
        elif [find_month, find_stat].count(None) == 0:
            return self._collect_params(find_month, find_stat)
        else:
            return self._collect_months(find_param, find_stat)

    def _paramlist(self):
        """
        Determine what parameters to show.

        # Returns
            list: weather parameters

        """
        dct = OrderedDict()
        for params in self.statdict[-1].values():
            for param in params.keys():
                dct[param] = 0
        return list(dct.keys())

    def _statlist(self):
        """
        Determine what data to show.

        # Returns
            list: statistic parameters

        """
        dct = OrderedDict()
        for params in self.statdict[-1].values():
            for stats in params.values():
                for stat in stats.keys():
                    dct[stat] = 0
        return list(dct.keys())

    def _update_stats(self):
        """
        Perform all statistics on the weather data.

        # Returns
            None:

        """
        self.metdata.append(self.annual_weather())   # weather data for current year
        self.statdict.append(OrderedDict())          # new set of statistics results
        for nmth in range(13):  # index 0 to 11: Jan to Dec, index 12: whole year
            s, e = MeteoStats.slice(nmth)
            self.statdict[-1][nmth] = OrderedDict()
            # statistics for every weather parameter:
            for f in self.metdata[-1].keys():
                self.statdict[-1][nmth][f] = OrderedDict(self._basic_stats(f, s, e, f == 'rain'))
            # additional statistics for the rain parameter:
            self.statdict[-1][nmth]['rain'].update(self._rain_probs(s, e))
            self.statdict[-1][nmth]['rain'].update(self._fit_gamma(s, e))
            # additional statistics for the wind parameter:
            self.statdict[-1][nmth]['wind'].update(self._fit_weibull(s, e))

    def _write_stats(self, fname, append_to_file=False):
        """
        Write to file the annual weather data for current year and their statistics.

        Also writes to file the raw statistics for every month and year. The name
        '-raw' is appended to the fileame of the output txt file.

        # Arguments
            fname (str): path and name of output text file
            append_to_file (bool): `False` (default) to create a new output file, else
                                   `True` to append output to an exisiting file

        # Returns
            None:

        """
        def _are_all_ints():
            """Return True if all values in a list are integers."""
            bintegers = True  # assume all integers first
            for strval in flst:
                try:
                    sv = str(strval)
                    int(sv)  # will throw exception if conversion fails
                    if sv.find('.') >= 0:
                        bintegers = False  # found a decimal, so assume it is a float
                        break  # exit loop since not all are integers
                except ValueError:
                    bintegers = False  # at least one item in the list is not a number
                    break  # exit loop
            return bintegers

        self._update_stats()    # perform all the statistics calculations
        paramlst = self._paramlist()    # get the full list of parameters
        statlst = self._statlist()      # get the full list of statistics

        nspan = 15  # width (no. of spaces) for each column
        mode = 'w' if not append_to_file else 'a'
        with open(fname, mode) as fout:
            fout.write('## Year no. {0}:\n'.format(self.__met.nyears))
            # print to file the column headings and format the data for each column:
            nfields = len(paramlst)
            txt = '{:>' + str(nspan) + 's},'
            txt += (('{:>' + str(nspan) + 's},') * nfields).rstrip(',') + '\n'
            fout.write(txt.format(*list(['doy', ] + [field for field in paramlst])))
            txt = '{:>' + str(nspan) + 'd},'
            txt += (('{:>' + str(nspan) + '.3f},') * nfields).rstrip(',') + '\n'

            # print to file the weather parameters for each day of the year:
            gw = self.metdata[-1]
            for day in range(365):
                lss = list([day + 1, ] + [gw[field][day] for field in paramlst])
                fout.write(txt.format(*lss))

            # print to file the statistics for every weather parameter:
            txt = '\n\nSUMMARY OF EACH MONTH AND WHOLE YEAR:\n'
            txt += (('{:>' + str(nspan) + 's},') * 15).rstrip(',') + '\n'
            fout.write(txt.format('PARAM', 'STAT',
                                  *['MONTH ' + str(n + 1) for n in range(12)], 'ALL'))
            txt = ('{:>' + str(nspan) + 's},') * 2
            txt_d = txt + (('{:>' + str(nspan) + 'd},') * 13).rstrip(',') + '\n'
            txt_f = txt + (('{:>' + str(nspan) + '.3f},') * 13).rstrip(',') + '\n'
            for p in paramlst:
                for s in statlst:
                    flst = self._collect_months(p, s)
                    if flst:  # write only if stat found
                        if _are_all_ints():
                            fout.write(txt_d.format(*[p, s], *flst))
                        else:
                            fout.write(txt_f.format(*[p, s], *flst))
                fout.write('\n')  # additional line separator between two different parameters

        # write the raw statistics data to another file (CSV text file):
        ndot = fname.rfind('.')     # find '.' for any file extension
        # '.' location must not precede back or forward slash
        if ndot > 0 and (fname.rfind('\\') < ndot or fname.rfind('/') < ndot):
            fnameraw = "{0}-{2}.{1}".format(*fname.rsplit('.', 1) + ['raw'])
        else:
            fnameraw = fname + "-raw"

        with open(fnameraw, mode) as fout:
            if not append_to_file:
                # write the column headers/titles:
                txt = 'year,month'
                # retrieve the statistics name for every weather parameter
                for param, vals in self.statdict[-1][0].items():
                    for stat in vals.keys():
                        txt += ',' + param + '_' + stat
                fout.write(txt + '\n')

            # now write the raw data:
            for mth in range(13):
                fout.write('{},{}'.format(self.__met.nyears, mth+1))
                for p in paramlst:
                    statlst = self._collect_stats(mth, p)
                    if statlst:
                        txt = ',{}' * len(statlst)
                        fout.write(txt.format(*[stat for stat in statlst]))
                fout.write('\n')

    def output_stats(self, fname, append_to_file=False):
        """
        Write to file the annual weather data for all years and their statistics.

        Also writes to file the raw statistics for every month and year. The name
        '-raw' is appended to the fileame of the output txt file.

        # Arguments
            fname (str): path and name of output text file
            append_to_file (bool): `False` (default) to create a new output file, else
                                   `True` to append output to an exisiting file

        # Returns
            None:

        """
        self.metdata = []       # reset lists
        self.statdict = []
        met = self.__met
        if met.is_generated:
            # weather is generated per year, so just do stats for this current year
            self._write_stats(fname, append_to_file)
        else:
            # weather is from file, and weather could be for several years
            numyears = int(met.annwthr.total_years())      # no. of years
            # save current position in weather data
            savedyear = met.nyears
            saveddoy = met.doy
            # do stats for each year:
            for yr in range(numyears):
                met.annwthr.update(yr)
                met.nyears = yr + 1
                bappend = append_to_file if yr == 0 else numyears > 1
                self._write_stats(fname, bappend)
            # restore to previous position in weather table
            met.annwthr.update(savedyear)
            met.nyears = savedyear
            met.update_weather(nextdoy=saveddoy, reuse=True)

    def annual_weather(self):
        """
        Return the entire daily weather data set for the current year.

        # Returns
            OrderedDict: annual daily weather

        """
        met = self.__met
        current_doy = met.doy    # save current DOY to reset later
        # get all weather fields from annual weather and add new ones
        annwthr = OrderedDict()
        fields = [field for field in met.annwthr.fields] + ['totrad', 'drrad', 'dfrad']
        for field in fields:
            annwthr.update({field: [0.0 for _ in range(365)]})
        # do weather for whole year
        for i in range(365):
            met.update_weather(nextdoy=i + 1, reuse=True)
            annwthr['totrad'][i], annwthr['drrad'][i], annwthr['dfrad'][i] = met.dayrad
            for field in met.annwthr.fields:
                annwthr[field][i] = met.annwthr(field)[i]
        # reset to previous state before updating the weather table:
        met.update_weather(nextdoy=current_doy, reuse=True)
        return annwthr
