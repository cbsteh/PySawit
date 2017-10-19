"""
Photosynthesis module.

Model leaf and canopy photosynthesis by oil palm.

# Author - Christopher Teh Boon Sung
------------------------------------

"""

import math
from collections import namedtuple

from soilwater import SoilWater

Reflect = namedtuple('Reflect', ['pdr', 'pdf'])
Reflect.__doc__ = '`' + Reflect.__doc__
Reflect.__doc__ += '`\r\nnamedtuple: Reflection coefficients'
Reflect.pdr.__doc__ = 'float: reflection coefficient for direct irradiance'
Reflect.pdf.__doc__ = 'float: reflection coefficient for diffuse irradiance'

Extinction = namedtuple('Extinction', ['kdr', 'kdf'])
Extinction.__doc__ = '`' + Extinction.__doc__
Extinction.__doc__ += '`\r\nnamedtuple: Canopy extinction coefficients'
Extinction.kdr.__doc__ = 'float: extinction coefficient for direct irradiance'
Extinction.kdf.__doc__ = 'float: extinction coefficient for diffuse irradiance'

PAR = namedtuple('PAR', ['outdr', 'outdf',
                         'indrscatter', 'indr', 'inscatter', 'indf',
                         'abssunlit', 'absshaded'])
PAR.__doc__ = '`' + PAR.__doc__
PAR.__doc__ += '`\r\nnamedtuple: Photosynthetically-active radiation (PAR) components'
PAR.outdr.__doc__ = 'float: direct PAR component outside the canopies'
PAR.outdf.__doc__ = 'float: diffuse PAR component outside the canopies'
PAR.indrscatter.__doc__ = 'float: direct PAR and scatter components within the canopies'
PAR.indr.__doc__ = 'float: direct PAR component within the canopies'
PAR.inscatter.__doc__ = 'float: scatter component within the canopies'
PAR.indf.__doc__ = 'float: diffuse PAR component within the canopies'
PAR.abssunlit.__doc__ = 'float: amount of PAR absorbed by the sunlit leaves'
PAR.absshaded.__doc__ = 'float: amount of PAR absorbed by the shaded leaves'

LAI = namedtuple('LAI', ['total', 'sunlit', 'shaded'])
LAI.__doc__ = '`' + LAI.__doc__
LAI.__doc__ += '`\r\nnamedtuple: Leaf area index (LAI) components'
LAI.total.__doc__ = 'float: total LAI (sunlit + shaded)'
LAI.sunlit.__doc__ = 'float: amount of LAI exposed to direct solar irradiance'
LAI.shaded.__doc__ = 'float: amount of LAI exposed to diffuse solar irradiance'

AssimCoef = namedtuple('AssimCoef', ['mmco2', 'mmo2', 'specificity', 'vcmax', 'co2pt'])
AssimCoef.__doc__ = '`' + AssimCoef.__doc__
AssimCoef.__doc__ += '`\r\nnamedtuple: Photosynthesis coefficients'
AssimCoef.mmco2.__doc__ = 'float: Michaelis-Menten constant for CO2'
AssimCoef.mmo2.__doc__ = 'float: Michaelis-Menten constant for O2'
AssimCoef.specificity.__doc__ = 'float: CO2 / O2 specificity factor'
AssimCoef.vcmax.__doc__ = 'float: Rubisco maximum capacity rate'
AssimCoef.co2pt.__doc__ = 'float: CO2 compensation point'

LeafAssim = namedtuple('LeafAssim', ['vc', 'vqsl', 'vqsh', 'vs', 'sunlit', 'shaded'])
LeafAssim.__doc__ = '`' + LeafAssim.__doc__
LeafAssim.__doc__ += '`\r\nnamedtuple: Leaf assimilation components'
LeafAssim.vc.__doc__ = 'float: Rubisco-limited assimilation'
LeafAssim.vqsl.__doc__ = 'float: light-limited assimilation by the sunlit leaves'
LeafAssim.vqsh.__doc__ = 'float: light-limited assimilation by the shaded leaves'
LeafAssim.vs.__doc__ = 'float: sink-limited assimilation'
LeafAssim.sunlit.__doc__ = 'float: total assimilation by the sunlit leaves'
LeafAssim.shaded.__doc__ = 'float: total assimilation by the shaded leaves'


