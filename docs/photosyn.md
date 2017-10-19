<h1 id="photosyn">photosyn <em>module</em></h1>


Photosynthesis module.

Model leaf and canopy photosynthesis by oil palm.

__Author - Christopher Teh Boon Sung__

------------------------------------


<h2 id="photosyn.Reflect">Reflect <em>namedtuple</em></h2>

`Reflect(pdr, pdf)`
namedtuple: Reflection coefficients
<h3 id="photosyn.Reflect.pdr">pdr</h3>

float: reflection coefficient for direct irradiance
<h3 id="photosyn.Reflect.pdf">pdf</h3>

float: reflection coefficient for diffuse irradiance
<h2 id="photosyn.Extinction">Extinction <em>namedtuple</em></h2>

`Extinction(kdr, kdf)`
namedtuple: Canopy extinction coefficients
<h3 id="photosyn.Extinction.kdr">kdr</h3>

float: extinction coefficient for direct irradiance
<h3 id="photosyn.Extinction.kdf">kdf</h3>

float: extinction coefficient for diffuse irradiance
<h2 id="photosyn.PAR">PAR <em>namedtuple</em></h2>

`PAR(outdr, outdf, indrscatter, indr, inscatter, indf, abssunlit, absshaded)`
namedtuple: Photosynthetically-active radiation (PAR) components
<h3 id="photosyn.PAR.outdr">outdr</h3>

float: direct PAR component outside the canopies
<h3 id="photosyn.PAR.outdf">outdf</h3>

float: diffuse PAR component outside the canopies
<h3 id="photosyn.PAR.indrscatter">indrscatter</h3>

float: direct PAR and scatter components within the canopies
<h3 id="photosyn.PAR.indr">indr</h3>

float: direct PAR component within the canopies
<h3 id="photosyn.PAR.inscatter">inscatter</h3>

float: scatter component within the canopies
<h3 id="photosyn.PAR.indf">indf</h3>

float: diffuse PAR component within the canopies
<h3 id="photosyn.PAR.abssunlit">abssunlit</h3>

float: amount of PAR absorbed by the sunlit leaves
<h3 id="photosyn.PAR.absshaded">absshaded</h3>

float: amount of PAR absorbed by the shaded leaves
<h2 id="photosyn.LAI">LAI <em>namedtuple</em></h2>

`LAI(total, sunlit, shaded)`
namedtuple: Leaf area index (LAI) components
<h3 id="photosyn.LAI.total">total</h3>

float: total LAI (sunlit + shaded)
<h3 id="photosyn.LAI.sunlit">sunlit</h3>

float: amount of LAI exposed to direct solar irradiance
<h3 id="photosyn.LAI.shaded">shaded</h3>

float: amount of LAI exposed to diffuse solar irradiance
<h2 id="photosyn.AssimCoef">AssimCoef <em>namedtuple</em></h2>

`AssimCoef(mmco2, mmo2, specificity, vcmax, co2pt)`
namedtuple: Photosynthesis coefficients
<h3 id="photosyn.AssimCoef.mmco2">mmco2</h3>

float: Michaelis-Menten constant for CO2
<h3 id="photosyn.AssimCoef.mmo2">mmo2</h3>

float: Michaelis-Menten constant for O2
<h3 id="photosyn.AssimCoef.specificity">specificity</h3>

float: CO2 / O2 specificity factor
<h3 id="photosyn.AssimCoef.vcmax">vcmax</h3>

float: Rubisco maximum capacity rate
<h3 id="photosyn.AssimCoef.co2pt">co2pt</h3>

float: CO2 compensation point
<h2 id="photosyn.LeafAssim">LeafAssim <em>namedtuple</em></h2>

`LeafAssim(vc, vqsl, vqsh, vs, sunlit, shaded)`
namedtuple: Leaf assimilation components
<h3 id="photosyn.LeafAssim.vc">vc</h3>

float: Rubisco-limited assimilation
<h3 id="photosyn.LeafAssim.vqsl">vqsl</h3>

float: light-limited assimilation by the sunlit leaves
<h3 id="photosyn.LeafAssim.vqsh">vqsh</h3>

float: light-limited assimilation by the shaded leaves
<h3 id="photosyn.LeafAssim.vs">vs</h3>

float: sink-limited assimilation
<h3 id="photosyn.LeafAssim.sunlit">sunlit</h3>

float: total assimilation by the sunlit leaves
<h3 id="photosyn.LeafAssim.shaded">shaded</h3>

float: total assimilation by the shaded leaves
<h2 id="photosyn.Photosyn">Photosyn <em>class</em></h2>


Photosynthesis class.

Model the leaf and canopy photosynthesis (CO2 assimilation) by oil palm.

__EXTERNAL INFORMATION REQUIRED (MUST BE SUPPLIED FROM AN EXTERNAL CLASS)__


```text
    canopytemp (float): Canopy/foliage (deg. C)
```

__ATTRIBUTES__

- `co2ambient (float)`: Ambient CO2 concentration (umol CO2/mol air)
- `co2change (float)`: Annual change in ambient [CO2] (umol CO2/mol air/year)
- `parscatter (float)`: PAR scattering coefficient (unitless)
- `parabsorb (float)`: PAR absorption coefficient (unitless)
- `parsoil (float)`: PAR reflection off soil surface (unitless)
- `quantum_yield (float)`: Quantum efficiency/yield (umol CO2/umol photons)
- `co2internal (float)`: Intercellular CO2 concentration (umol CO2/mol air)
- `o2ambient (float)`: Ambient O2 concentration (umol O2/mol air)
- `gap (float)`: Gap between canopies (unitless)
- `extcoef (Extinction)`: Canopy extinction coefficient (unitless)
- `clump (float)`: Canopy clump factor (unitless)
- `refcoef (Reflect)`: PAR reflection coefficient (unitless)
- `laicomp (LAI)`: Sunlit and shaded LAI components (m2 leaf/m2 ground)
- `par (PAR)`: PAR components (units vary)
- `assimcoef (AssimCoef)`: Assimilation coefficients (units vary)
- `leafassim (LeafAssim)`: CO2 assimilation by leaves (umol CO2/m2 leaf/s)
- `canopyassim (float)`: CO2 assimilation by canopies (umol CO2/m2 leaf/s)
- `dayassim (float)`: Daily CO2 assimilation by canopies (kg CH2O/palm/day)

__METHODS__

- `ambientco2`: Ambient CO2 concentration (umol CO2/mol air) for a given year
- `update_co2ambient`: Update ambient CO2 concentration
- `canopy_extinction`: Canopy extinction coefficients (unitless) for
                        direct and diffuse solar irradiance
- `gap_fraction`: Canopy gap fraction, viewed from zenith
                  (0 = no gap/openings, 1 = full opening)
- `canopy_clump`: Canopy clump (cluster) factor (0-1) (unitless)
- `reflection_coef`: Reflection coefficients (unitless) for direct and diffuse PAR
- `lai_components`: Sunlit and shaded LAI (need to first supply total LAI) (m2 leaf/m2 ground)
- `par_components`: PAR components (umol photons/m2 leaf/s)
- `set_assim_coefs`: Temperature-dependent CO2 assimilation parameters/coefficients.
- `co2_internal`: Internal CO2 concentration (in plant) (umol CO2/mol air)
- `leaf_assimilation`: CO2 assimilation per leaf basis (umol CO2/m2 leaf/s)
- `doy_has_changed`: DOY has changed, so update the atmospheric [CO2]
- `canopy_assimilation`: Instantaneous CO2 assimilation per canopy basis (umol CO2/m2 leaf/s)
- `daily_canopy_assimilation`: Daily CO2 assimilation per canopy per day basis
                               (kg CH2O/palm/day)
- `update`: Update the photosynthesis properties


<h3 id="photosyn.Photosyn.__init__"><em>Constructor</em> __init__</h3>

```python
Photosyn(self, fname_in)
```

Create and initiliaze the Photosyn object.

__Arguments__

- __fname_in (str)__: path and filename of the model initialization file


<h3 id="photosyn.Photosyn.ambientco2">ambientco2</h3>

```python
Photosyn.ambientco2(year)
```

Calculate the mean annual ambient [CO2] (umol CO2/mol air) for a given year.

!!! note
    `ambientco2` is a static method.

__Arguments__

- __year (int)__: year

__Returns__

`float`: ambient CO2 concentration


<h3 id="photosyn.Photosyn.update_co2ambient">update_co2ambient</h3>

```python
Photosyn.update_co2ambient(self)
```

Update ambient CO2 concentration.

__Returns__

`None`:


<h3 id="photosyn.Photosyn.canopy_extinction">canopy_extinction</h3>


Canopy extinction coefficients (unitless) for direct and diffuse solar irradiance.

__Returns__

`Extinction`: `namedtuple` containing direct and diffuse extinction coefficients
                (`float`)


<h3 id="photosyn.Photosyn.gap_fraction">gap_fraction</h3>

```python
Photosyn.gap_fraction(self)
```

Canopy gap fraction, viewed from zenith (0 = no gap/openings, 1 = full opening).

__Returns__

`float`: gap fraction (0-1)


<h3 id="photosyn.Photosyn.canopy_clump">canopy_clump</h3>

```python
Photosyn.canopy_clump(self)
```

Canopy clump (cluster) factor (0-1) (unitless).

__Returns__

`float`: canopy clumpy/cluster coefficient/factor


<h3 id="photosyn.Photosyn.reflection_coef">reflection_coef</h3>


Reflection coefficients (unitless) for direct and diffuse PAR.

__Returns__

`Reflect`: `namedtuple` containing direct and diffuse reflection coefficients (`float`)


<h3 id="photosyn.Photosyn.lai_components">lai_components</h3>


Sunlit and shaded LAI (need to first supply total LAI) (m2 leaf/m2 ground).

__Returns__

`LAI`: `namedtuple` containing total, sunlit, and shaded leaf area index (`float`)


<h3 id="photosyn.Photosyn.par_components">par_components</h3>


PAR components (umol photons/m2 leaf/s).

Outside, within canopies, and that absorbed by canopies.

__Returns__

`PAR`: `namedtuple` containing the PAR components (`float`)


<h3 id="photosyn.Photosyn.set_assim_coefs">set_assim_coefs</h3>


Temperature-dependent CO2 assimilation parameters/coefficients.

Photosynthesis parameters determined in this method are as follows
```text
    Kc (umol/mol) - Michaelis-Menten constant for CO2
    Ko (umol/mol) - Michaelis-Menten constant for O2
    specificity (unitless) - CO2 / O2 specificity factor
    Vcmax (umol CO2/m2 leaf/s) - Rubisco maximum capacity rate, and
    CO2 pt (umol CO2/mol) - CO2 compensation point
```

__Arguments__

- __canopytemp (float)__: foliage temperature (deg. C)

__Returns__

`AssimCoef`: `namedtuple` contining photosynthesis parameters (`float`)


<h3 id="photosyn.Photosyn.co2_internal">co2_internal</h3>

```python
Photosyn.co2_internal(self, canopytemp)
```

Internal CO2 concentration (in plant) (umol CO2/mol air).

__Arguments__

- __canopytemp (float)__: foliage temperature (deg. C)

__Returns__

`float`: intercellular CO2 concentration


<h3 id="photosyn.Photosyn.leaf_assimilation">leaf_assimilation</h3>


CO2 assimilation per leaf basis (umol CO2/m2 leaf/s).

__Returns__

`LeafAssim`: namedtuple containing CO2 assimilation rates (float)


<h3 id="photosyn.Photosyn.canopy_assimilation">canopy_assimilation</h3>

```python
Photosyn.canopy_assimilation(self, canopytemp)
```

Set the instantaneous CO2 assimilation per canopy basis (umol CO2/m2 leaf/s).

__Arguments__

- __canopytemp (float/Float)__: foliage temperature (deg. C)

__Returns__

`None`:


<h3 id="photosyn.Photosyn.daily_canopy_assimilation">daily_canopy_assimilation</h3>

```python
Photosyn.daily_canopy_assimilation(self, canopytemp)
```

Set the daily CO2 assimilation per canopy per day basis (kg CH2O/palm/day).

__Arguments__

- __canopytemp (float/Float)__: foliage temperature (deg. C)

__Returns__

`None`:


<h3 id="photosyn.Photosyn.doy_has_changed">doy_has_changed</h3>

```python
Photosyn.doy_has_changed(self)
```

DOY has changed, so update the atmospheric [CO2].

__Returns__

    None


<h3 id="photosyn.Photosyn.update">update</h3>

```python
Photosyn.update(self, external_info)
```

Update the photosynthesis properties.

__Arguments__

- __external_info (dict)__: requires information on canopy/foliage temperature (deg. C)

__Returns__

`None`:


