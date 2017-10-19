"""
Crop growth and yield module.

Model oil palm growth and yield.

# Author - Christopher Teh Boon Sung
------------------------------------

"""

import math
from collections import namedtuple

from meteo import Meteo
from utils import AFGen


Contents = namedtuple('Contents', ['n', 'm'])
Contents.__doc__ = '`' + Contents.__doc__
Contents.__doc__ += '`\r\nnamedtuple: Nitrogen and minerals contents in a given plant part'
Contents.n.__doc__ = 'float: N content'
Contents.m.__doc__ = 'float: minerals content'

Parts = namedtuple('Parts', ['pinnae', 'rachis', 'trunk', 'roots', 'maleflo', 'femaflo', 'bunches'])
Parts.__doc__ = '`' + Parts.__doc__
Parts.__doc__ += '`\r\nnamedtuple: Plant parts of the oil palm tree'
Parts.pinnae.__doc__ = '(Part): pinnae part'
Parts.rachis.__doc__ = '(Part): rachis part'
Parts.trunk.__doc__ = '(Part): trunk part'
Parts.roots.__doc__ = '(Part): roots parts'
Parts.maleflo.__doc__ = '(Part): male flowers part'
Parts.femaflo.__doc__ = '(Part): female flowers parts'
Parts.bunches.__doc__ = '(Part): bunches part'


class Part(object):
    """
    Class for individual plant parts (e.g., pinnae, rachis, trunk, etc.).

    # ATTRIBUTES
        content (Contents): N and mineral content (each stored as an `AFGen` object)
        maint (float): Assimilates used for maintenance (kg CH2O/palm/day)
        frac (float): DM (dry matter) partitioning (fraction)
        growth (float): Growth rate (kg DM/palm/day)
        death (float): Death rate (kg DM/palm/day)
        weight (float): Weight of the plant part (kg DM/palm)

    """

    def __init__(self):
        """
        Create and initialize the Part object.

        """
        self.content = None
        self.maint = 0.0
        self.frac = 0.0
        self.growth = 0.0
        self.death = 0.0
        self.weight = 0.0


class Crop(Meteo):
    """
    Crop class (oil palm growth and yield).

    # EXTERNAL INFORMATION REQUIRED (MUST BE SUPPLIED FROM AN EXTERNAL CLASS):
    ```text
        assimilates (float): Total amount of assimilates from photosynthesis
                             (kg CH2O/palm/day)
        cropstress (float): Plant water stress level
                            (0 = max. stress to 1 = no stress)
    ```

    # ATTRIBUTES
        treeage (int): Age of the tree (days)
        plantdens (int): Planting density (palms/ha)
        thinplantdens (int): Thinning planting density (palms/ha)
        thinage (int): Thinning tree age (days)
        femaleprob (float): Probability of obtaining female flowers (fraction)
        parts (Parts): `Parts` namedtuple of the various plant parts
        slatable (AFGen): SLA table (age vs SLA)
        trunkhgt (float): Trunk height (m)
        treehgt  (float): Total tree height (m)
        vdmwgt (float): VDM (vegetative dry matter) weight (kg DM/palm)
        tdmwgt (float): Total DM weight (kg DM/palm)
        vdmmax (float): Maximum VDM requirement for the given planting density (kg DM/palm/year)
        laimax (float): Maximum LAI (leaf area index) (m2 leaf/m2 ground)
        sla (float): SLA (specific leaf area) (m2 leaf/kg leaf)
        lai (float): LAI (leaf area index) (m2 leaf/m2 ground)
        vdmreq (float): VDM demand for growth (kg DM/palm/day)
        assim4maint (float): Total maintenance (kg CH2O/palm/day)
        assim4growth (float): Assimilates for vegetative growth (kg CH2O/palm/day)
        assim4gen (float): Assimilates for generative growth (kg CH2O/palm/day)
        boxmaleflo (list): Boxcar for male flowers
        boxfemaflo (list): Boxcar for female flowers (immature bunches)
        boxbunches (list): Boxcar for mature bunches
        bunchyield (float): Yield (kg DM/palm/year)
        flowersex (int): Flower sex at the start of bunch/mature phase (0 = male/abort, 1 = female)
        newflowersex (int): Sex of new flower (0 = male/abort, 1 = female)

    # METHODS
        tree_height: Trunk and total tree height (canopy + trunk height) (m)
        dm_wgts: Weight of vegetative parts and all parts (kg DM/palm)
        vdm_maximum: Maximum VDM requirement for the given planting density (kg DM/palm/year)
        lai_maximum: Maximum LAI for the given planting density (m2 leaf/m2 ground)
        lookup_sla_lai: SLA-LAI lookup table
        maintenance_respiration: Maintenance requirement for every plant part (kg CH2O/palm/day)
        vdm_requirement: Calculate the required VDM for growth (kg DM/palm/YEAR)
        veg_partitioning: DM partitioning for the various plant parts (fraction)
        cvf: Convert weight in glucose, CH2O, to that in dry matter, DM (kg DM/kg CH2O)
        veg_growth_rates: Growth rates for the various plant parts (kg DM/palm/day)
        veg_death_rates: Death rates for the various plant parts (kg DM/palm/day)
        update_veg_weights: Increment the various plant parts (kg DM/palm)
        new_flower_sex: Determine the gender of the first (newest) flower in the "boxcar"
        gen_growth_rates: Growth rates for generative organs (kg DM/palm/day)
        update_gen_weights: Increment the weights for all generative organs (kg DM/palm)
        daily_growth: Solve for the crop growth and yield
        doy_has_changed: Day of year has changed, so update crop properties
        update: Calls the `daily_growth()` method

    """

    __a = 0.935    # internal use: constant to calculate max. VDM and LAI, and VDM requirement

    def __init__(self, fname_in):
        """
        Create and initialize the Crop object.

        # Arguments
            fname_in (str): path and filename of the model initialization file

        """
        Meteo.__init__(self, fname_in)   # initialize the parent class first

        dinit = self.ini
        self.treeage = dinit['treeage']  # tree age (days)
        self.plantdens = dinit['plantdens']  # planting density (palms/ha)
        self.thinplantdens = dinit['thinplantdens']  # thinning planting density (palms/ha)
        self.thinage = dinit['thinage']  # thinning tree age (days)
        self.femaleprob = dinit['femaleprob']  # probability of getting female flowers
        nparts = len(Parts._fields)
        self.parts = Parts(*list(Part() for _ in range(nparts)))
        # load in the N and mineral tables, and for SLA:
        dsla = {float(k): v for k, v in dinit['sla'].items()}
        self.slatable = AFGen(dsla)
        for i in range(nparts):
            fieldname = Parts._fields[i]
            self.parts[i].weight = dinit[fieldname + '_wgt']
            if i < 4:
                d1 = dinit[fieldname + '_n']
                nd1 = {float(k): v for k, v in d1.items()}
                d2 = dinit[fieldname + '_m']
                nd2 = {float(k): v for k, v in d2.items()}
                self.parts[i].content = Contents(AFGen(nd1), AFGen(nd2))

        self.trunkhgt = -1.0  # -1.0 is a code: the initial trunk height will be calculated
        self.trunkhgt, self.treehgt = self.tree_height(1.0)  # trunk and full tree height (m)
        self.vdmwgt, self.tdmwgt = self.dm_wgts()  # VDM and total VDM weights (kg DM/palm)
        parts = self.parts
        # constant partitioning for generative organs (fractions):
        parts.maleflo.frac, parts.femaflo.frac, parts.bunches.frac = [0.159, 0.159, 0.682]
        self.vdmmax = self.vdm_maximum()  # maximum VDM (kg DM/palm)
        self.laimax = self.lai_maximum()  # maximum LAI (m2 leaf/m2 ground)
        # LAI (m2 leaf/m2 ground) and SLA (m2 leaf/kg DM)
        self.sla, self.lai = self.lookup_sla_lai()
        self.vdmreq = 0.0  # VDM requirement (kg DM/palm/day)
        self.assim4maint = 0.0  # assimilates for maintenance (kg CH2O/palm/day)
        self.assim4growth = 0.0  # assimilates for growth (kg CH2O/palm/day
        self.assim4gen = 0.0  # assimilates for generative growth (kg CH2O/palm/day)
        # "boxcar train" for the weights (kg DM/palm)of generative organs:
        self.boxmaleflo = list(0.0 for _ in range(210))  # for male flowers
        self.boxfemaflo = list(0.0 for _ in range(210))  # for female flowers (immature bunches)
        self.boxbunches = list(0.0 for _ in range(150))  # for mature bunches
        self.bunchyield = 0.0  # yield (kg DM/palm/year)
        # flower sex at the start of bunch/mature phase (0 = male/abort, 1 = female)
        self.flowersex = 0
        # sex of first flower
        self.newflowersex = 0

    def tree_height(self, cropstress):
        """
        Trunk and total tree height (canopy + trunk height) (m).

        # Arguments
            cropstress (float): 0-1 plant water stress; 0 = max stress, 1 = no stress

        # Returns
            tuple: trunk and total tree height (`float`)

        """
        a, b, c = 2.845586, -1980.88805, -5166.36569
        hgt0 = math.exp(a + b / self.plantdens ** 2 + c / self.treeage)
        if self.trunkhgt > 0:
            rate = -c / (0.7 * self.treeage ** 2) * hgt0 * (0.21 * cropstress + 0.553)
            trunk = self.trunkhgt + rate
        else:
            trunk = hgt0  # initial height (no crop stress assumed for the initial height)
        canopyhgt = (0.1382 * self.treeage + 150.91) / 100    # canopy height (m)
        return trunk, trunk + canopyhgt

    def dm_wgts(self):
        """
        Weight of vegetative parts and all parts (kg DM/palm).

        # Returns
            tuple: VDM and TDM (`float`)

        """
        vegwgt = totalwgt = 0.0
        for i in range(len(Parts._fields)):
            wgt = self.parts[i].weight
            totalwgt += wgt
            if i < 4:
                vegwgt += wgt  # first four are vegetative parts: pinnae, rachis, trunk, and roots
        return vegwgt, totalwgt

    def vdm_maximum(self):
        """
        Maximum VDM requirement for the given planting density (kg DM/palm/year).

        # Returns
            float: max VDM

        """
        return 231 * self.plantdens ** (Crop.__a - 1 / Crop.__a)

    def lai_maximum(self):
        """
        Maximum LAI for the given planting density (m2 leaf/m2 ground).

        # Returns
            float: maximum LAI

        """
        return 0.0274 * self.plantdens ** (1 / Crop.__a)

    def lookup_sla_lai(self):
        """
        SLA-LAI lookup table.

        Lookup from `AFGen` the current SLA (specific leaf area, m2 leaf/kg leaf)
        then calculate the LAI (m2 leaf/m2 ground).

        # Returns
            tuple: SLA and LAI (`float`)

        """
        sla = self.slatable.val(self.treeage)
        lai = self.parts.pinnae.weight * sla * self.plantdens / 10000
        return sla, lai

    def maintenance_respiration(self, assimilates):
        """
        Maintenance requirement for every plant part (kg CH2O/palm/day).

        # Arguments
            assimilates (float): amount of assimilates from photosynthesis (kg CH2O/palm/day)

        # Returns
            tuple: maintenance for every plant part (`float`)

        """
        tmean = self.daytmean  # mean daily air temperature
        q10 = 2.0  # Q10 value for temperature correction at mean daily air temperature

        def _temp_corr(val25):
            """Temperature correction."""
            return val25 * q10 ** ((tmean - 25) / 25)

        def _maintcoef_fn(p):
            """Calculate a given plant part's maintenance coefficient (kg CH2O/kg DM)."""
            val25 = p.n.val(self.treeage) * 0.036 * 6.25 + p.m.val(self.treeage) * 0.072 * 2
            return _temp_corr(val25)

        # pinnae:
        part = self.parts.pinnae
        partcont = part.content
        mc_pinnae = _maintcoef_fn(partcont)
        m_pinnae = part.weight * mc_pinnae * (24 - self.daylen) / 24
        # rachis:
        part = self.parts.rachis
        partcont = part.content
        mc_rachis = _maintcoef_fn(partcont)
        m_rachis = part.weight * mc_rachis
        # trunk:
        part = self.parts.trunk
        partcont = part.content
        mc_trunk = _maintcoef_fn(partcont)
        toptrunk_wgt = min(45, part.weight)
        bottomtrunk_wgt = part.weight - toptrunk_wgt
        m_trunk = toptrunk_wgt * mc_trunk + bottomtrunk_wgt * mc_trunk * 0.06
        # roots:
        part = self.parts.roots
        partcont = part.content
        mc_roots = _maintcoef_fn(partcont)
        m_roots = part.weight * mc_roots
        # male flowers:
        part = self.parts.maleflo
        m_maleflo = part.weight * mc_rachis
        # female flowers (immature bunches):
        part = self.parts.femaflo
        m_femaflo = part.weight * mc_rachis
        # mature bunches:
        part = self.parts.bunches
        m_bunches = part.weight * _temp_corr(0.0027)
        # total maintenance:
        if 15 < tmean < 45:  # between 15 and 45 deg. C
            m_metabolic = _temp_corr(0.16 * assimilates / self.tdmwgt)
            m_total = m_pinnae + m_rachis + m_trunk + m_roots
            m_total += m_maleflo + m_femaflo + m_bunches + m_metabolic
        else:
            # all assimilates diverted for maintenance due to unfavorable temperatures
            m_total = assimilates
        return m_pinnae, m_rachis, m_trunk, m_roots, m_maleflo, m_femaflo, m_bunches, m_total

    def vdm_requirement(self):
        """
        Calculate the required VDM for growth (kg DM/palm/YEAR).

        VDM is per annual basis, so don't forget to divide by 365 to obtain
        the required VDM per DAY.

        # Returns
            float: VDM

        """
        idelta = 1 / Crop.__a
        a = Crop.__a / self.vdmmax
        b = 0.1 * (idelta - 1) * (self.plantdens / 100) ** idelta
        vdm = max(20.0, 1 / (a + b / self.lai ** 1.5))
        return vdm / 365

    # noinspection PyMethodMayBeStatic
    def veg_partitioning(self):
        """
        DM partitioning for the various plant parts (fraction).

        # Returns
            tuple: DM partitioning between all plant parts(float)

        """
        dm_pinnae = 0.24
        dm_rachis = 0.46
        dm_trunk = 0.14
        dm_roots = 1 - dm_pinnae - dm_rachis - dm_trunk
        return dm_pinnae, dm_rachis, dm_trunk, dm_roots

    def cvf(self):
        """
        Convert weight in glucose, CH2O, to that in dry matter, DM (kg DM/kg CH2O).

        # Returns
            float: conversion factor

        """
        parts = self.parts
        leaves = parts.pinnae.frac + parts.rachis.frac
        return 0.7 * leaves + 0.66 * parts.trunk.frac + 0.65 * parts.roots.frac

    def veg_growth_rates(self):
        """
        Growth rates for the various plant parts (kg DM/palm/day).

        # Returns
            tuple: growth rates (float)

        """
        availvdm = self.assim4growth * self.cvf()  # convert weight from per CH2O to DM basis
        return tuple(self.parts[i].frac * availvdm for i in range(4))

    def veg_death_rates(self):
        """
        Death rates for the various plant parts (kg DM/palm/day).

        # Returns
            tuple: death rates (`float`)

        """
        age = self.treeage
        # leaves (pinnae and rachis) death:
        maxdeath = 0.0016
        lower_age, upper_age = 600, 2500
        if age <= lower_age:
            dleaves = 0.0
        elif lower_age < age <= upper_age:
            dleaves = maxdeath * (age - lower_age) / (upper_age - lower_age)
        else:
            dleaves = maxdeath
        dpinnae = dleaves * self.parts.pinnae.weight
        drachis = dleaves * self.parts.rachis.weight
        # roots death:
        lower_age, upper_age = 1200, 3285
        if age <= lower_age:
            droots = 0.0
        elif lower_age < age <= upper_age:
            droots = (9.592 * 10 ** (-5) * age - 0.11510791) / 365
        else:
            droots = 0.2 / 365
        droots *= self.parts.roots.weight
        return dpinnae, drachis, 0.0, droots  # no death for trunk

    def update_veg_weights(self, assimilates):
        """
        Increment the various plant parts (kg DM/palm).

        # Arguments
            assimilates (float): amount of assimilates from photosynthesis (kg CH2O/palm/day)

        # Returns
            None:

        """
        for i, p in enumerate(self.veg_partitioning()):
            self.parts[i].frac = p  # update DM partitioning between plant parts
        cvf = self.cvf()
        # 1. maintenance respiration (kg CH2O/palm/day):
        m = self.maintenance_respiration(assimilates)
        for i in range(len(m) - 1):
            self.parts[i].maint = m[i] * cvf  # store each part's maintenance as kg DM/palm/day
        # total maintenance (note: in kg CH2O/palm/day)
        self.assim4maint = min(assimilates, float(m[-1]))
        # 2. growth respiration (kg CH2O/palm/day):
        # max. avail. assimilates for growth (kg CH2O/palm/day)
        maxassim = assimilates - self.assim4maint
        self.vdmreq = self.vdm_requirement()  # VDM demand for growth (kg DM/palm/day)
        # assimilates for vegetative growth (kg CH2O/palm/day)
        self.assim4growth = min(self.vdmreq / cvf, maxassim)
        for i, g in enumerate(self.veg_growth_rates()):
            # growth rates for the individual plant parts (kg DM/palm/day)
            self.parts[i].growth = g
        for i, d in enumerate(self.veg_death_rates()):
            # death rates for the individual plant parts (kg DM/palm/day)
            self.parts[i].death = d
        # assimilates for generative growth (kg CH2O/palm/day)
        self.assim4gen = maxassim - self.assim4growth
        # update weights (kg DM/palm):
        self.vdmwgt = 0.0
        for i in range(4):
            part = self.parts[i]
            part.weight += part.growth - part.death
            self.vdmwgt += part.weight
        # pinnae weight has changed, so LAI changes too
        self.sla, self.lai = self.lookup_sla_lai()

    def new_flower_sex(self):
        """
        Determine the gender of the first (newest) flower in the "boxcar".

        # Returns
            int: sex of flower (0 = male/abortl 1 = female)

        """
        return 1 if self.rnd() <= self.femaleprob else 0  # 0 = male/abort, 1 = female

    def gen_growth_rates(self):
        """
        Growth rates for generative organs (kg DM/palm/day).

        # Returns
            tuple: generative growth rates (`float`)

        """
        self.newflowersex = self.new_flower_sex()
        # count non-zero weights in boxcar trains:
        # +1 if first gender is male
        n1 = sum(1 for x in self.boxmaleflo[1:] if x > 0.0) + (1 - self.newflowersex)
        f1 = self.parts.maleflo.frac * n1 / len(self.boxmaleflo)
        # +1 if first gender is female
        n2 = sum(1 for x in self.boxfemaflo[1:] if x > 0.0) + self.newflowersex
        f2 = self.parts.femaflo.frac * n2 / len(self.boxfemaflo)
        n3 = sum(1 for x in self.boxbunches if x > 0.0)  # can have 0 bunches
        f3 = self.parts.bunches.frac * n3 / len(self.boxbunches)
        ftotal = f1 + f2 + f3  # won't be zero because there's at least one female or male flower
        f1 /= ftotal
        f2 /= ftotal
        f3 /= ftotal
        cvf2 = 0.7 * f1 + 0.7 * f2 + 0.44 * f3
        g1 = f1 * cvf2 * self.assim4gen / n1 if n1 > 0 else 0.0
        g2 = f2 * cvf2 * self.assim4gen / n2 if n2 > 0 else 0.0
        g3 = f3 * cvf2 * self.assim4gen / n3 if n3 > 0 else 0.0
        return g1, g2, g3  # male flowers, female flowers, bunches

    def update_gen_weights(self, cropstress):
        """
        Increment the weights for all generative organs (kg DM/palm).

        # Arguments
            cropstress (float): 0-1 plant water stress; 0 = max stress, 1 = no stress

        # Returns
            None:

        """
        def _shift(boxes):
            """In-place shift to the right for weights in the "boxcar train"."""
            tail = boxes[-1]
            del boxes[-1]
            boxes.insert(0, tail)

        def _increment_box_wgts(boxes, wgt):
            """Increment weights in the individual boxcars."""
            if wgt > 0:
                for i, x in enumerate(boxes):
                    if x > 0:
                        boxes[i] += wgt  # weight gain only if existing weight is not 0

        # determine if water stress will abort flower (male and female):
        if self.rnd() > cropstress:
            self.boxmaleflo[90] = 0.0  # male and female flowers aborted at node 90
            self.boxfemaflo[90] = 0.0
        parts = self.parts
        # growth rates (kg DM/palm/day):
        parts.maleflo.growth, parts.femaflo.growth, parts.bunches.growth = self.gen_growth_rates()
        # increment the weights (kg DM/palm) in the generative organ boxcars:
        _increment_box_wgts(self.boxmaleflo, parts.maleflo.growth)
        _increment_box_wgts(self.boxfemaflo, parts.femaflo.growth)
        _increment_box_wgts(self.boxbunches, parts.bunches.growth)
        # get yield (kg DM/palm/day) which is the last value in the bunches boxcar train:
        self.bunchyield = self.boxbunches[-1]
        # shift one step to the right for each boxcar train:
        _shift(self.boxmaleflo)
        _shift(self.boxfemaflo)
        _shift(self.boxbunches)
        # update the endpoints (latest flower can be either male or female):
        self.boxmaleflo[0] = parts.maleflo.growth * (1 - self.newflowersex)
        self.boxbunches[0] = self.boxfemaflo[0]
        self.boxfemaflo[0] = parts.femaflo.growth * self.newflowersex
        # flower gender at start of bunch phase:
        self.flowersex = 1 if self.boxbunches[0] > 0.0 else 0
        # update the total weights (kg DM/palm):
        parts.maleflo.weight = sum(self.boxmaleflo)
        parts.femaflo.weight = sum(self.boxfemaflo)
        parts.bunches.weight = sum(self.boxbunches)
        # total DM weight is the weight of all plant parts
        flowgt = parts.maleflo.weight + parts.femaflo.weight
        self.tdmwgt = self.vdmwgt + flowgt + parts.bunches.weight

    def daily_growth(self, assimilates, cropstress):
        """
        Solve for the crop growth and yield.

        # Arguments
            assimilates (float): amount of assimilates from photosynthesis (kg CH2O/palm/day)
            cropstress (float): 0-1 plant water stress; 0 = max stress, 1 = no stress

        # Returns
            None:

        """
        self.trunkhgt, self.treehgt = self.tree_height(cropstress)
        self.update_veg_weights(assimilates)
        self.update_gen_weights(cropstress)

    def doy_has_changed(self):
        """
        DOY has changed, so change the tree age.

        # Returns
            None:

        """
        self.treeage += 1     # a day older
        # check if planting density should now be changed due to thinning, if any:
        if 0 < self.thinplantdens != self.plantdens and self.treeage >= self.thinage:
            self.plantdens = self.thinplantdens
            # since planting density has changed, update the constants, VDM and
            #    LAI maximum, as both require information about planting density
            self.vdmmax = self.vdm_maximum()  # maximum VDM (kg DM/palm)
            self.laimax = self.lai_maximum()  # maximum LAI (m2 leaf/m2 ground)

    def update(self, external_info):
        """
        Update the crop properties by calling the daily_growth method.

        # Arguments
            external_info (dict): requires information on the assimilates and crop stress level

        # Returns
            None:

        """
        self.daily_growth(external_info['assimilates'], external_info['cropstress'])