class Photosyn(SoilWater):
    """
    Photosynthesis class.

    Model the leaf and canopy photosynthesis (CO2 assimilation) by oil palm.

    # EXTERNAL INFORMATION REQUIRED (MUST BE SUPPLIED FROM AN EXTERNAL CLASS)

    ```text
        canopytemp (float): Canopy/foliage (deg. C)
    ```

    # ATTRIBUTES
        co2ambient (float): Ambient CO2 concentration (umol CO2/mol air)
        co2change (float): Annual change in ambient [CO2] (umol CO2/mol air/year)
        parscatter (float): PAR scattering coefficient (unitless)
        parabsorb (float): PAR absorption coefficient (unitless)
        parsoil (float): PAR reflection off soil surface (unitless)
        quantum_yield (float): Quantum efficiency/yield (umol CO2/umol photons)
        co2internal (float): Intercellular CO2 concentration (umol CO2/mol air)
        o2ambient (float): Ambient O2 concentration (umol O2/mol air)
        gap (float): Gap between canopies (unitless)
        extcoef (Extinction): Canopy extinction coefficient (unitless)
        clump (float): Canopy clump factor (unitless)
        refcoef (Reflect): PAR reflection coefficient (unitless)
        laicomp (LAI): Sunlit and shaded LAI components (m2 leaf/m2 ground)
        par (PAR): PAR components (units vary)
        assimcoef (AssimCoef): Assimilation coefficients (units vary)
        leafassim (LeafAssim): CO2 assimilation by leaves (umol CO2/m2 leaf/s)
        canopyassim (float): CO2 assimilation by canopies (umol CO2/m2 leaf/s)
        dayassim (float): Daily CO2 assimilation by canopies (kg CH2O/palm/day)

    # METHODS
        ambientco2: Ambient CO2 concentration (umol CO2/mol air) for a given year
        update_co2ambient: Update ambient CO2 concentration
        canopy_extinction: Canopy extinction coefficients (unitless) for
                            direct and diffuse solar irradiance
        gap_fraction: Canopy gap fraction, viewed from zenith
                      (0 = no gap/openings, 1 = full opening)
        canopy_clump: Canopy clump (cluster) factor (0-1) (unitless)
        reflection_coef: Reflection coefficients (unitless) for direct and diffuse PAR
        lai_components: Sunlit and shaded LAI (need to first supply total LAI) (m2 leaf/m2 ground)
        par_components: PAR components (umol photons/m2 leaf/s)
        set_assim_coefs: Temperature-dependent CO2 assimilation parameters/coefficients.
        co2_internal: Internal CO2 concentration (in plant) (umol CO2/mol air)
        leaf_assimilation: CO2 assimilation per leaf basis (umol CO2/m2 leaf/s)
        doy_has_changed: DOY has changed, so update the atmospheric [CO2]
        canopy_assimilation: Instantaneous CO2 assimilation per canopy basis (umol CO2/m2 leaf/s)
        daily_canopy_assimilation: Daily CO2 assimilation per canopy per day basis
                                   (kg CH2O/palm/day)
        update: Update the photosynthesis properties

    """

    def __init__(self, fname_in):
        """
        Create and initiliaze the Photosyn object.

        # Arguments
            fname_in (str): path and filename of the model initialization file

       """
        SoilWater.__init__(self, fname_in)   # initialize the parent class first

        d = self.ini
        co2 = d['co2ambient']  # ambient [CO2] (umol CO2/mol air if +ve, or year if -ve)
        # special code: a -ve co2 means the given input is a year, but a +ve input means [CO2]
        if co2 > 0:
            self.co2ambient = co2  # +ve input, so given input is [CO2]
        else:
            # -ve input, so determine [CO2] based on provided year
            self.co2ambient = Photosyn.ambientco2(-co2)
        # annual change in ambient [CO2] (umol CO2/mol air/year)
        self.co2change = d['co2change']
        self.parscatter = 0.8  # PAR scattering coefficient (unitless)
        self.parabsorb = 0.8  # PAR absorption coefficient (unitless)
        self.parsoil = 0.15  # PAR reflection off soil surface (unitless)
        self.quantum_yield = 0.051  # quantum efficiency/yield (umol CO2/umol photons)
        self.co2internal = 0.7 * self.co2ambient  # intercellular [CO2] (umol CO2/mol air)
        self.o2ambient = 210000.0  # ambient O2 concentration (umol O2/mol air)
        self.extcoef = Extinction(0.5, 0.5)  # canopy extinction coefficient (unitless)
        self.gap = 1.0    # open canopies
        self.clump = 1.0  # canopy clump factor (unitless)
        self.refcoef = Reflect(0.04, 0.04)  # PAR reflection coefficient (unitless)
        self.laicomp = LAI(0.0, 0.0, 0.0)  # Sunlit and shaded LAI (m2 leaf/m2 ground)
        self.par = PAR(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)  # PAR components (units vary)
        # Assimilation coefficients (units vary)
        self.assimcoef = AssimCoef(270.0, 16500.0, 2800.0, 100.0, 35.0)
        # CO2 assimilation by leaves (umol CO2/m2 leaf/s)
        self.leafassim = LeafAssim(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        self.canopyassim = 0.0  # CO2 assimilation by canopies (umol CO2/m2 leaf/s)
        self.dayassim = 0.0  # daily CO2 assimilation by canopies (kg CH2O/palm/day)

    @staticmethod
    def ambientco2(year):
        """
        Calculate the mean annual ambient [CO2] (umol CO2/mol air) for a given year.

        !!! note
            `ambientco2` is a static method.

        # Arguments
            year (int): year

        # Returns
            float: ambient CO2 concentration

        """
        a, b, c = 39413600.0, -40620.1096, 10.49094
        return math.sqrt(a + b * year + c * year ** 2)

    def update_co2ambient(self):
        """
        Update ambient CO2 concentration.

        # Returns
            None:

        """
        self.co2ambient += self.co2change / 365     # change per day

    def canopy_extinction(self):
        """
        Canopy extinction coefficients (unitless) for direct and diffuse solar irradiance.

        # Returns
            Extinction: `namedtuple` containing direct and diffuse extinction coefficients
                        (`float`)

        """
        # k is very high and nonsensical for hours before sunrise and after sunset, so cap it
        kdr = min(10.0, 0.5 / math.cos(self.solarpos.inc))
        lai = self.lai
        kdf = math.exp(0.038042 - 0.38845 * lai ** 0.5)
        return Extinction(kdr, kdf)

    def gap_fraction(self):
        """
        Canopy gap fraction, viewed from zenith (0 = no gap/openings, 1 = full opening).

        # Returns
            float: gap fraction (0-1)

        """
        return 1 / (1 + 1.33 * math.sqrt(self.lai))

    def canopy_clump(self):
        """
        Canopy clump (cluster) factor (0-1) (unitless).

        # Returns
            float: canopy clumpy/cluster coefficient/factor

        """
        kdrlai = self.extcoef.kdr * self.lai
        gap = self.gap
        w0 = -math.log(gap + (1 - gap) * math.exp(-kdrlai / (1 - gap))) / kdrlai
        return w0 + 6.6557 * (1 - w0) * math.exp(-math.exp(-self.solarpos.inc + 2.2103))

    def reflection_coef(self):
        """
        Reflection coefficients (unitless) for direct and diffuse PAR.

        # Returns
            Reflect: `namedtuple` containing direct and diffuse reflection coefficients (`float`)

        """
        a = math.sqrt(self.parscatter) * self.lai
        pdr = max(0.04, self.parsoil * math.exp(-2 * self.extcoef.kdr * self.clump * a))
        pdf = max(0.04, self.parsoil * math.exp(-2 * self.extcoef.kdf * a))
        return Reflect(pdr, pdf)

    def lai_components(self):
        """
        Sunlit and shaded LAI (need to first supply total LAI) (m2 leaf/m2 ground).

        # Returns
            LAI: `namedtuple` containing total, sunlit, and shaded leaf area index (`float`)

        """
        total = self.lai
        a = self.extcoef.kdr * self.clump
        lsl = (1 - math.exp(-a * total)) / a
        lsh = total - lsl
        return LAI(total, lsl, lsh)

    def par_components(self):
        """
        PAR components (umol photons/m2 leaf/s).

        Outside, within canopies, and that absorbed by canopies.

        # Returns
            PAR: `namedtuple` containing the PAR components (`float`)

        """
        # outside PAR (umol photons/m2 ground/s):
        # 50% of solar radiation = PAR, and 1 W/m2 = 4.55 umol photons/m2/s
        qdr = self.rad.direct * 0.5 * 4.55
        qdf = self.rad.diffuse * 0.5 * 4.55
        a = self.extcoef.kdr * self.clump * self.lai
        b = math.sqrt(self.parscatter)
        # within canopies PAR (umol photons/m2 ground or leaf/s):
        # umol photons/m2 ground/s
        q_p_dr_scatter = (1 - self.refcoef.pdr) * qdr * math.exp(-a * b)
        q_p_dr = (1 - self.refcoef.pdr) * qdr * math.exp(-a)  # umol photons/m2 ground/s
        q_p_scatter = 0.5 * (q_p_dr_scatter - q_p_dr)  # umol photons/m2 leaf/s
        a = self.extcoef.kdf * b * self.lai
        q_p_df = ((1 - self.refcoef.pdf) * qdf * (1 - math.exp(-a))) / a  # umol photons/m2 leaf/s
        # absorbed PAR by sunlit and shaded leaves (umol photons/m2 leaf/s):
        qsl = self.parabsorb * (self.extcoef.kdr * self.clump * qdr + q_p_df + q_p_scatter)
        qsh = self.parabsorb * (q_p_df + q_p_scatter)
        return PAR(qdr, qdf, q_p_dr_scatter, q_p_dr, q_p_scatter, q_p_df, qsl, qsh)

    def set_assim_coefs(self, canopytemp):
        """
        Temperature-dependent CO2 assimilation parameters/coefficients.

        Photosynthesis parameters determined in this method are as follows
        ```text
            Kc (umol/mol) - Michaelis-Menten constant for CO2
            Ko (umol/mol) - Michaelis-Menten constant for O2
            specificity (unitless) - CO2 / O2 specificity factor
            Vcmax (umol CO2/m2 leaf/s) - Rubisco maximum capacity rate, and
            CO2 pt (umol CO2/mol) - CO2 compensation point
        ```

        # Arguments
            canopytemp (float): foliage temperature (deg. C)

        # Returns
            AssimCoef: `namedtuple` contining photosynthesis parameters (`float`)

        """
        # lists for Kc, Ko, specificity, then Vcmax
        # (each parameter's 25 deg C value then its Q10 value)
        vcmax25 = 87.935 - 0.0026 * self.treeage   # Vcmax declines with tree age
        params = ([270.0, 2.786], [165000.0, 1.355], [2800.0, 0.703], [vcmax25, 2.573])
        adj_params = list()
        for param in params:
            adj_params.append(param[0] * math.pow(param[1], (canopytemp - 25) / 10))
        # additional temperature correction just for Vcmax
        adj_params[3] /= 1 + math.exp(0.29 * (canopytemp - 40))
        adj_params.append(0.5 * self.o2ambient / adj_params[2])  # add CO2 compensation point
        return AssimCoef(*adj_params)

    def co2_internal(self, canopytemp):
        """
        Internal CO2 concentration (in plant) (umol CO2/mol air).

        # Arguments
            canopytemp (float): foliage temperature (deg. C)

        # Returns
            float: intercellular CO2 concentration

        """
        # vapor pressure deficit in leaf: > 65 mbar, after which full stomatal closure in oil palm
        vpdleaf = min(65.0, self.svp_fn(canopytemp) - self.vp)
        a, b = 0.0615, 0.0213  # empirical coefficients for intercellular CO2 (Ci) vs VPD
        ca = self.co2ambient
        ci = ca * (1 - (1 - self.assimcoef.co2pt / ca) * (a + b * vpdleaf))
        return ci

    def leaf_assimilation(self):
        """
        CO2 assimilation per leaf basis (umol CO2/m2 leaf/s).

        # Returns
            LeafAssim: namedtuple containing CO2 assimilation rates (float)

        """
        # no photosynthesis if internal CO2 is less than CO2 compensation point
        co2diff = max(0.0, self.co2internal - self.assimcoef.co2pt)
        vc = self.assimcoef.vcmax * co2diff
        n = 1 + self.o2ambient / self.assimcoef.mmo2
        vc /= self.assimcoef.mmco2 * n + self.co2internal
        a = co2diff / (self.co2internal + 2 * self.assimcoef.co2pt)
        a *= self.quantum_yield * self.parabsorb
        vqsl, vqsh = self.par.abssunlit * a, self.par.absshaded * a
        vs = self.assimcoef.vcmax * 0.5
        sunlit = min(vc, vqsl, vs)
        shaded = min(vc, vqsh, vs)
        return LeafAssim(vc, vqsl, vqsh, vs, sunlit, shaded)

    def canopy_assimilation(self, canopytemp):
        """
        Set the instantaneous CO2 assimilation per canopy basis (umol CO2/m2 leaf/s).

        # Arguments
            canopytemp (float/Float): foliage temperature (deg. C)

        # Returns
            None:

        """
        self.gap = self.gap_fraction()
        self.extcoef = self.canopy_extinction()
        self.clump = self.canopy_clump()
        self.refcoef = self.reflection_coef()
        self.laicomp = self.lai_components()
        self.par = self.par_components()
        tf = canopytemp.real    # normal float number or Float wrapper of float numbers
        self.assimcoef = self.set_assim_coefs(tf)
        self.co2internal = self.co2_internal(tf)
        self.leafassim = self.leaf_assimilation()
        self.canopyassim = self.leafassim.sunlit * self.laicomp.sunlit
        self.canopyassim += self.leafassim.shaded * self.laicomp.shaded

    def daily_canopy_assimilation(self, canopytemp):
        """
        Set the daily CO2 assimilation per canopy per day basis (kg CH2O/palm/day).

        # Arguments
            canopytemp (float/Float): foliage temperature (deg. C)

        # Returns
            None:

        """
        def _assim(tf):
            self.canopy_assimilation(tf)
            return self.canopyassim,  # integrate requires a tuple type return

        ans = self.integrate(5, self.sunrise, self.sunset, _assim, canopytemp)
        ans = ans[0]  # get the canopy assimilation result (result is a tuple type)
        ans *= 1.08 / self.plantdens  # convert umol CO2/m2 leaf/day to kg CH2O/palm/day
        self.dayassim = ans

    def doy_has_changed(self):
        """
        DOY has changed, so update the atmospheric [CO2].

        # Returns
            None

        """
        self.update_co2ambient()
        SoilWater.doy_has_changed(self)

    def update(self, external_info):
        """
        Update the photosynthesis properties.

        # Arguments
            external_info (dict): requires information on canopy/foliage temperature (deg. C)

        # Returns
            None:

        """
        self.daily_canopy_assimilation(external_info['canopytemp'])
        external_info['assimilates'] = self.dayassim    # info on assimilates for SoilWater
        SoilWater.update(self, external_info)
