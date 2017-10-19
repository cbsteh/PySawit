"""
AnnualWeather module.

Hold one year of weather data in an ordered dictionary.

# Author - Christopher Teh Boon Sung
------------------------------------

"""


from collections import OrderedDict


class AnnualWeather(object):
    """
    Hold one year weather data in an ordered dictionary (`table` attribute).

    This class is meant to be inherited, so that the update method can be implemented to
    fill in, either by simulation or reading in data from a file, the table with one year of
    weather data. The annual weather data is stored in the attribute table.

    Weather data consist of weather parameters/fields and data sets, where weather
    parameters are names such as 'rain' (for rainfall), 'tmin' (for min. air temperature), 'tmax'
    (for max. air temperature), 'wind' (for wind speed), and so on. The names of these weather
    parameters are provided by users.

    These weather parameters make up one data set. If these data sets represent daily weather
    data, then one year of weather data would have 365 data sets. But this is not necassarily
    always the case. A data set may represent hourly weather data. If this is the case, the
    annual weather data would then have: 365 days/year x 24 hours/day = 8,760 data sets.

    By overriding the `__call__()` method, objects of this class can be called like this:

    ```python
       obj('wind')
    ```

    to retrive the whole year of wind speed data, or

    ```python
        obj('wind')[30]
    ```

    will retrieve the wind speed from the 30th data set. If each data set is daily weather data,
    then this will retrieve the wind speed data for the 30th day.

    And by overriding the `__str__()` method, the entire annual weather data can be printed as a
    formatted output. For instance:

    ```python
        print(obj)
    ```

    prints the entire annual weather data, where every line of output contains each data set.

    # ATTRIBUTES
        nsets (int): Number of data sets that make up a year
        fields (list): List of weather parameters/fields for each data set
        table (OrderedDict): Hold the annual weather data

    # METHODS
        update: Fill in the table attribute with annual weather data. Needs to be implemented
                by the descendant class.

    """

    def __init__(self, nsets, *fields):
        """
        Create and initialize the AnnualWeather object.

        # Arguments
            nsets (int): number of data sets that make up a year
            fields (str): variable length of weather parameters in each data set

        """
        self.nsets = nsets          # number of data sets in a year
        self.fields = fields        # names of weather parameters/fields in each data set
        self.table = OrderedDict()  # holds one year daily weather data
        for field in self.fields:
            self.table.update({field: [0.0 for _ in range(nsets)]})   # initialize all with 0.0

    def __call__(self, field):
        """
        Retrieve the given weather parameter/field.

        Override the `obj()`, so that the object can be called like a method.

        # Example
        ```python
            obj('rain')     # retrieves 'rain' weather parameter for the entire year, but
            obj('rain')[2]  # retrieves 'rain' weather parameter for the second data set.
        ```

        # Arguments
            field (str): name of weather parameter/field, e.g., 'rain', 'wind', or 'tmin'

        # Returns
            list: list of values (`int` or `float`) for a given weather parameter/field

        """
        return self.table[field]

    def __str__(self):
        """
        Format the entire annual weather data as a text/string.

        Allow the `print()` method to output the entire weather data as a formatted output.

        # Returns
            str: formatted string of the annual weather data

        """
        fmt = '{:8.3f},' * len(self.fields)
        fmt = fmt.rstrip(',')
        txt = ''
        for day in range(self.nsets):
            txt += fmt.format(*[self.table[field][day] for field in self.fields])
            txt += '\n'
        return txt

    def update(self):
        """
        Update annual weather table.

        !!! warning "Implementation"
            To be implemented by the descendant class on how the attribute `table` is
            to be filled with weather data.

        # Raises
            NotImplementedError: raised if this method is used at this base class level

        """
        raise NotImplementedError('Must be implemented by a descendant class.')
