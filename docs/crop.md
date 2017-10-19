<h1 id="crop">crop <em>module</em></h1>


Crop growth and yield module.

Model oil palm growth and yield.

__Author - Christopher Teh Boon Sung__

------------------------------------


<h2 id="crop.Contents">Contents <em>namedtuple</em></h2>

`Contents(n, m)`
namedtuple: Nitrogen and minerals contents in a given plant part
<h3 id="crop.Contents.n">n</h3>

float: N content
<h3 id="crop.Contents.m">m</h3>

float: minerals content
<h2 id="crop.Parts">Parts <em>namedtuple</em></h2>

`Parts(pinnae, rachis, trunk, roots, maleflo, femaflo, bunches)`
namedtuple: Plant parts of the oil palm tree
<h3 id="crop.Parts.pinnae">pinnae</h3>

(Part): pinnae part
<h3 id="crop.Parts.rachis">rachis</h3>

(Part): rachis part
<h3 id="crop.Parts.trunk">trunk</h3>

(Part): trunk part
<h3 id="crop.Parts.roots">roots</h3>

(Part): roots parts
<h3 id="crop.Parts.maleflo">maleflo</h3>

(Part): male flowers part
<h3 id="crop.Parts.femaflo">femaflo</h3>

(Part): female flowers parts
<h3 id="crop.Parts.bunches">bunches</h3>

(Part): bunches part
<h2 id="crop.Part">Part <em>class</em></h2>


Class for individual plant parts (e.g., pinnae, rachis, trunk, etc.).

__ATTRIBUTES__

- `content (Contents)`: N and mineral content (each stored as an `AFGen` object)
- `maint (float)`: Assimilates used for maintenance (kg CH2O/palm/day)
- `frac (float)`: DM (dry matter) partitioning (fraction)
- `growth (float)`: Growth rate (kg DM/palm/day)
- `death (float)`: Death rate (kg DM/palm/day)
- `weight (float)`: Weight of the plant part (kg DM/palm)


<h3 id="crop.Part.__init__"><em>Constructor</em> __init__</h3>

```python
Part(self)
```

Create and initialize the Part object.


<h2 id="crop.Crop">Crop <em>class</em></h2>


Crop class (oil palm growth and yield).

__EXTERNAL INFORMATION REQUIRED (MUST BE SUPPLIED FROM AN EXTERNAL CLASS):__

```text
    assimilates (float): Total amount of assimilates from photosynthesis
                         (kg CH2O/palm/day)
    cropstress (float): Plant water stress level
                        (0 = max. stress to 1 = no stress)
```

__ATTRIBUTES__

- `treeage (int)`: Age of the tree (days)
- `plantdens (int)`: Planting density (palms/ha)
- `thinplantdens (int)`: Thinning planting density (palms/ha)
- `thinage (int)`: Thinning tree age (days)
- `femaleprob (float)`: Probability of obtaining female flowers (fraction)
- `parts (Parts)`: `Parts` namedtuple of the various plant parts
- `slatable (AFGen)`: SLA table (age vs SLA)
- `trunkhgt (float)`: Trunk height (m)
- `treehgt  (float)`: Total tree height (m)
- `vdmwgt (float)`: VDM (vegetative dry matter) weight (kg DM/palm)
- `tdmwgt (float)`: Total DM weight (kg DM/palm)
- `vdmmax (float)`: Maximum VDM requirement for the given planting density (kg DM/palm/year)
- `laimax (float)`: Maximum LAI (leaf area index) (m2 leaf/m2 ground)
- `sla (float)`: SLA (specific leaf area) (m2 leaf/kg leaf)
- `lai (float)`: LAI (leaf area index) (m2 leaf/m2 ground)
- `vdmreq (float)`: VDM demand for growth (kg DM/palm/day)
- `assim4maint (float)`: Total maintenance (kg CH2O/palm/day)
- `assim4growth (float)`: Assimilates for vegetative growth (kg CH2O/palm/day)
- `assim4gen (float)`: Assimilates for generative growth (kg CH2O/palm/day)
- `boxmaleflo (list)`: Boxcar for male flowers
- `boxfemaflo (list)`: Boxcar for female flowers (immature bunches)
- `boxbunches (list)`: Boxcar for mature bunches
- `bunchyield (float)`: Yield (kg DM/palm/year)
- `flowersex (int)`: Flower sex at the start of bunch/mature phase (0 = male/abort, 1 = female)
- `newflowersex (int)`: Sex of new flower (0 = male/abort, 1 = female)

__METHODS__

- `tree_height`: Trunk and total tree height (canopy + trunk height) (m)
- `dm_wgts`: Weight of vegetative parts and all parts (kg DM/palm)
- `vdm_maximum`: Maximum VDM requirement for the given planting density (kg DM/palm/year)
- `lai_maximum`: Maximum LAI for the given planting density (m2 leaf/m2 ground)
- `lookup_sla_lai`: SLA-LAI lookup table
- `maintenance_respiration`: Maintenance requirement for every plant part (kg CH2O/palm/day)
- `vdm_requirement`: Calculate the required VDM for growth (kg DM/palm/YEAR)
- `veg_partitioning`: DM partitioning for the various plant parts (fraction)
- `cvf`: Convert weight in glucose, CH2O, to that in dry matter, DM (kg DM/kg CH2O)
- `veg_growth_rates`: Growth rates for the various plant parts (kg DM/palm/day)
- `veg_death_rates`: Death rates for the various plant parts (kg DM/palm/day)
- `update_veg_weights`: Increment the various plant parts (kg DM/palm)
- `new_flower_sex`: Determine the gender of the first (newest) flower in the "boxcar"
- `gen_growth_rates`: Growth rates for generative organs (kg DM/palm/day)
- `update_gen_weights`: Increment the weights for all generative organs (kg DM/palm)
- `daily_growth`: Solve for the crop growth and yield
- `doy_has_changed`: Day of year has changed, so update crop properties
- `update`: Calls the `daily_growth()` method


<h3 id="crop.Crop.__init__"><em>Constructor</em> __init__</h3>

```python
Crop(self, fname_in)
```

Create and initialize the Crop object.

__Arguments__

- __fname_in (str)__: path and filename of the model initialization file


<h3 id="crop.Crop.tree_height">tree_height</h3>

```python
Crop.tree_height(self, cropstress)
```

Trunk and total tree height (canopy + trunk height) (m).

__Arguments__

- __cropstress (float)__: 0-1 plant water stress; 0 = max stress, 1 = no stress

__Returns__

`tuple`: trunk and total tree height (`float`)


<h3 id="crop.Crop.dm_wgts">dm_wgts</h3>

```python
Crop.dm_wgts(self)
```

Weight of vegetative parts and all parts (kg DM/palm).

__Returns__

`tuple`: VDM and TDM (`float`)


<h3 id="crop.Crop.vdm_maximum">vdm_maximum</h3>

```python
Crop.vdm_maximum(self)
```

Maximum VDM requirement for the given planting density (kg DM/palm/year).

__Returns__

`float`: max VDM


<h3 id="crop.Crop.lai_maximum">lai_maximum</h3>

```python
Crop.lai_maximum(self)
```

Maximum LAI for the given planting density (m2 leaf/m2 ground).

__Returns__

`float`: maximum LAI


<h3 id="crop.Crop.lookup_sla_lai">lookup_sla_lai</h3>

```python
Crop.lookup_sla_lai(self)
```

SLA-LAI lookup table.

Lookup from `AFGen` the current SLA (specific leaf area, m2 leaf/kg leaf)
then calculate the LAI (m2 leaf/m2 ground).

__Returns__

`tuple`: SLA and LAI (`float`)


<h3 id="crop.Crop.maintenance_respiration">maintenance_respiration</h3>

```python
Crop.maintenance_respiration(self, assimilates)
```

Maintenance requirement for every plant part (kg CH2O/palm/day).

__Arguments__

- __assimilates (float)__: amount of assimilates from photosynthesis (kg CH2O/palm/day)

__Returns__

`tuple`: maintenance for every plant part (`float`)


<h3 id="crop.Crop.vdm_requirement">vdm_requirement</h3>

```python
Crop.vdm_requirement(self)
```

Calculate the required VDM for growth (kg DM/palm/YEAR).

VDM is per annual basis, so don't forget to divide by 365 to obtain
the required VDM per DAY.

__Returns__

`float`: VDM


<h3 id="crop.Crop.veg_partitioning">veg_partitioning</h3>

```python
Crop.veg_partitioning(self)
```

DM partitioning for the various plant parts (fraction).

__Returns__

`tuple`: DM partitioning between all plant parts(float)


<h3 id="crop.Crop.cvf">cvf</h3>

```python
Crop.cvf(self)
```

Convert weight in glucose, CH2O, to that in dry matter, DM (kg DM/kg CH2O).

__Returns__

`float`: conversion factor


<h3 id="crop.Crop.veg_growth_rates">veg_growth_rates</h3>

```python
Crop.veg_growth_rates(self)
```

Growth rates for the various plant parts (kg DM/palm/day).

__Returns__

`tuple`: growth rates (float)


<h3 id="crop.Crop.veg_death_rates">veg_death_rates</h3>

```python
Crop.veg_death_rates(self)
```

Death rates for the various plant parts (kg DM/palm/day).

__Returns__

`tuple`: death rates (`float`)


<h3 id="crop.Crop.update_veg_weights">update_veg_weights</h3>

```python
Crop.update_veg_weights(self, assimilates)
```

Increment the various plant parts (kg DM/palm).

__Arguments__

- __assimilates (float)__: amount of assimilates from photosynthesis (kg CH2O/palm/day)

__Returns__

`None`:


<h3 id="crop.Crop.new_flower_sex">new_flower_sex</h3>

```python
Crop.new_flower_sex(self)
```

Determine the gender of the first (newest) flower in the "boxcar".

__Returns__

`int`: sex of flower (0 = male/abortl 1 = female)


<h3 id="crop.Crop.gen_growth_rates">gen_growth_rates</h3>

```python
Crop.gen_growth_rates(self)
```

Growth rates for generative organs (kg DM/palm/day).

__Returns__

`tuple`: generative growth rates (`float`)


<h3 id="crop.Crop.update_gen_weights">update_gen_weights</h3>

```python
Crop.update_gen_weights(self, cropstress)
```

Increment the weights for all generative organs (kg DM/palm).

__Arguments__

- __cropstress (float)__: 0-1 plant water stress; 0 = max stress, 1 = no stress

__Returns__

`None`:


<h3 id="crop.Crop.daily_growth">daily_growth</h3>

```python
Crop.daily_growth(self, assimilates, cropstress)
```

Solve for the crop growth and yield.

__Arguments__

- __assimilates (float)__: amount of assimilates from photosynthesis (kg CH2O/palm/day)
- __cropstress (float)__: 0-1 plant water stress; 0 = max stress, 1 = no stress

__Returns__

`None`:


<h3 id="crop.Crop.doy_has_changed">doy_has_changed</h3>

```python
Crop.doy_has_changed(self)
```

DOY has changed, so change the tree age.

__Returns__

`None`:


<h3 id="crop.Crop.update">update</h3>

```python
Crop.update(self, external_info)
```

Update the crop properties by calling the daily_growth method.

__Arguments__

- __external_info (dict)__: requires information on the assimilates and crop stress level

__Returns__

`None`:


