<h1 id="annualweather">annualweather <em>module</em></h1>


AnnualWeather module.

Hold one year of weather data in an ordered dictionary.

__Author - Christopher Teh Boon Sung__

------------------------------------


<h2 id="annualweather.AnnualWeather">AnnualWeather <em>class</em></h2>


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

__ATTRIBUTES__

- `nsets (int)`: Number of data sets that make up a year
- `fields (list)`: List of weather parameters/fields for each data set
- `table (OrderedDict)`: Hold the annual weather data

__METHODS__

- `update`: Fill in the table attribute with annual weather data. Needs to be implemented
            by the descendant class.


<h3 id="annualweather.AnnualWeather.__init__"><em>Constructor</em> __init__</h3>

```python
AnnualWeather(self, nsets, *fields)
```

Create and initialize the AnnualWeather object.

__Arguments__

- __nsets (int)__: number of data sets that make up a year
- __fields (str)__: variable length of weather parameters in each data set


<h3 id="annualweather.AnnualWeather.update">update</h3>

```python
AnnualWeather.update(self)
```

Update annual weather table.

!!! warning "Implementation"
    To be implemented by the descendant class on how the attribute `table` is
    to be filled with weather data.

__Raises__

- `NotImplementedError`: raised if this method is used at this base class level


