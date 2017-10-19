<h1 id="energybal">energybal <em>module</em></h1>


Energy balance module.

Model the energy fluxes in the soil-plant-atmosphere system.

__Author - Christopher Teh Boon Sung__

------------------------------------


<h2 id="energybal.LeafDim">LeafDim <em>namedtuple</em></h2>

`LeafDim(length, width)`
namedtuple: Leaflet dimension
<h3 id="energybal.LeafDim.length">length</h3>

float: mean length of a single leaflet
<h3 id="energybal.LeafDim.width">width</h3>

float: mean width of a single leaflet
<h2 id="energybal.StomatalStresses">StomatalStresses <em>namedtuple</em></h2>

`StomatalStresses(water, vpd, par)`
namedtuple: Stresses that would reduce stomatal conductivity
<h3 id="energybal.StomatalStresses.water">water</h3>

float: reduction due to water stress
<h3 id="energybal.StomatalStresses.vpd">vpd</h3>

float: reduction due to vapor pressure deficit
<h3 id="energybal.StomatalStresses.par">par</h3>

float: reduction due to insufficient solar irradiance
<h2 id="energybal.AvailEnergy">AvailEnergy <em>namedtuple</em></h2>

`AvailEnergy(total, crop, soil, net, g)`
namedtuple: Available radiation to the soil-plant-atmosphere system
<h3 id="energybal.AvailEnergy.total">total</h3>

float: radiation available to both crop and soil (total)
<h3 id="energybal.AvailEnergy.crop">crop</h3>

float: radiation available to the crop
<h3 id="energybal.AvailEnergy.soil">soil</h3>

float: radiation available to the soil
<h3 id="energybal.AvailEnergy.net">net</h3>

float: net radiation
<h3 id="energybal.AvailEnergy.g">g</h3>

float: soil heat flux
<h2 id="energybal.Resistances">Resistances <em>namedtuple</em></h2>

`Resistances(rsa, raa, rca, rst, rcs, rss)`
namedtuple: Resistances to heat fluxes
<h3 id="energybal.Resistances.rsa">rsa</h3>

float: aerodynamic resistance between soil and mcf (mean canopy flow)
<h3 id="energybal.Resistances.raa">raa</h3>

float: aerodynamic resistance between mcf and the reference level
<h3 id="energybal.Resistances.rca">rca</h3>

float: boundary layer resistance
<h3 id="energybal.Resistances.rst">rst</h3>

float: leaf stomatal resistance
<h3 id="energybal.Resistances.rcs">rcs</h3>

float: canopy resistance
<h3 id="energybal.Resistances.rss">rss</h3>

float: soil resistance
<h2 id="energybal.HeatFluxes">HeatFluxes <em>namedtuple</em></h2>

`HeatFluxes(total, crop, soil)`
namedtuple: Heat flux components
<h3 id="energybal.HeatFluxes.total">total</h3>

float total heat flux (crop + soil)
<h3 id="energybal.HeatFluxes.crop">crop</h3>

float heat flux from the crop
<h3 id="energybal.HeatFluxes.soil">soil</h3>

float heat flux from the soil
<h2 id="energybal.EnergyBal">EnergyBal <em>class</em></h2>


Energy balance class.

Model the energy fluxes in the soil-plant-atmosphere system, using the electrical network
analogy, where the system is described as a network of resistances where various heat fluxes
must traverse a series of resistances to a reach a given reference height.

This class determines the canopy/foliage temperature which is used by the Photosynthesis model
component to determine the canopy photosynthesis.

__CLASS ATTRIBUTES__

- `psycho (float)`: psychometric constant (0.658 mbar/K)
- `pcp (float)`: vol. heat capacity (1221.09 J/m3/K)
- `soilroughlen (float)`: soil roughness length for flat, tilled land (0.004 m)
- `vonk (float)`: von Karman constant (0.4)

!!! note
    All the above class attributes are supposed to be treated as constants.

__ATTRIBUTES__

- `refhgt (float)`: Reference height (m)
- `d (float)`: Zero plane displacement (m)
- `z0 (float)`: Crop roughness length (m)
- `windext (float)`: Wind extinction coefficient (unitless)
- `eddyext (float)`: Eddy diffusivity extinction coefficient (unitless)
- `leafdim (LeafDim)`: Leaflet dimension (m)
- `stressfn (StomatalStresses)`: Reduction in stomatal conductance due to stresses
- `availegy (AvailEnergy)`: Available energy (W/m2)
- `ustar (float)`: Friction velocity (m/s)
- `ucrophgt (float)`: Wind speed at crop height (m/s)
- `res (Resistances)`: Flux resistances (s/m)
- `et (HeatFluxes)`: Latent heat flux components (W/m2)
- `h (HeatFluxes)`: Sensible heat flux components (W/m2)
- `canopytemp (float)`: Canopy/foliage temperature (deg. C)
- `dayet (HeatFluxes)`: Daily latent heat flux components (mm water/day)
- `dayh (HeatFluxes)`: Daily sensible heat flux components (MJ/m2/day)

__METHODS__

- `windspeed_profile_params`: Windspeed profile paramaters
- `leaf_dimension`: Mean length and width of leaflets (m)
- `stomatal_cond_stresses`: Reduction in stomatal conductance due to
                            various stresses (unitless)
- `available_energy`: Available energy (W/m2) to crop and soil (net radiation partitioning)
- `res_rss`: Soil resistance (s/m)
- `friction_velocity`: Friction velocity (m/s)
- `windspd_at_crophgt`: Wind speed at crop/tree height (m/s)
- `windspd_at_refhgt`: Extrapolated wind speed from weather station
                       height to reference height (m/s)
- `res_rsa`: Aerodynamic resistance between soil and mcf (mean canopy flow) (s/m)
- `res_raa`: Aerodynamic resistance between mcf and reference height (s/m)
- `effective_lai`: Effective LAI (m2 leaf/m2 ground)
- `res_rca`: Boundary layer resistance (s/m)
- `res_rcs_st`: Canopy and stomatal resistance (s/m)
- `resistances`: Flux resistances (s/m)
- `calc_all_fluxes`: Calculate the various latent and sensible heat fluxes (W/m2)
- `canopy_temperature`: Canopy/foliage temperature (deg C)
- `set_heat_fluxes`: Instantaneous heat fluxes (W/m2)
- `set_daily_immutables`: Set constants that do not change within a day
- `daily_heat_balance`: Solve for daily fluxes for latent heat (mm water/day) and
                        sensible heat (MJ/m2/day)
- `update`: Update the energy balance properties
- `next_hour`: Generator to increment the hour and then update the model properties


<h3 id="energybal.EnergyBal.__init__"><em>Constructor</em> __init__</h3>

```python
EnergyBal(self, fname_in)
```

Create and initialize the EnergyBal object.

__Arguments__

- __fname_in (str)__: path and filename of the model initialization file


<h3 id="energybal.EnergyBal.windspeed_profile_params">windspeed_profile_params</h3>

```python
EnergyBal.windspeed_profile_params(self)
```

Windspeed profile paramaters.

Paramaters calculated are as follows
```text
    zero plane displacement, d (m)
    crop roughness length, z0 (m)
    vertical profile extinction coeffiicient (unitless) for:
        wind speed
        eddy diffusivity
```

__Returns__

`tuple`: windspeed profile parameters (float)


<h3 id="energybal.EnergyBal.leaf_dimension">leaf_dimension</h3>


Mean length and width of leaflets (m).

__Returns__

`LeafDim`: `namedtuple` containing the leaf dimensions (`float`)


<h3 id="energybal.EnergyBal.stomatal_cond_stresses">stomatal_cond_stresses</h3>


Reduction in stomatal conductance due to various stresses (unitless).

__Returns__

`StomatalStresses`: `namedtuple` containing the stresses


<h3 id="energybal.EnergyBal.available_energy">available_energy</h3>


Available energy (W/m2) to crop and soil (net radiation partitioning).

__Returns__

`AvailEnergy`: `namedtuple` containing the available energy
                 to the system and its components


<h3 id="energybal.EnergyBal.res_rss">res_rss</h3>

```python
EnergyBal.res_rss(self)
```

Soil resistance (s/m).

__Returns__

`float`: soil resistance


<h3 id="energybal.EnergyBal.friction_velocity">friction_velocity</h3>

```python
EnergyBal.friction_velocity(self)
```

Friction velocity (m/s).

__Returns__

`float`: friction velocity

__Raises__

- `ArithmeticError`: raised when tree is taller than reference height


<h3 id="energybal.EnergyBal.windspd_at_crophgt">windspd_at_crophgt</h3>

```python
EnergyBal.windspd_at_crophgt(self)
```

Wind speed at crop/tree height (m/s).

__Returns__

`float`: wind speed at the tree height


<h3 id="energybal.EnergyBal.windspd_at_refhgt">windspd_at_refhgt</h3>

```python
EnergyBal.windspd_at_refhgt(self)
```

Wind speed (m/s) at reference height.

Wind speed measured at weather station height may not be the same
as the reference height (thus, wind speed will have to be extrapolated to the
reference height).

__Returns__

`float`: wind speed at reference height


<h3 id="energybal.EnergyBal.res_rsa">res_rsa</h3>

```python
EnergyBal.res_rsa(self)
```

Aerodynamic resistance between soil and mcf (mean canopy flow) (s/m).

__Returns__

`float`: aerodynamic resistance between soil and mcf


<h3 id="energybal.EnergyBal.res_raa">res_raa</h3>

```python
EnergyBal.res_raa(self)
```

Aerodynamic resistance between mcf (mean canopy flow) and reference height (s/m).

__Returns__

`float`: aerodynamic resistance between mcf and reference height


<h3 id="energybal.EnergyBal.effective_lai">effective_lai</h3>

```python
EnergyBal.effective_lai(self)
```

Effective LAI (m2 leaf/m2 ground).

__Returns__

`float`: effective LAI


<h3 id="energybal.EnergyBal.res_rca">res_rca</h3>

```python
EnergyBal.res_rca(self)
```

Boundary layer resistance (s/m).

__Returns__

`float`: boundary layer resistance


<h3 id="energybal.EnergyBal.res_rcs_st">res_rcs_st</h3>

```python
EnergyBal.res_rcs_st(self)
```

Canopy and stomatal resistance (s/m).

__Returns__

`float`: Canopy and stomatal resistance


<h3 id="energybal.EnergyBal.resistances">resistances</h3>


Flux resistances (s/m).

__Returns__

`Resistances`: `namedtuple` containing all the resistances (`float`)


<h3 id="energybal.EnergyBal.calc_all_fluxes">calc_all_fluxes</h3>


Calculate the various latent and sensible heat fluxes (W/m2).

__Returns__

`HeatFluxes`: `namedtuple` containing the components of latent and sensible heat fluxes
                 (`float`)


<h3 id="energybal.EnergyBal.canopy_temperature">canopy_temperature</h3>

```python
EnergyBal.canopy_temperature(self)
```

Canopy/foliage temperature (deg. C).

__Returns__

`float`: canopy temperature


<h3 id="energybal.EnergyBal.set_heat_fluxes">set_heat_fluxes</h3>

```python
EnergyBal.set_heat_fluxes(self)
```

Instantaneous heat fluxes (W/m2).

Sets the following attributes
```text
    stressfn - reduction to stomatal conductance
    availegy - available energy to the crop and soil
    ustar - friction velocity
    ucrophgt - wind speed at tree height
    res - all the heat flux resisitances
    et & h - latent and sensible heatfluxes
    canopytemp - foliage temperature
```

__Returns__

`None`:


<h3 id="energybal.EnergyBal.set_daily_immutables">set_daily_immutables</h3>

```python
EnergyBal.set_daily_immutables(self)
```

Set constants that do not change within a day.

Sets parameters that will not change within the same day. This speeds up hourly
calculations carried out for the same day.

__Returns__

`None`:


<h3 id="energybal.EnergyBal.daily_heat_balance">daily_heat_balance</h3>

```python
EnergyBal.daily_heat_balance(self)
```

Solve for daily fluxes for latent (mm water/day) and sensible (MJ/m2/day) heat.

__Returns__

`None`:


<h3 id="energybal.EnergyBal.update">update</h3>

```python
EnergyBal.update(self, external_info)
```

Update the energy balance properties.

__Arguments__

- __external_info (dict)__: will be used to pass information needed by parent classes

__Returns__

`None`:


<h3 id="energybal.EnergyBal.next_hour">next_hour</h3>

```python
EnergyBal.next_hour(self, duration)
```

Generator to increment the hour and then update the model properties.

Hour moves forward an hour day at a time within the same day, where for each hour shift,
the model properties are updated.

__Arguments__

- __duration (int)__: number of cycles/steps to increment the hour and model update

__Yields__

`int`: current hour run


