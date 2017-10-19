"""
Energy balance module.

Model the energy fluxes in the soil-plant-atmosphere system.

# Author - Christopher Teh Boon Sung
------------------------------------

"""

import math
from collections import namedtuple

from photosyn import Photosyn
from utils import Float

LeafDim = namedtuple('LeafDim', ['length', 'width'])
LeafDim.__doc__ = '`' + LeafDim.__doc__
LeafDim.__doc__ += '`\r\nnamedtuple: Leaflet dimension'
LeafDim.length.__doc__ = 'float: mean length of a single leaflet'
LeafDim.width.__doc__ = 'float: mean width of a single leaflet'

StomatalStresses = namedtuple('StomatalStresses', ['water', 'vpd', 'par'])
StomatalStresses.__doc__ = '`' + StomatalStresses.__doc__
StomatalStresses.__doc__ += '`\r\nnamedtuple: Stresses that would reduce stomatal conductivity'
StomatalStresses.water.__doc__ = 'float: reduction due to water stress'
StomatalStresses.vpd.__doc__ = 'float: reduction due to vapor pressure deficit'
StomatalStresses.par.__doc__ = 'float: reduction due to insufficient solar irradiance'

AvailEnergy = namedtuple('AvailEnergy', ['total', 'crop', 'soil', 'net', 'g'])
AvailEnergy.__doc__ = '`' + AvailEnergy.__doc__
AvailEnergy.__doc__ += '`\r\nnamedtuple: Available radiation to the soil-plant-atmosphere system'
AvailEnergy.total.__doc__ = 'float: radiation available to both crop and soil (total)'
AvailEnergy.crop.__doc__ = 'float: radiation available to the crop'
AvailEnergy.soil.__doc__ = 'float: radiation available to the soil'
AvailEnergy.net.__doc__ = 'float: net radiation'
AvailEnergy.g.__doc__ = 'float: soil heat flux'

Resistances = namedtuple('Resistances', ['rsa', 'raa', 'rca', 'rst', 'rcs', 'rss'])
Resistances.__doc__ = '`' + Resistances.__doc__
Resistances.__doc__ += '`\r\nnamedtuple: Resistances to heat fluxes'
Resistances.rsa.__doc__ = 'float: aerodynamic resistance between soil and mcf (mean canopy flow)'
Resistances.raa.__doc__ = 'float: aerodynamic resistance between mcf and the reference level'
Resistances.rca.__doc__ = 'float: boundary layer resistance'
Resistances.rst.__doc__ = 'float: leaf stomatal resistance'
Resistances.rcs.__doc__ = 'float: canopy resistance'
Resistances.rss.__doc__ = 'float: soil resistance'

HeatFluxes = namedtuple('HeatFluxes', ['total', 'crop', 'soil'])
HeatFluxes.__doc__ = '`' + HeatFluxes.__doc__
HeatFluxes.__doc__ += '`\r\nnamedtuple: Heat flux components'
HeatFluxes.total.__doc__ = 'float total heat flux (crop + soil)'
HeatFluxes.crop.__doc__ = 'float heat flux from the crop'
HeatFluxes.soil.__doc__ = 'float heat flux from the soil'


class EnergyBal(Photosyn):
    """
    Energy balance class.

    Model the energy fluxes in the soil-plant-atmosphere system, using the electrical network
    analogy, where the system is described as a network of resistances where various heat fluxes
    must traverse a series of resistances to a reach a given reference height.

    This class determines the canopy/foliage temperature which is used by the Photosynthesis model
    component to determine the canopy photosynthesis.

    # CLASS ATTRIBUTES
        psycho (float): psychometric constant (0.658 mbar/K)
        pcp (float): vol. heat capacity (1221.09 J/m3/K)
        soilroughlen (float): soil roughness length for flat, tilled land (0.004 m)
        vonk (float): von Karman constant (0.4)

    !!! note
        All the above class attributes are supposed to be treated as constants.

    # ATTRIBUTES
        refhgt (float): Reference height (m)
        d (float): Zero plane displacement (m)
        z0 (float): Crop roughness length (m)
        windext (float): Wind extinction coefficient (unitless)
        eddyext (float): Eddy diffusivity extinction coefficient (unitless)
        leafdim (LeafDim): Leaflet dimension (m)
        stressfn (StomatalStresses): Reduction in stomatal conductance due to stresses
        availegy (AvailEnergy): Available energy (W/m2)
        ustar (float): Friction velocity (m/s)
        ucrophgt (float): Wind speed at crop height (m/s)
        res (Resistances): Flux resistances (s/m)
        et (HeatFluxes): Latent heat flux components (W/m2)
        h (HeatFluxes): Sensible heat flux components (W/m2)
        canopytemp (float): Canopy/foliage temperature (deg. C)
        dayet (HeatFluxes): Daily latent heat flux components (mm water/day)
        dayh (HeatFluxes): Daily sensible heat flux components (MJ/m2/day)

    # METHODS
        windspeed_profile_params: Windspeed profile paramaters
        leaf_dimension: Mean length and width of leaflets (m)
        stomatal_cond_stresses: Reduction in stomatal conductance due to
                                various stresses (unitless)
        available_energy: Available energy (W/m2) to crop and soil (net radiation partitioning)
        res_rss: Soil resistance (s/m)
        friction_velocity: Friction velocity (m/s)
        windspd_at_crophgt: Wind speed at crop/tree height (m/s)
        windspd_at_refhgt: Extrapolated wind speed from weather station
                           height to reference height (m/s)
        res_rsa: Aerodynamic resistance between soil and mcf (mean canopy flow) (s/m)
        res_raa: Aerodynamic resistance between mcf and reference height (s/m)
        effective_lai: Effective LAI (m2 leaf/m2 ground)
        res_rca: Boundary layer resistance (s/m)
        res_rcs_st: Canopy and stomatal resistance (s/m)
        resistances: Flux resistances (s/m)
        calc_all_fluxes: Calculate the various latent and sensible heat fluxes (W/m2)
        canopy_temperature: Canopy/foliage temperature (deg C)
        set_heat_fluxes: Instantaneous heat fluxes (W/m2)
        set_daily_immutables: Set constants that do not change within a day
        daily_heat_balance: Solve for daily fluxes for latent heat (mm water/day) and
                            sensible heat (MJ/m2/day)
        update: Update the energy balance properties
        next_hour: Generator to increment the hour and then update the model properties

    """

    # constants:
    psycho = 0.658  # psychometric constant mbar/K
    pcp = 1221.09   # vol. heat capacity J/m3/K
    soilroughlen = 0.004  # soil roughness length for flat, tilled land (m)
    vonk = 0.4      # von Karman constant

    def __init__(self, fname_in):
        """
        Create and initialize the EnergyBal object.

        # Arguments
            fname_in (str): path and filename of the model initialization file

        """
        Photosyn.__init__(self, fname_in)   # initialize the parent class first

        d = self.ini
        self.refhgt = d['refhgt']  # reference height (m)

        self.d = 0.0  # zero plane displacement (m)
        self.z0 = 0.0  # crop roughness length (m)
        self.windext = 0.0  # wind extinction coefficient (unitless)
        self.eddyext = 0.0  # eddy diffusivity extinction coefficient (unitless)
        self.leafdim = LeafDim(0.0, 0.0)  # leaflet dimension (m)
        # reduction in stomatal conductance from stresses
        self.stressfn = StomatalStresses(1.0, 1.0, 1.0)
        self.availegy = AvailEnergy(0.0, 0.0, 0.0, 0.0, 0.0)  # available energy (W/m2)
        self.ustar = 0.0  # friction velocity (m/s)
        self.ucrophgt = 0.0  # wind speed at crop height (m/s)
        self.res = Resistances(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)  # flux resistances (s/m)
        self.et = HeatFluxes(0.0, 0.0, 0.0)  # latent heat flux components (W/m2)
        self.h = HeatFluxes(0.0, 0.0, 0.0)  # sensible heat flux components (W/m2)
        self.canopytemp = 25.0  # canopy/foliage temperature (deg. C)
        self.dayet = HeatFluxes(0.0, 0.0, 0.0)  # daily latent heat flux components (mm water/day)
        self.dayh = HeatFluxes(0.0, 0.0, 0.0)  # daily sensible heat flux components (MJ/m2/day)

    def windspeed_profile_params(self):
        """
        Windspeed profile paramaters.

        Paramaters calculated are as follows
        ```text
            zero plane displacement, d (m)
            crop roughness length, z0 (m)
            vertical profile extinction coeffiicient (unitless) for:
                wind speed
                eddy diffusivity
        ```

        # Returns
            tuple: windspeed profile parameters (float)

        """
        ustar2u_h = 0.32    # related to foliage drag coefficient
        h = self.treehgt    # tree height
        # wind speed extinction coefficient (leaflet mean length = 1 m):
        windext = 3 * (1 - math.exp(-self.lai))
        n = 2 * windext
        dhd = min(0.95, max(0.3, 1 - (math.exp(-n) / n * (math.exp(n) - 1))))
        d = dhd * h     # zero plane displacement height, d (m)
        dhz0 = (1 - dhd) * math.exp(-EnergyBal.vonk / ustar2u_h)
        z0 = dhz0 * h   # crop roughness length, z0 (m)
        return d, z0, windext, windext      # assume eddy = wind extinction coefficient

    def leaf_dimension(self):
        """
        Mean length and width of leaflets (m).

        # Returns
            LeafDim: `namedtuple` containing the leaf dimensions (`float`)

        """
        age = self.treeage / 365  # tree age in years
        l = 0.2191 * math.log(age) + 0.475  # leaflet mean length (m)
        w = 0.0152 * math.log(age) + 0.0165  # leaflet mean width (m)
        return LeafDim(l, w)

    def stomatal_cond_stresses(self):
        """
        Reduction in stomatal conductance due to various stresses (unitless).

        # Returns
            StomatalStresses: `namedtuple` containing the stresses

        """
        def _stress_by_vpd():
            """Reduction in stomatal conductance due to VPD (unitless)."""
            def _gst_vpd(vpd):
                """Relationship between stomatal conductance and VPD (m/s)."""
                return -0.007516 * math.log(vpd) + 0.031970

            # conductance declines with increasing VPD
            gstmin = _gst_vpd(65.0)     # VPD for min. conductance
            gstmax = _gst_vpd(10.0)     # VPD for max. conductance
            gst = min(gstmax, max(gstmin, _gst_vpd(max(10.0, self.vpd))))
            return gst / gstmax

        def _stress_by_par():
            """Reduction in stomatal conductance due to PAR (unitless)."""
            def _gst_par(par):
                """Relationship between stomatal conductance and PAR (m/s)."""
                return 0.014614 * (1 - math.exp(-0.008740 * par))

            # conductance increases with increasing PAR
            gstmin = _gst_par(0.1)  # PAR for min. conductance (not 0, avoid divide-by-zero later)
            gstmax = _gst_par(330.0)  # PAR for max. conductance
            partotal = self.rad.total * 0.5  # total PAR in W/m2
            gst = min(gstmax, max(gstmin, _gst_par(partotal)))
            return gst / gstmax

        return StomatalStresses(self.waterstresses.crop, _stress_by_vpd(), _stress_by_par())

    def available_energy(self):
        """
        Available energy (W/m2) to crop and soil (net radiation partitioning).

        # Returns
            AvailEnergy: `namedtuple` containing the available energy
                         to the system and its components

        """
        tc = 0.05  # portion of Rn as soil heat flux under full canopy
        ts = 0.315  # portion of Rn as soil heat flux for bare soil (no canopy cover)
        pfn = math.exp(-self.extcoef.kdr * self.clump * math.sqrt(0.5) * self.lai)
        gap = max(self.gap, pfn)  # penetration of Rn into canopies
        rn = self.netrad  # net radiation (Rn)
        acrp = (1 - gap) * (1 - tc) * rn  # Rn portion to crop
        asol = gap * (1 - ts) * rn  # Rn portion to soil
        atot = acrp + asol  # available to both crop and soil
        g = (tc + gap * (ts - tc)) * rn  # Rn portion as soil heat flux
        return AvailEnergy(atot, acrp, asol, rn, g)

    def res_rss(self):
        """
        Soil resistance (s/m).

        # Returns
            float: soil resistance

        """
        topsoil = self.layers[0]  # diffusion out only from the first soil layer
        tau = math.sqrt(topsoil.swc.porosity + 3.79 * (1 - topsoil.swc.porosity))  # tortuosity
        dmv = 24.7 * 10 ** (-6)  # vapor diffusion coefficient, m2/s
        rssmax = tau * topsoil.thick / (topsoil.swc.porosity * dmv)
        return rssmax * math.exp(-topsoil.vwc / (topsoil.swc.psd * topsoil.swc.sat))

    def friction_velocity(self):
        """
        Friction velocity (m/s).

        # Returns
            float: friction velocity

        # Raises
            ArithmeticError: raised when tree is taller than reference height

        """
        if self.refhgt < self.treehgt:
            raise ArithmeticError('Tree height has exceeded reference height.')
        windspd = self.windspd_at_refhgt()
        return EnergyBal.vonk * windspd / math.log((self.refhgt - self.d) / self.z0)

    def windspd_at_crophgt(self):
        """
        Wind speed at crop/tree height (m/s).

        # Returns
            float: wind speed at the tree height

        """
        return (self.ustar / EnergyBal.vonk) * math.log((self.treehgt - self.d) / self.z0)

    def windspd_at_refhgt(self):
        """
        Wind speed (m/s) at reference height.

        Wind speed measured at weather station height may not be the same
        as the reference height (thus, wind speed will have to be extrapolated to the
        reference height).

        # Returns
            float: wind speed at reference height

        """
        ws = self.windspd  # wind speed at weather station height
        z0 = 0.03  # roughness length for open agricultural fields (m)
        # extrapolation by log law to determine wind speed at the reference height
        return ws * math.log(self.refhgt / z0) / math.log(self.methgt / z0)

    def res_rsa(self):
        """
        Aerodynamic resistance between soil and mcf (mean canopy flow) (s/m).

        # Returns
            float: aerodynamic resistance between soil and mcf

        """
        n = self.eddyext
        a = math.exp(n) / (n * EnergyBal.vonk * self.ustar)
        b = math.exp(-n * EnergyBal.soilroughlen / self.treehgt)
        c = math.exp(-n * (self.z0 + self.d) / self.treehgt)
        return a * (b - c)

    def res_raa(self):
        """
        Aerodynamic resistance between mcf (mean canopy flow) and reference height (s/m).

        # Returns
            float: aerodynamic resistance between mcf and reference height

        """
        n = self.eddyext
        a = EnergyBal.vonk * self.ustar
        b = math.log((self.refhgt - self.d) / (self.treehgt - self.d)) / a
        c = 1 - (self.z0 + self.d) / self.treehgt
        d = (math.exp(n * c) - 1) / (n * a)
        return b + d

    def effective_lai(self):
        """
        Effective LAI (m2 leaf/m2 ground).

        # Returns
            float: effective LAI

        """
        efflai = 0.5 * self.laimax
        return min(self.lai, efflai)

    def res_rca(self):
        """
        Boundary layer resistance (s/m).

        # Returns
            float: boundary layer resistance

        """
        n = self.windext
        a = (1 - math.exp(-n / 2)) * math.sqrt(self.ucrophgt / self.leafdim.width)
        return n / (0.01 * self.effective_lai() * a)

    def res_rcs_st(self):
        """
        Canopy and stomatal resistance (s/m).

        # Returns
            float: Canopy and stomatal resistance

        """
        gstmax = 0.0125  # maximum stomatal conductance, in m/s, equivalent to 500 mmol/m2/s
        gst = gstmax * self.stressfn.water * self.stressfn.vpd * self.stressfn.par
        gcs = gst * self.effective_lai()
        return 1 / gst, 1 / gcs

    def resistances(self):
        """
        Flux resistances (s/m).

        # Returns
            Resistances: `namedtuple` containing all the resistances (`float`)

        """
        rsa = self.res_rsa()
        raa = self.res_raa()
        rca = self.res_rca()
        rst, rcs = self.res_rcs_st()
        rss = self.res_rss()
        return Resistances(rsa, raa, rca, rst, rcs, rss)

    def calc_all_fluxes(self):
        """
        Calculate the various latent and sensible heat fluxes (W/m2).

        # Returns
            HeatFluxes: `namedtuple` containing the components of latent and sensible heat fluxes
                         (`float`)

        """
        psycho = EnergyBal.psycho
        pcp = EnergyBal.pcp
        slope = self.slopesvp
        vpd = self.vpd
        raa = self.res.raa
        rca = self.res.rca
        rsa = self.res.rsa
        rcs = self.res.rcs
        rss = self.res.rss
        atotal = self.availegy.total
        acrop = self.availegy.crop
        asoil = self.availegy.soil
        ra = (slope + psycho) * raa
        rc = (slope + psycho) * rca + psycho * rcs
        rs = (slope + psycho) * rsa + psycho * rss
        cc = 1 / (1 + rc * ra / (rs * (rc + ra)))
        cs = 1 / (1 + rs * ra / (rc * (rs + ra)))
        pmc = slope * atotal + (pcp * vpd - slope * rca * asoil) / (raa + rca)
        pmc /= slope + psycho * (1 + rcs / (raa + rca))
        pms = slope * atotal + (pcp * vpd - slope * rsa * acrop) / (raa + rsa)
        pms /= slope + psycho * (1 + rss / (raa + rsa))
        et = cc * pmc + cs * pms
        vpd0 = vpd + (raa / pcp) * (slope * atotal - (slope + psycho) * et)
        etc = slope * acrop + pcp * vpd0 / rca
        etc /= slope + psycho * (rcs + rca) / rca
        ets = slope * asoil + pcp * vpd0 / rsa
        ets /= slope + psycho * (rss + rsa) / rsa
        hc = psycho * acrop * (rcs + rca) - pcp * vpd0
        hc /= slope * rca + psycho * (rcs + rca)
        hs = psycho * asoil * (rss + rsa) - pcp * vpd0
        hs /= slope * rsa + psycho * (rss + rsa)
        return HeatFluxes(et, etc, ets), HeatFluxes(hc + hs, hc, hs)

    def canopy_temperature(self):
        """
        Canopy/foliage temperature (deg. C).

        # Returns
            float: canopy temperature

        """
        delta = self.h.crop * self.res.rca + (self.h.soil + self.h.crop) * self.res.raa
        return delta / EnergyBal.pcp + self.airtemp

    def set_heat_fluxes(self):
        """
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

        # Returns
            None:

        """
        self.stressfn = self.stomatal_cond_stresses()
        self.availegy = self.available_energy()
        self.ustar = self.friction_velocity()
        self.ucrophgt = self.windspd_at_crophgt()
        self.res = self.resistances()
        self.et, self.h = self.calc_all_fluxes()
        self.canopytemp = self.canopy_temperature()  # set the foliage temperature

    def set_daily_immutables(self):
        """
        Set constants that do not change within a day.

        Sets parameters that will not change within the same day. This speeds up hourly
        calculations carried out for the same day.

        # Returns
            None:

        """
        self.leafdim = LeafDim(*list(self.leaf_dimension()))
        self.d, self.z0, self.windext, self.eddyext = self.windspeed_profile_params()

    def _tf(self):
        """
        Saved function to `call _heat_fluxes()` method to determine canopy temperature (deg. C).

        Used in `utils.Float` objects to call `set_heat_fluxes()` to determine the foliage
        temperature which will then be used in `Photosyn.canopy_assimilation()` (which requires
        foliage temperature in the function argument) to determine canopy photosynthesis.


        # Returns
            float: foliage temperature

        """
        self.set_heat_fluxes()  # calling this function will set the foliage temperature
        return self.canopytemp  # updated foliage temperature

    def _itg(self):
        """
        Instantaneous photosynthesis (umol CO2/m2 leaf/s) and heat fluxes (W/m2).

        Uses `NumberProxy` class to calculate the heat fluxes and work out the
        foliage temperature which is then used in canopy photsynthesis.


        # Returns
            tuple: canopy assimilation and heat fluxes (`HeatFluxes`)

        """
        self.canopy_assimilation(Float(self._tf))
        return (self.canopyassim,) + self.et + self.h

    def daily_heat_balance(self):
        """
        Solve for daily fluxes for latent (mm water/day) and sensible (MJ/m2/day) heat.

        # Returns
            None:

        """
        self.set_daily_immutables()    # set the day constants (those that don't change in a day)
        ans = self.integrate(5, 0, 24, self._itg)
        # throw away the canopy assimilation result (first value), keep flux results
        self.dayet = HeatFluxes(*list(v * 3600 / 2454000 for v in ans[1:4]))  # in mm water/day
        self.dayh = HeatFluxes(*list(v * 3600 / 10 ** 6 for v in ans[4:]))  # in MJ/m2/day

    def update(self, external_info):
        """
        Update the energy balance properties.

        # Arguments
            external_info (dict): will be used to pass information needed by parent classes

        # Returns
            None:

        """
        self.daily_heat_balance()  # daily losses of water by evapotranspiration
        # provides information for Photosyn
        external_info['canopytemp'] = Float(self._tf)
        external_info['petcrop'] = self.dayet.crop
        external_info['petsoil'] = self.dayet.soil
        Photosyn.update(self, external_info)

    def next_hour(self, duration):
        """
        Generator to increment the hour and then update the model properties.

        Hour moves forward an hour day at a time within the same day, where for each hour shift,
        the model properties are updated.

        # Arguments
            duration (int): number of cycles/steps to increment the hour and model update

        # Yields
            int: current hour run

        """
        for i in range(duration):
            self.update_weather(nexthour=i)  # move forward an hour at a time
            if i == 0:
                self.set_daily_immutables()  # same day, same values for these immutables
            self._itg()
            yield i
