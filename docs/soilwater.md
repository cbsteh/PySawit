<h1 id="soilwater">soilwater <em>module</em></h1>


Soil water movement and content module.

Model one-dimensional soil water movement (fluxes).
Includes groundwater (assumes constant water table depth).

__Author - Christopher Teh Boon Sung__

------------------------------------


<h2 id="soilwater.SWC">SWC <em>namedtuple</em></h2>

`SWC(sat, fc, pwp, psd, porosity, airentry)`
namedtuple: Soil water characteristics
<h3 id="soilwater.SWC.sat">sat</h3>

float: saturation point
<h3 id="soilwater.SWC.fc">fc</h3>

float: field capacity
<h3 id="soilwater.SWC.pwp">pwp</h3>

float: permanent wilting point
<h3 id="soilwater.SWC.psd">psd</h3>

float: pore-size distribution
<h3 id="soilwater.SWC.porosity">porosity</h3>

float: soil porosity
<h3 id="soilwater.SWC.airentry">airentry</h3>

float: air-entry value
<h2 id="soilwater.Texture">Texture <em>namedtuple</em></h2>

`Texture(clay, sand, om)`
namedtuple: Soil texture
<h3 id="soilwater.Texture.clay">clay</h3>

float: percentage of clay
<h3 id="soilwater.Texture.sand">sand</h3>

float: percentage of sand
<h3 id="soilwater.Texture.om">om</h3>

float: percentage of organic matter
<h2 id="soilwater.AET">AET <em>namedtuple</em></h2>

`AET(crop, soil)`
namedtuple: Actual or reduction to evapotranspiration (ET)
<h3 id="soilwater.AET.crop">crop</h3>

float: actual crop transpiration (or reduction of crop potential transpiration)
<h3 id="soilwater.AET.soil">soil</h3>

float: actual soil evaporation (or reduction of soil potential evaporation)
<h2 id="soilwater.RootWater">RootWater <em>class</em></h2>


Soil water characteristics in the rooting zone.

__ATTRIBUTES__

- `wc (float)`: water content (mm)
- `vwc (float)`: water content (m3/m3)
- `critical (float)`: critical water content, below which plant water stress occurs (m3/m3)
- `sat (float)`: saturation point (m3/m3)
- `fc (float)`: field capacity (m3/m3)
- `pwp (float)`: permanent wilting point (m3/m3)


<h3 id="soilwater.RootWater.__init__"><em>Constructor</em> __init__</h3>

```python
RootWater(self)
```

Create and initialize the RootWater object.


<h2 id="soilwater.SoilLayer">SoilLayer <em>class</em></h2>


Soil layer properties class.

The physical properties of a soil layer, dealing with soil water content and fluxes.

__CLASS ATTRIBUTES__

- `flux_fields (list)`: list of flux names (str) to serve as dictionary keys which are
                        `['t', 'e', 'influx', 'outflux', 'netflux']`

__ATTRIBUTES__

- `thick (float)`: Thickness of the soil layer (m)
- `texture`: Sand, clay, and organic matter (%)
- `vwc (float)`: Vol. water content (m3/m3)
- `wc (float)`: Water content (mm)
- `accthick (float)`: Cumulative thickness (m)
- `depth (float)`: Depth of layer from soil surface (m)
- `swc (SWC)`: Soil water characteristics (varying units)
- `ksat (float)`: Saturated hydraulic conductivity (m/day)
- `k (float)`: Hydraulic conductivity (m/day)
- `matric (float)`: Matric head (m)
- `gravity (float)`: Gravity head (m)
- `fluxes (dict)`: Water flux components stored in a dictionary

The keys for the dictionary `fluxes` are as follows

```text
    't': Plant water uptake via transpiration (m/day)
    'e':  Loss of water via evaporation (m/day)
    'influx': Water entry into layer (m/day)
    'outflux': Water exit out of layer (m/day)
    'netflux': Difference between influx and outflux (m/day)
```

__METHODS__

- `initialize_layer`: Initialize all attributes
- `update_heads_k`: Update the matric head, gravity head, and
                    the unsaturated hydraulic conductivity
- `tothead`: Total/sum of matric and gravity head (m) - `getter` method

__Note__

Volumetric water content (vwc) can be given as a negative value. Negative
values are a special code to mean that the water content is a fraction
between SAT and FC or between FC and PWP. The codes are along a scale
from -3 to -1:

```text
    Scale:
              -2.75      -2.25              -1.5
        [-3 ....|..........|....-2 ...........|..........-1]
         PWP                    FC                      SAT
```

so that if the given water content is -1, -2, or -3, it means the
water content should be set to saturation, field capacity, or
permanent wilting point, respectively. A value of -1.5 means the
water content will be set at halfway between SAT and FC. Likewise,
-2.25 and -2.75 mean the water content will be lower than FC, where
the former (-2.25) means the water content will be set nearer to FC,
but the latter (-2.75) closer to PWP.

Any negative values outside the range of -3 to -1 means the water
content wil be set at FC.


<h3 id="soilwater.SoilLayer.__init__"><em>Constructor</em> __init__</h3>

```python
SoilLayer(self)
```

Create and initialize the SoilLayer object.


<h3 id="soilwater.SoilLayer.initialize_layer">initialize_layer</h3>

```python
SoilLayer.initialize_layer(self, prevlayer, nextlayer)
```

Initialize all soil layer attributes.

!!! note
    This function will set the water content to be within the range of
    SAT and FC or between FC and PWP, if the volumetric water content
    is given as negative value. See this class's docstring above.

__Arguments__

- __prevlayer (`SoilLayer`)__: previous soil layer (layer above current layer)
- __nextlayer (`SoilLayer`)__: next soil layer (layer beneath current layer)

__Returns__

`None`:


<h3 id="soilwater.SoilLayer.update_heads_k">update_heads_k</h3>

```python
SoilLayer.update_heads_k(self)
```

Update matric and gravity heads (m), and unsaturated hydraulic conductivity (m/day).

Update is based on current soil water content.

__Returns__

`None`:


<h3 id="soilwater.SoilLayer.tothead">tothead</h3>


Total head (m) - `getter` method.

__Returns__

`float`: total head


<h2 id="soilwater.SoilWater">SoilWater <em>class</em></h2>


Soil water balance class.

Model the soil water flow in one dimension and water balance. Include the effect
of groundwater, if any, but assume constant water table depth.

__EXTERNAL INFORMATION REQUIRED (MUST BE SUPPLIED FROM AN EXTERNAL CLASS)__


```text
    petcrop (float): Potential transpiration (from crop) (mm/day)
    petsoil (float): Potential evaporation (fro soil) (mm/day)
```

__ATTRIBUTES__

- `numintervals (int)`: Number of intervals for integration within a day
- `rootdepth (float)`: Rooting depth (m)
- `has_watertable (bool)`: True if water table / groundwater is present, else False
- `numlayers (int)`: Number of soil layers
- `layers (list)`: List of SoilLayer objects (their numbers must match numlayers)
- `rootwater (RootWater)`: Soil water characteristics in the root zone
- `cf (list)`: List of dictionary of cumulative fluxes for every soil layer
- `waterstresses (AET)`: Reduction to evaporation and transpiration due to water stress
- `netrain (float)`: Net rainfall (mm/day)
- `aet (AET)`: Actual water loss by evaporation and transpiration (mm/day)

__METHODS__

- `net_rainfall`: Net rainfall (mm/day)
- `rooting_depth`: Increase in rooting depth (m)
- `update_rootwater`: Update the water content and water characteristics in the rooting zone
- `reduce_et`: Reduction in evaporation and transpiration (0-1, 1=no stress, 0=max. stress)
- `actual_et`: Actual evaporation and transpiration (mm/day)
- `influx_from_watertable`: Influx of water from the water table (m/day).
- `calc_water_fluxes`: Calculate the various water fluxes (m/day) for all soil layers
- `daily_water_balance`: Solve for the water content in each soil layer
- `update`: Update the soil water properties by solving the water fluxes


<h3 id="soilwater.SoilWater.__init__"><em>Constructor</em> __init__</h3>

```python
SoilWater(self, fname_in)
```

Create and initialize the SoilWater object.

__Arguments__

- __fname_in (str)__: path and filename of the model initialization file


<h3 id="soilwater.SoilWater.net_rainfall">net_rainfall</h3>

```python
SoilWater.net_rainfall(self)
```

Net rainfall (mm/day).

__Returns__

`float`: net rainfall


<h3 id="soilwater.SoilWater.rooting_depth">rooting_depth</h3>

```python
SoilWater.rooting_depth(self)
```

Increase in rooting depth (m).

__Returns__

`float`: rooting depth


<h3 id="soilwater.SoilWater.update_rootwater">update_rootwater</h3>

```python
SoilWater.update_rootwater(self)
```

Update the water content and water characteristics in the rooting zone.

The `RootZone` object will be set here.

!!! note
    Critical soil water content for plant water stress taken as 0.6 or 60%
    of the difference between soil saturation and permanent wilting point.

__Returns__

`None`:


<h3 id="soilwater.SoilWater.reduce_et">reduce_et</h3>


Reduction in evaporation and transpiration (0-1, 1=no stress, 0=max. stress).

__Returns__

`AET`: `namedtuple` containing reduction in E and T (`float`)


<h3 id="soilwater.SoilWater.actual_et">actual_et</h3>


Actual evaporation and transpiration (mm/day).

__Arguments__

- __petcrop (float)__: potential water loss from the crop (mm/day)
- __petsoil (float)__: potential water loss from the soil (mm/day)

__Returns__

`AET`: `namedtuple` containing actual water loss from soil and crop (`float`)


<h3 id="soilwater.SoilWater.influx_from_watertable">influx_from_watertable</h3>

```python
SoilWater.influx_from_watertable(self)
```

Influx of water from the water table (m/day).

__Returns__

`float`: groundwater influx


<h3 id="soilwater.SoilWater.calc_water_fluxes">calc_water_fluxes</h3>

```python
SoilWater.calc_water_fluxes(self, petcrop, petsoil, firstrun)
```

Calculate the various water fluxes (m/day) for all soil layers.

Flux can either have a positive or negative sign

```text
    +ve flux - means downward flow
    -ve flux - means upward flow (against gravity)
```

__Arguments__

- __petcrop (float)__: potential water loss from the crop (mm/day)
- __petsoil (float)__: potential water loss from the soil (mm/day)
- __firstrun (bool)__: set to `True` for first run, else `False`.
                     `True` means the cumulative fluxes will be initialize with the first
                     set of flux values. `False` will accumulate the flux values.

__Returns__

`None`:


<h3 id="soilwater.SoilWater.daily_water_balance">daily_water_balance</h3>

```python
SoilWater.daily_water_balance(self, petcrop, petsoil)
```

Solve for the water content in each soil layer.

__Arguments__

- __petcrop (float)__: potential water loss from the crop (mm/day)
- __petsoil (float)__: potential water loss from the soil (mm/day)

__Returns__

`None`:


<h3 id="soilwater.SoilWater.update">update</h3>

```python
SoilWater.update(self, external_info)
```

Update the soil water properties by solving the water fluxes.

__Arguments__

- __external_info (dict)__: requires information on potential transpiration and evaporation

__Returns__

`None`:


