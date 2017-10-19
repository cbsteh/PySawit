<h1 id="meteo">meteo <em>module</em></h1>


Meteorological module.

Daily and hourly (instantaneous) meteorology properties.

__Author - Christopher Teh Boon Sung__

------------------------------------


<h2 id="meteo.SolarRadComponents">SolarRadComponents <em>namedtuple</em></h2>

`SolarRadComponents(total, direct, diffuse)`
namedtuple: Solar radiation components
<h3 id="meteo.SolarRadComponents.total">total</h3>

float: total solar radiation (direct + diffuse)
<h3 id="meteo.SolarRadComponents.direct">direct</h3>

float: direct solar radiation
<h3 id="meteo.SolarRadComponents.diffuse">diffuse</h3>

float: diffuse solar radiation
<h2 id="meteo.SolarPos">SolarPos <em>namedtuple</em></h2>

`SolarPos(inc, hgt, azi)`
namedtuple: Solar position
<h3 id="meteo.SolarPos.inc">inc</h3>

float: solar inclination (angle from vertical)
<h3 id="meteo.SolarPos.hgt">hgt</h3>

float: solar elevation or height (angle from horizontal)
<h3 id="meteo.SolarPos.azi">azi</h3>

float: solar azimuth (angle from North in a clockwise direction)
<h2 id="meteo.Meteo">Meteo <em>class</em></h2>


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

__ATTRIBUTES__

- `seed (int)`: Random seed number
- `lat (float)`: Site latitude (deg.)
    methgt (float)- Weather station height (m)
- `doy (int)`: Day of year (Jan 1 = 1, Feb 1 = 32, ..., Dec 31 = 365)
- `solarhour (float)`: Local solar hour (not local time!) (hours)
- `dewtemp (float)`: Dew temperature (deg. C)
- `lag (float)`: No. of hours after sunrise when air temperature
                 and wind speed are minimum (hours)
- `is_generated (bool)`: `True` to generate daily weather or `False` to read in daily weather
- `weatherfilename (str)`: Name of weather file
- `annwthr (AnnualWeather)`: Annual daily weather data for current year
- `nyears (int)`: Year number (number of years elapsed)
- `decl (float)`: Solar declination (radians)
- `sunrise (float)`: Local solar hour of sunrise (hour)
- `sunset (float)`: Local solar hour of sunset (hour)
- `daylen (float)`: Length of day (hour)
- `solarconst (float)`: Solar constant (W/m2)
- `dayetrad (float)`: Daily extra-terrestrial (ET) solar irradiance (MJ/m2)
- `dayrad (SolarRadComponents)`: Daily solar rad components (MJ/m2)
- `daytmin (float)`: Min. daily air temperature (deg. C)
- `daytmax (float)`: Max. daily air temperature (deg. C)
- `daytmean (float)`: Mean daily air temperature (deg. C)
- `daywind (float)`: Daily wind speed (m/s)
- `dayrain (float)`: Rainfall amount (mm/day)
- `solarpos (SolarPos)`: Solar position (inclination and azimuth) (radians)
- `etrad (float)`: Extra-terrestrial (ET) solar irradiance (W/m2)
- `rad (SolarRadComponents)`: Solar radiation components (W/m2)
- `airtemp (float)`: Air temperature (deg. C)
- `slopesvp (float)`: Slope of the saturated air vapor pressure curve (mbar/K)
- `svp (float)`: Saturated air vapor pressure (mbar)
- `vp (float)`: Air vapor pressure (mbar)
- `vpd (float)`: Vapor pressure deficit (mbar)
- `rh (float)`: Air relative humidity (%)
- `netrad (float)`: Net radiation (W/m2)
- `windspd (float)`: Wind speed (m/s)

__METHODS__

- `doy365`: Forces the day of year to stay within 1 and 365 inclusive
- `rnd`: Random number, needs to be seeded by the user or computer
- `svp_fn`: Saturated air vapor pressure for a given air temperature (mbar)
- `solar_declination`: Solar declination (radians)
- `sunrise_set_hour`: Local solar hour of sunrise and sunset (hours)
- `daylength`: No. of hours between sunrise and sunset (hours)
- `solar_constant`: Solar irradiance outside Earth (W/m2)
- `day_et_radiation`: Daily total extraterrestrial solar irradiance (MJ/m2/day)
- `day_radiation`: Daily direct, diffuse, and total solar irradiance (MJ/m2/day)
- `solar_position`: Inclination, height, and azimuth of the Sun (radians)
- `et_radiation`: Instantaneous extraterrestrial solar irradiance (W/m2)
- `radiation`: Instantaneous direct, diffuse, and total solar irradiance (W/m2)
- `air_temperature`: Instantaneous air temperature (deg. C)
- `svp`: Saturated air vapor pressure (mbar)
- `slope_svp`: Slope of the saturated air vapor pressure (mbar/deg. C)
- `vapor_pressure`: Air vapor pressure (mbar)
- `vapor_pressure_deficit`: Vapor pressure deficit (mbar)
- `relative_humidity`: Relative humidity (%)
- `net_radiation`: Net radiation (W/m2)
- `wind_speed`: Wind speed (m/s)
- `integrate`: N-point numerical Gaussian integration
- `update_weather`: Update daily weather when day of year and/or local solr hour have changed
- `next_day`: Generator to increment DOY and then update the model properties

- `doy_has_changed`: To be implemented in descendant classes that day of year has changed
- `update`: To be implemented in descendant classes for updating model properties based on
             current model settings or values


<h3 id="meteo.Meteo.__init__"><em>Constructor</em> __init__</h3>

```python
Meteo(self, fname_in)
```

Create and initialize the Weather object.

__Arguments__

- __fname_in (str)__: path and filename of the model initialization file


<h3 id="meteo.Meteo.rnd">rnd</h3>

```python
Meteo.rnd()
```

!!! note
    `rnd` is a static method.

Generate a uniform random number between the interval [0 - 1).

__Returns__

`int`: random value [0-1)


<h3 id="meteo.Meteo.doy365">doy365</h3>

```python
Meteo.doy365(doy)
```

!!! note
    `doy365` is a static method.

Return a given day of year so that it stays within 1 and 365 inclusive.

__Returns__

`int`: day of year [1-365]


<h3 id="meteo.Meteo.svp_fn">svp_fn</h3>

```python
Meteo.svp_fn(temp)
```

!!! note
    `svp_fn` is a static method.

Saturated vapor pressure (mbar) at a given air temperature (deg. C).

__Arguments__

- __temp (float)__: air temperature (deg. C)

__Returns__

`float`: saturated vapor pressure


<h3 id="meteo.Meteo.solar_declination">solar_declination</h3>

```python
Meteo.solar_declination(self)
```

Solar declination (radians).

__Returns__

`float`: solar declination


<h3 id="meteo.Meteo.sunrise_set_hour">sunrise_set_hour</h3>

```python
Meteo.sunrise_set_hour(self)
```

Hour of sunrise and sunset (hours).

__Returns__

`tuple`: local solar hour of sunrise and sunset (`float`)


<h3 id="meteo.Meteo.daylength">daylength</h3>

```python
Meteo.daylength(self)
```

Length of day, between sunrise and sunset (hours).

__Returns__

`float`: day length


<h3 id="meteo.Meteo.solar_constant">solar_constant</h3>

```python
Meteo.solar_constant(self)
```

Solar constant (W/m2), corrected for eccentricity.

__Returns__

`float`: solar constant


<h3 id="meteo.Meteo.day_et_radiation">day_et_radiation</h3>

```python
Meteo.day_et_radiation(self)
```

Extra-terrestrial (outside Earth) solar irradiance (MJ/m2/day).

__Returns__

`float`: ET solar irradiance


<h3 id="meteo.Meteo.day_radiation">day_radiation</h3>


Daily total solar irradiance and its direct and diffuse components (MJ/m2/day).

__Returns__

`SolarRadComponents`: `namedtuple` containing the daily solar radiation components
                        (`float`)


<h3 id="meteo.Meteo.solar_position">solar_position</h3>


Solar position: inclination, height (solar elevation), and azimuth (radians).

__Returns__

`SolarPos`: `namedtuple` containing position of the sun (`float`)


<h3 id="meteo.Meteo.et_radiation">et_radiation</h3>

```python
Meteo.et_radiation(self)
```

Instantaneous extra-terrestrial solar irradiance (W/m2).

__Returns__

`float`: ET solar radiation


<h3 id="meteo.Meteo.radiation">radiation</h3>


Instantaneous total solar irradiance and its direct and diffuse components (W/m2).

__Returns__

`SolarRadComponents`: `namedtuple` containing solar radiation components (`float`)


<h3 id="meteo.Meteo.air_temperature">air_temperature</h3>

```python
Meteo.air_temperature(self)
```

Instantaneous air temperature (deg. C).

__Returns__

`float`: air temperature


<h3 id="meteo.Meteo.saturated_vapor_presure">saturated_vapor_presure</h3>

```python
Meteo.saturated_vapor_presure(self)
```

Saturated air vapor pressure (mbar).

__Returns__

`float`: saturated air vapor pressure


<h3 id="meteo.Meteo.slope_svp">slope_svp</h3>

```python
Meteo.slope_svp(self)
```

Slope of the saturated air vapor pressure (SVP) against air temperature (mbar/deg. C).

__Returns__

`float`: slope of the curve between SVP and air temperature


<h3 id="meteo.Meteo.vapor_pressure">vapor_pressure</h3>

```python
Meteo.vapor_pressure(self)
```

Instantaneous air vapor pressure (mbar).

__Returns__

`float`: air vapor pressure


<h3 id="meteo.Meteo.vapor_pressure_deficit">vapor_pressure_deficit</h3>

```python
Meteo.vapor_pressure_deficit(self)
```

Air vapor pressure deficit (mbar).

The difference between saturated air vapor pressure and current air vapor pressure.

__Returns__

`float`: air vapor pressure deficit


<h3 id="meteo.Meteo.relative_humidity">relative_humidity</h3>

```python
Meteo.relative_humidity(self)
```

Air relative humidity (RH) (%).

__Returns__

`float`: RH


<h3 id="meteo.Meteo.net_radiation">net_radiation</h3>

```python
Meteo.net_radiation(self)
```

Instantaneous net solar irradiance (W/m2).

__Returns__

`float`: net solar radiation


<h3 id="meteo.Meteo.wind_speed">wind_speed</h3>

```python
Meteo.wind_speed(self)
```

Instantaneous wind speed (m/s) based on a sine curve.

__Returns__

`float`: wind speed


<h3 id="meteo.Meteo.integrate">integrate</h3>

```python
Meteo.integrate(self, n, lower, upper, func, *args)
```

N-point numerical Gaussian integration.

__Arguments__

- __n (int)__: no. of points for integration (min. 1, max, 9; typically, 3 or 5)
- __lower (float)__: lower limit of integration
- __upper (float)__: upper limit of integration
- __func__: function to be integrated
- __args__: variable length of function arguments to passed into `func()`

__Returns__

`tuple`: results of integration


<h3 id="meteo.Meteo.update_weather">update_weather</h3>

```python
Meteo.update_weather(self, nextdoy=None, nexthour=None, reuse=False)
```

Update the daily (and/or hourly) meteorological properties.

__Arguments__

- __nextdoy (int)__: the new day of year
- __nexthour (int/float)__: the new local solar hour
- __reuse (bool)__: `False` by default so that annual weather will be updated
                  (i.e., regenerated) if the year end has been passed.
                  Set to `True` so that the same annual weather is used
                  regardless if the year end has been passed (i.e., always
                  use the same annual weather data).

__Returns__

`None`:


<h3 id="meteo.Meteo.next_day">next_day</h3>

```python
Meteo.next_day(self, duration)
```

Generator to increment DOY and then update the model properties.

This class only allows the day of year (DOY) to move forward a day at a time, where each
time the day moves forward, the model properties are updated.

__Arguments__

- __duration (int)__: number of daily cycles/steps to increment the DOY and model update

__Yields__

`int`: current day run number


<h3 id="meteo.Meteo.doy_has_changed">doy_has_changed</h3>

```python
Meteo.doy_has_changed(self)
```

To be implemented in descendant classes that the DOY has gone forward by a day.

!!! note
    To be implemented by descendant classes on how the model will be updated when
    the DOY has changed.

__Raises__

- `NotImplementedError`: raised if this method is used at this base class level


<h3 id="meteo.Meteo.update">update</h3>

```python
Meteo.update(self, external_info)
```

To be implemented in descendant classes for updating model properties.

!!! warning "Implementation"
    To be implemented by descendant classes on how the model will be updated.

__Arguments__

- __external_info (dict)__: information determined from external sources

__Raises__

- `NotImplementedError`: thrown if this method is used at this base class level


