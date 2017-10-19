<h1 id="simweather">simweather <em>module</em></h1>


SimWeather module.

Simulates daily weather for min. and max. air temperature, wind speed, and rainfall.

!!! warning "Required installation"
    * [Anaconda](https://www.continuum.io/downloads) for `scipy` for statistics

__Author - Christopher Teh Boon Sung__

------------------------------------


<h2 id="simweather.ParamRain">ParamRain <em>namedtuple</em></h2>

`ParamRain(pww, pwd, shape, scale)`
namedtuple: Rain generation parameters
<h3 id="simweather.ParamRain.pww">pww</h3>

float: probability of two consecutive wet days
<h3 id="simweather.ParamRain.pwd">pwd</h3>

float: probability of a wet day, followed by a dry day
<h3 id="simweather.ParamRain.shape">shape</h3>

float: shape factor of the gamma probability distribution
<h3 id="simweather.ParamRain.scale">scale</h3>

float: scale factor of the gamma probability distribution
<h2 id="simweather.ParamTemp">ParamTemp <em>namedtuple</em></h2>

`ParamTemp(mean, amp, cv, ampcv, meanwet)`
namedtuple: Air temperature generation parameters
<h3 id="simweather.ParamTemp.mean">mean</h3>

float: annual mean air temperature
<h3 id="simweather.ParamTemp.amp">amp</h3>

float: amplitude (highest value - mean value) of air temperature
<h3 id="simweather.ParamTemp.cv">cv</h3>

float: coefficient of variation of air temperature
<h3 id="simweather.ParamTemp.ampcv">ampcv</h3>

float: amplitude (smallest value - mean value) of cv
<h3 id="simweather.ParamTemp.meanwet">meanwet</h3>

float: mean air temperature on days that rained
<h2 id="simweather.ParamWind">ParamWind <em>namedtuple</em></h2>

`ParamWind(shape, scale)`
namedtuple: Wind generation parameters
<h3 id="simweather.ParamWind.shape">shape</h3>

float: shape factor of the Weibull probability distribution
<h3 id="simweather.ParamWind.scale">scale</h3>

float: scale factor of the Weibull probability distribution
<h2 id="simweather.SimWeather">SimWeather <em>class</em></h2>


SimWeather class.

Simulate daily weather for min. and max. air temperatures, wind speed, and rain.

__CLASS ATTRIBUTES__

- `cumulative_days (tuple)`: cumulative number of days for every month

__METHODS__

- `rnd`: Random number generator [0-1)
- `generate_rain`: Daily rainfall amount (mm/day) based on a fitted inverse gamma CDF
- `generate_temperature`: Daily max. and min. air temperatures (deg. C)
- `generate_wind`: Mean daily wind speed (m/s) based on a fitted inverse Weibull distribution
- `update`: Generate (simulate) a new set of daily weather for one year


<h3 id="simweather.SimWeather.__init__"><em>Constructor</em> __init__</h3>

```python
SimWeather(self, infile, jsonformat=False)
```

Create and initialize the SimWeather object.

__Arguments__

- __infile (str/json)__: path and filename of initialization text file
                       or a JSON-formatted string
- __jsonformat (bool)__: `False` if `infile` is a plain text file, or
                       `True` if `infile` is a string in JSON format


<h3 id="simweather.SimWeather.rnd">rnd</h3>

```python
SimWeather.rnd()
```

!!! note
    `rnd` is a static method.

Generate a uniform random number between the interval [0 - 1).

__Returns__

`float`: random value [0-1)


<h3 id="simweather.SimWeather.generate_rain">generate_rain</h3>

```python
SimWeather.generate_rain(self)
```

Determine the daily rainfall amount (mm/day) based on a fitted inverse gamma CDF.

__Returns__

`None`:


<h3 id="simweather.SimWeather.generate_temperature">generate_temperature</h3>

```python
SimWeather.generate_temperature(self)
```

Determine the daily max. and min. air temperatures (deg. C).

__Returns__

`None`:


<h3 id="simweather.SimWeather.generate_wind">generate_wind</h3>

```python
SimWeather.generate_wind(self)
```

Determine the mean daily wind speed (m/s) based on a fitted inverse Weibull distribution.

__Returns__

`None`:


<h3 id="simweather.SimWeather.update">update</h3>

```python
SimWeather.update(self)
```

Generate (simulate) one year of daily weather.

__Returns__

`None`:


