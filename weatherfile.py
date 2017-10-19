"""
WeatherFile module.

Read and parse weather data from a text file.

# Author - Christopher Teh Boon Sung
------------------------------------

"""

import re
from collections import OrderedDict

from annualweather import AnnualWeather


class WeatherFile(AnnualWeather):
    """
    Weather file class to read and parse weather data from a given weather file.

    Given a weather file (comma-delimited and plain text file format), this class loads the file,
    reads, then parses the file content for the weather data. The weather data is then stored in a
    dictionary instance attribute named `data`.

    The weather file (in this case, we will name the file "weather.txt") must follow the
    following format (in plain text file):

    ```text
        # lines starting with hash (#) are comments (comments are optional)
        # sample weather data in "weather.txt"
        *doy,sunhr,tmax,tmin,rh,wind,rain
        1,5.95,31.4,22,87,1.04,0
        2,5.1,32.7,21.9,96,1.02,0
        ...
        364,5.5,31.7,20.5,95,0.73,0.4
        365,8.05,32,20.6,96,0.58,0
    ```

    where the data are separated by commas. The first two rows of the file begins with the `#`
    character, which denotes these two lines are comments. You can have as many comment lines in
    a weather file as you like, so long as you start the line for each comment with `#`. Comments
    are ignored by this class. Note: comments, if any, must only appear at the beginning of the
    file. However, you cannot have comments within the weather data or at the end of the file.

    After the comment lines, you will list down the weather data, where the data are separated
    commas. The third line in the "weather.txt" above contains the column headers, where "doy" is
    the day of year, "sunhr" is the sunshine hours, "tmax" and "tmin" are the maximum and minimum
    air temperature, respectively, "wind" is the wind speed, and "rain" is the rainfall amount.

    Column headers are mandatory because they indicate what kind of data are being stored.
    Header names are user-defined and need not follow the example in "weather.txt". For example,
    you can have column headers named "year", "month", and "day" to indicate the year,
    month, and day, respectively. You can even use "rainfall" as the header for rain, instead of
    "rain", as used in the "weather.txt" file example. Please note that header names are
    case-sensitive, so column headers "rain", "Rain", and "RAIN" are not the same to one another.

    Note the symbol `*` in front of "doy" column header in "weather.txt". This symbol `*`
    indicates that "doy" is the key used to search for weather data. So, if we want to search for
    the weather data when the day of year is 2 (doy==2), this class will return
    "5.1,32.7,21.9,96,1.02,0" (see the fifth row in "weather.txt" above).

    This class will read the file from top to bottom, so once we reached the end of the weather
    data, the class will 'rewind' so that data search begins again from the top. So, after
    searching the weather data for doy==365, and if the data have been exhausted, the next call to
    search for the weather data for doy==1 will return "5.95,31.4,22,87,1.04,0" (see fourth row in
    "weather.txt" above).

    You can have as many keys as you want, so long as you precede the column headers with `*`.
    In this example, we have created three keys:

    ```text
        # "weather2.txt"
        *year,*month,*day,doy,sunhr,tmax,tmin,rh,wind,rain
        1990,1,1,1,5.95,31.4,22,87,1.04,0
        1990,1,2,2,5.1,32.7,21.9,96,1.02,0
        ...
    ```

    so that "year", "month", and "day" are keys that will be used to search for the weather data.
    Keys do not need to be consecutively arranged or even begin the header line. For instance,

    ```text
        # "weather3.txt"
        sunhr,*doy,tmax,tmin,rh,wind,rain,*year
        5.95,1,31.4,22,87,1.04,0,1990
        5.1,2, 32.7,21.9,96,1.02,0,1990
        ...
    ```

    where you now have two keys ("doy" and "year'), and these keys are not arranged consecutively
    and do not start the header line.

    Lastly, the weather data need not be for 1 year. You can place two or more years' worth of
    weather, such as:

    ```text
        # "weather4.txt"
        *doy,sunhr,tmax,tmin,rh,wind,rain
        1,5.95,31.4,22,87,1.04,0
        2,5.1,32.7,21.9,96,1.02,0
        ...
        364,5.5,31.7,20.5,95,0.73,0.4
        365,8.05,32,20.6,96,0.58,0
        1,2.1,31.4,22.1,100,0.75,1.3
        2,4.15,31.9,22.1,91,0.74,50.6
        ...
        1,5,31.1,19.9,91,0.64,3.6
        2,3,31.5,20.2,96,0.71,32.7
        ...
    ```

    Again, as mentioned earlier, if the weather data set have been exhausted, the class will
    'rewind' the search back from the start. This is useful when you want to reuse the same
    weather data set repeatedly in simulation runs (e.g., running a 20-year simulation time
    with only one year of weather data set).

    # ATTRIBUTES
        alldata (list): List containing the weather data read from the weather file

    # METHODS
        total_years:  Number of years for the entire weather data
        total_datasets: Number of data sets for the entire weather data
        load: Read the whole weather data from a provided weather file and store in `alldata`
        update: Load one year of daily data and store them in weather table

    """

    def __init__(self, wthrfile, nsets=365):
        """
        Create and initialize the WeatherFile object.

        # Arguments
             wthrfile (str): weather file name and path
             nsets (int): no. of data sets in a year

        """
        self.alldata = None  # stores the full weather data in a table
        # internal use attributes:
        self.__curdata = None  # holds weather data for current day
        self.__keys = None  # the keys (one or more) used to find weather data
        self.__vals = None  # non-keys headers which will be used as weather fields
        self.__pos = None  # the current position in the full weather data storage
        self.__headers = None  # column headers obtained from weather file
        self.load(wthrfile)
        AnnualWeather.__init__(self, nsets, *self.__vals)

    def _readline(self):
        """
        Read the next set of weather data from the table.

        # Returns
            None:

        """
        sz = len(self.__headers)
        endpos = self.__pos + sz + 1
        self.__curdata = OrderedDict(zip(self.__headers, self.alldata[self.__pos:endpos]))
        self.__pos += sz
        if self.__pos >= len(self.alldata):
            self.__pos = 0

    def _findkeys(self, char='*'):
        """
        Identify which column headers read from the weather file are keys.

        # Arguments
             char (str): symbol or character to indicate key (default '*')

        !!! note
            There can be more than one key, and keys are identified by
            headers marked with a symbol, '*' by default

        # Returns
            None:

        """
        self.__keys = []  # reset/clear
        self.__vals = []
        n = 0  # start with the first header
        bfound_at_least_one_key = False  # need to find at least one key
        while n < len(self.__headers):
            bfound = self.__headers[n][0] == char
            if bfound:
                bfound_at_least_one_key = True  # found at least one key
                self.__headers[n] = self.__headers[n][1:]  # rid the key identifier *
                self.__keys.append(self.__headers[n])
            else:
                self.__vals.append(self.__headers[n])   # add to non-key list
            n += 1  # find all keys until no more headers left
        if not bfound_at_least_one_key:
            # no keys found, so assume first column data is the key
            self.__keys.append(self.__headers[0])
            del self.__vals[0]  # first column is taken as key, so delete it from non-keys

    @staticmethod
    def _type(strval):
        """
        !!! note
            `_type` is a static method.

        Determine if a string can be converted into a number (float or integer).

        Weather data in a file may not all be numbers (integers and floats). Dates, for
        instance, can be a string, such as "12/1/1990" for Jan. 12, 1990. This function
        checks and converts an object into an `int` or `float`, if it is possible. Otherwise, it
        leaves the object as it is (no conversion).

        # Arguments
            strval (str): the string to be converted into a number (`int` or `float`)

        # Returns
            float/int/str: type returned after conversion

        """
        try:
            f = float(strval)  # throws ValueError if the string cannot be converted into a number
            if strval.find('.') >= 0:
                return f  # found a decimal point, so it is a float
            else:
                return int(strval)  # no decimal point found, so assume it is an integer
        except ValueError:
            return strval  # string cannot be converted into a number, so return it as-is

    def total_years(self):
        """
        Return the number of years for the entire weather data.

        # Returns
           int: number of years

        """
        return len(self.alldata) / len(self.__headers) / self.nsets

    def total_datasets(self):
        """
        Return the number of data sets for the entire weather data.

        # Returns
            int: number of data sets

        """
        return len(self.alldata) / len(self.__headers)

    def load(self, wthrfile):
        """
        Read the entire contents in a given weather file into memory for fast access.

        Comments in the weather file are ignored and not stored. The weather file must be in
        CSV and plain text format. However, the weather data can also be separated by semicolons.

        # Arguments
            wthrfile (str): the weather file name and path

        # Returns
            None:

        """
        # remove all whitespaces (newlines, tabs, and spaces), then tokenize base on ',' or ';'
        with open(wthrfile, 'rt') as fwthr:
            line = ''
            # ignore all blank and comment lines on top of file
            while line == '' or line[0] == '#':
                line = fwthr.readline().lstrip()
            # first non-blank or non-comment line is encountered and assumed to hold the column
            #    headers, so remove all leading and trailing whitespaces, then tokenize based on
            #    comma or semicolon
            self.__headers = [h.strip() for h in re.split(r'[,;]', line)]
            # now identify which headers are the keys
            self._findkeys()  # keys are assumed those headers marked with '*'
            self.alldata = []  # clear the weather table for new data
            self.__pos = 0  # current read position in weather table is reset
            # read in the entire weather file into memory (table)
            for data in fwthr:
                lst = [d.strip() for d in re.split(r'[,;]', data)]
                self.alldata += [WeatherFile._type(strval) for strval in lst]

    def update(self, year=0):
        """
        Load one year of daily weather from the weather file.

        Refresh the weather table to a specified year.

        # Arguments
             year (int): weather data set for which year number (>= 1) to load into weather
                         table. If `year` <= 0, the next successive year's weather data set
                         will be used.

        # Returns
            None:

        """
        if year > 0:
            nheaders = len(self.__headers)
            ndata = len(self.alldata)
            self.__pos = ((year - 1) * self.nsets * nheaders) % ndata
        for iday in range(self.nsets):
            self._readline()
            for field in self.fields:
                self.table[field][iday] = self.__curdata[field]
