<h1 id="meteostats">meteostats <em>module</em></h1>


Weather statistics module.

Descriptive statistics of annual and monthly weather data.

!!! warning "Required installation"
    * [Anaconda](https://www.continuum.io/downloads) for `scipy` for statistics

__Author - Christopher Teh Boon Sung__

------------------------------------


<h2 id="meteostats.MeteoStats">MeteoStats <em>class</em></h2>


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

__ATTRIBUTES__

- `metdata (list)`: Annual weather data (list of `OrderedDict` objects)
- `statdict (list)`: 3-D dictionary that hold the results of the statistical values
                     (list of `OrderedDict` objects).

__Example__


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

__METHODS__

- `slice`: Extract a given month's weather data
- `collect`: Create a list that contain all statistical values for a given month,
             parameter, or statistic
- `output_stats`: Print the weather data and their descriptive statistics to file
                  (can append data and descriptive statistics to file).
- `annual_weather`: Return the daily weather for the entire current year


<h3 id="meteostats.MeteoStats.__init__"><em>Constructor</em> __init__</h3>

```python
MeteoStats(self, met)
```

Create and initialize the MeteoStats object.

__Arguments__

- __met (Meteo)__: the Meteo object


<h3 id="meteostats.MeteoStats.slice">slice</h3>

```python
MeteoStats.slice(month)
```

Return the start and end positions in the weather data list for a given month.

__Arguments__

- __month (int)__: 0 to 11 for Jan to Dec, and 12 for whole year

__Returns__

`tuple`: start and end positions (`int`)


<h3 id="meteostats.MeteoStats.collect">collect</h3>

```python
MeteoStats.collect(self, find_month=None, find_param=None, find_stat=None)
```

Collect all values for a given/specified condition.

__Arguments__

- __find_month (int/None)__: month number
- __find_param (str/None)__: name of the weather parameter
- __find_stat (str/None)__: name of the statistic

!!! note
    The `month` list is an zero-based index, so this means
    `month`=0 is Jan, `month`=1 is Feb.,..., `month`=11 is Dec, and
    `month`=12 is for the whole year.

__Returns__

`list`: a list of values, depending on the following example

__Example__


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

__Raises__

- `ValueError`: raised when the no. of arguments passed into this function is not two


<h3 id="meteostats.MeteoStats.output_stats">output_stats</h3>

```python
MeteoStats.output_stats(self, fname, append_to_file=False)
```

Write to file the annual weather data for all years and their statistics.

Also writes to file the raw statistics for every month and year. The name
'-raw' is appended to the fileame of the output txt file.

__Arguments__

- __fname (str)__: path and name of output text file
- __append_to_file (bool)__: `False` (default) to create a new output file, else
                           `True` to append output to an exisiting file

__Returns__

`None`:


<h3 id="meteostats.MeteoStats.annual_weather">annual_weather</h3>

```python
MeteoStats.annual_weather(self)
```

Return the entire daily weather data set for the current year.

__Returns__

`OrderedDict`: annual daily weather


