<h1 id="weatherfile">weatherfile <em>module</em></h1>


WeatherFile module.

Read and parse weather data from a text file.

__Author - Christopher Teh Boon Sung__

------------------------------------


<h2 id="weatherfile.WeatherFile">WeatherFile <em>class</em></h2>


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

__ATTRIBUTES__

- `alldata (list)`: List containing the weather data read from the weather file

__METHODS__

- `total_years`:  Number of years for the entire weather data
- `total_datasets`: Number of data sets for the entire weather data
- `load`: Read the whole weather data from a provided weather file and store in `alldata`
- `update`: Load one year of daily data and store them in weather table


<h3 id="weatherfile.WeatherFile.__init__"><em>Constructor</em> __init__</h3>

```python
WeatherFile(self, wthrfile, nsets=365)
```

Create and initialize the WeatherFile object.

__Arguments__

- __wthrfile (str)__: weather file name and path
- __nsets (int)__: no. of data sets in a year


<h3 id="weatherfile.WeatherFile.total_years">total_years</h3>

```python
WeatherFile.total_years(self)
```

Return the number of years for the entire weather data.

__Returns__

`int`: number of years


<h3 id="weatherfile.WeatherFile.total_datasets">total_datasets</h3>

```python
WeatherFile.total_datasets(self)
```

Return the number of data sets for the entire weather data.

__Returns__

`int`: number of data sets


<h3 id="weatherfile.WeatherFile.load">load</h3>

```python
WeatherFile.load(self, wthrfile)
```

Read the entire contents in a given weather file into memory for fast access.

Comments in the weather file are ignored and not stored. The weather file must be in
CSV and plain text format. However, the weather data can also be separated by semicolons.

__Arguments__

- __wthrfile (str)__: the weather file name and path

__Returns__

`None`:


<h3 id="weatherfile.WeatherFile.update">update</h3>

```python
WeatherFile.update(self, year=0)
```

Load one year of daily weather from the weather file.

Refresh the weather table to a specified year.

__Arguments__

- __year (int)__: weather data set for which year number (>= 1) to load into weather
                 table. If `year` <= 0, the next successive year's weather data set
                 will be used.

__Returns__

`None`:


