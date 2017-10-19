"""
Soil water movement and content module.

Model one-dimensional soil water movement (fluxes).
Includes groundwater (assumes constant water table depth).

# Author - Christopher Teh Boon Sung
------------------------------------

"""

import math
from collections import namedtuple

from crop import Crop


SWC = namedtuple('SWC', ['sat', 'fc', 'pwp', 'psd', 'porosity', 'airentry'])
SWC.__doc__ = '`' + SWC.__doc__
SWC.__doc__ += '`\r\nnamedtuple: Soil water characteristics'
SWC.sat.__doc__ = 'float: saturation point'
SWC.fc.__doc__ = 'float: field capacity'
SWC.pwp.__doc__ = 'float: permanent wilting point'
SWC.psd.__doc__ = 'float: pore-size distribution'
SWC.porosity.__doc__ = 'float: soil porosity'
SWC.airentry.__doc__ = 'float: air-entry value'

Texture = namedtuple('Texture', ['clay', 'sand', 'om'])
Texture.__doc__ = '`' + Texture.__doc__
Texture.__doc__ += '`\r\nnamedtuple: Soil texture'
Texture.clay.__doc__ = 'float: percentage of clay'
Texture.sand.__doc__ = 'float: percentage of sand'
Texture.om.__doc__ = 'float: percentage of organic matter'

AET = namedtuple('AET', ['crop', 'soil'])
AET.__doc__ = '`' + AET .__doc__
AET.__doc__ += '`\r\nnamedtuple: Actual or reduction to evapotranspiration (ET)'
AET.crop.__doc__ = 'float: actual crop transpiration (or reduction of crop potential transpiration)'
AET.soil.__doc__ = 'float: actual soil evaporation (or reduction of soil potential evaporation)'


class RootWater(object):
    """
    Soil water characteristics in the rooting zone.

    # ATTRIBUTES
        wc (float): water content (mm)
        vwc (float): water content (m3/m3)
        critical (float): critical water content, below which plant water stress occurs (m3/m3)
        sat (float): saturation point (m3/m3)
        fc (float): field capacity (m3/m3)
        pwp (float): permanent wilting point (m3/m3)

    """

    def __init__(self):
        """
        Create and initialize the RootWater object.

        """
        self.wc = 0.0           # water content (mm)
        self.vwc = 0.0          # water content (m3/m3)
        self.critical = 0.0     # water content, below which plant water stress occurs (m3/m3)
        self.sat = 0.0          # saturation point (m3/m3)
        self.fc = 0.0           # field capacity (m3/m3)
        self.pwp = 0.0          # permanent wilting point (m3/m3)


class SoilLayer(object):
    """
    Soil layer properties class.

    The physical properties of a soil layer, dealing with soil water content and fluxes.

    # CLASS ATTRIBUTES
        flux_fields (list): list of flux names (str) to serve as dictionary keys which are
                            `['t', 'e', 'influx', 'outflux', 'netflux']`

    # ATTRIBUTES
        thick (float): Thickness of the soil layer (m)
        texture: Sand, clay, and organic matter (%)
        vwc (float): Vol. water content (m3/m3)
        wc (float): Water content (mm)
        accthick (float): Cumulative thickness (m)
        depth (float): Depth of layer from soil surface (m)
        swc (SWC): Soil water characteristics (varying units)
        ksat (float): Saturated hydraulic conductivity (m/day)
        k (float): Hydraulic conductivity (m/day)
        matric (float): Matric head (m)
        gravity (float): Gravity head (m)
        fluxes (dict): Water flux components stored in a dictionary

    The keys for the dictionary `fluxes` are as follows

    ```text
        't': Plant water uptake via transpiration (m/day)
        'e':  Loss of water via evaporation (m/day)
        'influx': Water entry into layer (m/day)
        'outflux': Water exit out of layer (m/day)
        'netflux': Difference between influx and outflux (m/day)
    ```

    # METHODS
        initialize_layer: Initialize all attributes
        update_heads_k: Update the matric head, gravity head, and
                        the unsaturated hydraulic conductivity
        tothead: Total/sum of matric and gravity head (m) - `getter` method

    # Note
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

    """

    __accdepth = 0.0    # internal use: used to determine a soil layer's depth
    flux_fields = ['t', 'e', 'influx', 'outflux', 'netflux']

    def __init__(self):
        """
        Create and initialize the SoilLayer object.

        """
        self.thick = 0.0
        self.texture = Texture(0.0, 0.0, 0.0)
        self.vwc = 0.0
        self.wc = 0.0
        self.accthick = 0.0
        self.depth = 0.0
        self.swc = SWC(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        self.ksat = 0.0
        self.k = 0.0
        self.matric = 0.0
        self.gravity = 0.0
        self.prevlayer = None
        self.nextlayer = None
        self.fluxes = {f: 0.0 for f in SoilLayer.flux_fields}

    def initialize_layer(self, prevlayer, nextlayer):
        """
        Initialize all soil layer attributes.

        !!! note
            This function will set the water content to be within the range of
            SAT and FC or between FC and PWP, if the volumetric water content
            is given as negative value. See this class's docstring above.

        # Arguments
            prevlayer (`SoilLayer`): previous soil layer (layer above current layer)
            nextlayer (`SoilLayer`): next soil layer (layer beneath current layer)

        # Returns
            None:

        """
        self.prevlayer = prevlayer
        self.nextlayer = nextlayer

        # 1. set layer depth and cumulative thickness:
        prevaccthick = self.prevlayer.accthick if self.prevlayer else 0.0
        self.accthick = self.thick + prevaccthick
        prevthick = self.prevlayer.thick if self.prevlayer else 0.0
        d = 0.5 * (prevthick + self.thick)
        self.depth = SoilLayer.__accdepth + d
        SoilLayer.__accdepth += d

        # 2. set soil water characteristics (Bittelli et al., 2015; Saxton & Rawls, 2008):
        c, s, om = self.texture
        s /= 100  # convert sand and clay from % to fraction, but om remains as %
        c /= 100
        # 2a. permanent wilting, field capacity, then saturation points:
        n1 = -0.024 * s + 0.487 * c + 0.006 * om
        n2 = 0.005 * (s * om) - 0.013 * (c * om) + 0.068 * (s * c) + 0.031
        theta1500t = n1 + n2
        theta1500 = theta1500t + (0.14 * theta1500t - 0.02)
        n1 = -0.251 * s + 0.195 * c + 0.011 * om
        n2 = 0.006 * (s * om) - 0.027 * (c * om) + 0.452 * (s * c) + 0.299
        theta33t = n1 + n2
        theta33 = theta33t + (1.283 * theta33t ** 2 - 0.374 * theta33t - 0.015)
        n1 = 0.278 * s + 0.034 * c + 0.022 * om
        n2 = - 0.018 * (s * om) - 0.027 * (c * om) - 0.584 * (s * c) + 0.078
        theta_s33t = n1 + n2
        theta_s33 = theta_s33t + 0.636 * theta_s33t - 0.107
        theta0 = theta33 + theta_s33 - 0.097 * s + 0.043
        # 2b. pore size distribution index (no unit):
        dg = math.exp(-1.96 * c + 2.3 * (1 - s - c) + 5.76 * s)
        b = 8.25 - 1.26 * math.log(dg)
        psd = 1 / b
        # 2c. air-entry suction (kPa):
        aire = 3.9 - 0.61 * math.log(dg)
        # 2d. store calculated soil water characteristics (assume porosity = saturation)
        self.swc = SWC(theta0, theta33, theta1500, psd, theta0, aire)
        # 3. saturated hydraulic conductivity (m/day):
        self.ksat = 864 * 0.07 * (theta0 - (1 - (aire / 33) ** psd)) ** 4

        # 4. check for special code:
        if self.vwc < 0:
            # given volumetric water content is a fraction between SAT, FC, and PWP:
            vwc = -self.vwc     # make a +ve
            fc = self.swc.fc
            if 1 <= vwc <= 2:
                # water content is between SAT and FC
                sat = self.swc.sat
                vwc = sat - (vwc - 1) * (sat - fc)      # linear interpolation
            elif 2 < vwc <= 3:
                # water content is between FC and PWP
                pwp = self.swc.pwp
                vwc = fc - (vwc - 2) * (fc - pwp)       # linear interpolation
            else:
                # out of range, so just set to FC
                vwc = fc
            self.vwc = vwc  # m3/m3
            self.wc = self.vwc * self.thick * 1000  # mm/day

        # 5. update the matric and gravity heads, then the hydraulic conductivity:
        self.update_heads_k()

    def update_heads_k(self):
        """
        Update matric and gravity heads (m), and unsaturated hydraulic conductivity (m/day).

        Update is based on current soil water content.

        # Returns
            None:

        """
        fc = self.swc.fc
        vwc = self.vwc      # current soil water content
        # matric suction, convert from kPa to m by dividing by 10
        if vwc >= fc:
            hm = (33 - (33 - self.swc.airentry) * (vwc - fc) / (self.swc.sat - fc)) / 10.0
        else:
            b = 1 / self.swc.psd
            a = math.exp(3.496508 + b * math.log(fc))
            hm = (a * max(0.05, vwc) ** (-b)) / 10.0
        # matric head (m)
        self.matric = max(0.0, hm)
        # gravity head (m) is always constant and equal to layer's depth from surface
        self.gravity = self.depth
        # unsaturated hydraulic conductivity (m/day)
        ae = self.swc.airentry / 10.0  # air entry (convert to m)
        hm = self.matric  # matric head (m)
        ratio = self.vwc / self.swc.sat
        if hm > ae:
            # unsaturated k is too large for lower layers, so correct it
            #    based on soil water measurements from UPM oil palm site
            ncorr = 1.0 if self.prevlayer is None else 0.2   # calibrate
            self.k = self.ksat * ratio ** (3 + ncorr * 2 / self.swc.psd)
        else:
            self.k = self.ksat

    @property
    def tothead(self):
        """
        Total head (m) - `getter` method.

        # Returns
            float: total head

        """
        return self.matric + self.gravity


class SoilWater(Crop):
    """
    Soil water balance class.

    Model the soil water flow in one dimension and water balance. Include the effect
    of groundwater, if any, but assume constant water table depth.

    # EXTERNAL INFORMATION REQUIRED (MUST BE SUPPLIED FROM AN EXTERNAL CLASS)

    ```text
        petcrop (float): Potential transpiration (from crop) (mm/day)
        petsoil (float): Potential evaporation (fro soil) (mm/day)
    ```

    # ATTRIBUTES
        numintervals (int): Number of intervals for integration within a day
        rootdepth (float): Rooting depth (m)
        has_watertable (bool): True if water table / groundwater is present, else False
        numlayers (int): Number of soil layers
        layers (list): List of SoilLayer objects (their numbers must match numlayers)
        rootwater (RootWater): Soil water characteristics in the root zone
        cf (list): List of dictionary of cumulative fluxes for every soil layer
        waterstresses (AET): Reduction to evaporation and transpiration due to water stress
        netrain (float): Net rainfall (mm/day)
        aet (AET): Actual water loss by evaporation and transpiration (mm/day)

    # METHODS
        net_rainfall: Net rainfall (mm/day)
        rooting_depth: Increase in rooting depth (m)
        update_rootwater: Update the water content and water characteristics in the rooting zone
        reduce_et: Reduction in evaporation and transpiration (0-1, 1=no stress, 0=max. stress)
        actual_et: Actual evaporation and transpiration (mm/day)
        influx_from_watertable: Influx of water from the water table (m/day).
        calc_water_fluxes: Calculate the various water fluxes (m/day) for all soil layers
        daily_water_balance: Solve for the water content in each soil layer
        update: Update the soil water properties by solving the water fluxes

    """

    def __init__(self, fname_in):
        """
        Create and initialize the SoilWater object.

        # Arguments
            fname_in (str): path and filename of the model initialization file

        """
        Crop.__init__(self, fname_in)   # initialize the parent class first

        d = self.ini
        self.numintervals = d['numintervals']  # number of intervals for integration within a day
        self.rootdepth = d['rootdepth']  # rooting depth (m)
        self.has_watertable = d['has_watertable']     # has a water table / groundwater?
        self.numlayers = d['numlayers']  # the number of soil layers
        self.layers = [SoilLayer() for _ in range(self.numlayers)]  # create the soil layers

        # read in the properties for each soil layer. If there is a water table, the last soil
        #    layer is assumed to border the water table surface
        dl = d['layers']
        for i, layer in enumerate(self.layers):
            layer.thick = dl[i]['thick']  # thickness of each soil layer (m)
            layer.vwc = dl[i]['vwc']  # vol. water content in m3/m3
            layer.wc = layer.vwc * layer.thick * 1000  # convert from m3/m3 to mm water
            tex = dl[i]['texture']  # clay, sand, and OM percentages (%)
            layer.texture = Texture(tex['clay'], tex['sand'], tex['om'])

        # initialize the soil layers (those that do not change with water content)
        for i in range(self.numlayers):
            prevlayer = self.layers[i - 1] if i > 0 else None
            nextlayer = self.layers[i + 1] if i < self.numlayers - 1 else None
            self.layers[i].initialize_layer(prevlayer, nextlayer)

        # internal use: speedier calculations: proxy to store intermediate water flux values
        #    fluxes within a sub-interval daily time step
        self.__pf = [{f: 0.0 for f in SoilLayer.flux_fields} for _ in range(self.numlayers)]

        # cumulative fluxes at the end of a daily time step
        self.cf = [{f: 0.0 for f in SoilLayer.flux_fields} for _ in range(self.numlayers)]
        # root zone water characteristics:
        self.rootwater = RootWater()
        self.update_rootwater()  # amount of water in the root zone (mm and m3/m3)
        # reduction to evaporation and transpiration due to water stress
        self.waterstresses = self.reduce_et()
        self.netrain = 0.0  # net rainfall (mm/day)
        self.aet = AET(0.0, 0.0)  # actual water loss by ET (mm/day)

    def net_rainfall(self):
        """
        Net rainfall (mm/day).

        # Returns
            float: net rainfall

        """
        fraction = max(0.7295, 1 - 0.0541 * self.lai)  # net rain (mm) reaching soil depends on lai
        return fraction * self.dayrain

    def rooting_depth(self):
        """
        Increase in rooting depth (m).

        # Returns
            float: rooting depth

        """
        # root growth rate = 2 mm/day but limited by water stress and total soil depth
        newdepth = self.rootdepth + (2.0 / 1000) * self.waterstresses.crop
        depthlimit = self.layers[-1].accthick
        return min(newdepth, depthlimit)

    def update_rootwater(self):
        """
        Update the water content and water characteristics in the rooting zone.

        The `RootZone` object will be set here.

        !!! note
            Critical soil water content for plant water stress taken as 0.6 or 60%
            of the difference between soil saturation and permanent wilting point.

        # Returns
            None:

        """
        wc = wcsat = wcfc = wcpwp = 0.0
        # only consider those soil layers in where the roots reside:
        for layer in self.layers:
            diff = layer.thick - max(0.0, layer.accthick - self.rootdepth)
            if diff <= 0:
                break  # found all the soil layers holding the roots, so exit loop
            wc += layer.vwc * diff
            wcsat += layer.swc.sat * diff
            wcfc += layer.swc.fc * diff
            wcpwp += layer.swc.pwp * diff
        vwc = wc / self.rootdepth  # convert from m water to m3/m3
        vwcsat = wcsat / self.rootdepth
        vwcfc = wcfc / self.rootdepth
        vwcpwp = wcpwp / self.rootdepth
        vwccr = vwcpwp + 0.6 * (vwcsat - vwcpwp)   # critical point
        # update the RootWater object with latest values:
        self.rootwater.wc = wc * 1000    # mm
        self.rootwater.vwc = vwc         # all the rest in m3/m3
        self.rootwater.critical = vwccr
        self.rootwater.sat = vwcsat
        self.rootwater.fc = vwcfc
        self.rootwater.pwp = vwcpwp

    def reduce_et(self):
        """
        Reduction in evaporation and transpiration (0-1, 1=no stress, 0=max. stress).

        # Returns
            AET: `namedtuple` containing reduction in E and T (`float`)

        """
        rde = 1 / (1 + (3.6073 * (self.layers[0].vwc / self.layers[0].swc.sat)) ** -9.3172)
        vwc = self.rootwater.vwc
        vwcpwp = self.rootwater.pwp
        vwccr = self.rootwater.critical
        if vwc >= vwccr:
            rdt = 1.0
        elif vwcpwp < vwc < vwccr:
            rdt = (vwc - vwcpwp) / (vwccr - vwcpwp)
        else:
            rdt = 0.01
        return AET(rdt, rde)

    def actual_et(self, petcrop, petsoil):
        """
        Actual evaporation and transpiration (mm/day).

        # Arguments
            petcrop (float): potential water loss from the crop (mm/day)
            petsoil (float): potential water loss from the soil (mm/day)

        # Returns
            AET: `namedtuple` containing actual water loss from soil and crop (`float`)

        """
        return AET(self.waterstresses.crop * petcrop, self.waterstresses.soil * petsoil)

    def influx_from_watertable(self):
        """
        Influx of water from the water table (m/day).

        # Returns
            float: groundwater influx

        """
        last = self.layers[-1]  # water table assumed just beneath the last soil layer
        k = (last.ksat - last.k) / (math.log(last.ksat) - math.log(last.k))
        hm = (33 - (33 - last.swc.airentry)) / 10.0   # saturated water table
        hg = last.accthick
        tothead = hm + hg
        return k * (tothead - last.tothead) / (last.thick * 0.5)

    def calc_water_fluxes(self, petcrop, petsoil, firstrun):
        """
        Calculate the various water fluxes (m/day) for all soil layers.

        Flux can either have a positive or negative sign

        ```text
            +ve flux - means downward flow
            -ve flux - means upward flow (against gravity)
        ```

        # Arguments
            petcrop (float): potential water loss from the crop (mm/day)
            petsoil (float): potential water loss from the soil (mm/day)
            firstrun (bool): set to `True` for first run, else `False`.
                             `True` means the cumulative fluxes will be initialize with the first
                             set of flux values. `False` will accumulate the flux values.

        # Returns
            None:

        """
        self.update_rootwater()
        self.waterstresses = self.reduce_et()
        self.aet = self.actual_et(petcrop, petsoil)

        # 1. calculates the influx
        prvpsi = 0.0
        for idx in range(self.numlayers):
            cur = self.layers[idx]  # current soil layer
            prv = cur.prevlayer  # previous soil layer (None for first soil layer)

            # set the total (gravity and matric) head (m) and unsaturated k (m/day)
            cur.update_heads_k()  # set the total (gravity and matric) head (m)

            # evaporation (only from first soil layer) and transpiration loss:
            ei = 0.0 if prv is not None else self.aet.soil / 1000     # actual E (m/day)
            cj = min(1.0, cur.accthick / self.rootdepth)
            curpsi = 1.8 * cj - 0.8 * cj ** 2
            ti = self.aet.crop * (curpsi - prvpsi) / 1000      # actual T (m/day)
            prvpsi = curpsi

            # influx into current layer:
            if prv is not None:
                # use Darcy's law for second soil layer onwards
                n = math.log(cur.k) - math.log(prv.k)
                k = (cur.k - prv.k) / n if n != 0.0 else cur.k   # logarithmic mean of k
                curinflux = k * (cur.tothead - prv.tothead) / (cur.depth - prv.depth) - ti
            else:
                # first layer influx is simply the net rainfall after losses from E and T
                netrain = self.netrain / 1000       # net rainfall (convert to m)
                curinflux = min(netrain, cur.ksat) - ei - ti

            # store the intermediary fluxes:
            self.__pf[idx]['t'] = ti
            self.__pf[idx]['e'] = ei
            self.__pf[idx]['influx'] = curinflux

        # 2. calculates the net flux then water content
        for idx in range(self.numlayers):
            cur = self.layers[idx]  # current soil layer
            nxt = cur.nextlayer  # next soil layer (None for last soil layer)

            wc = cur.vwc * cur.thick  # current water content (m)
            influx = self.__pf[idx]['influx']  # water entering current layer
            if nxt is not None:
                outflux = self.__pf[idx + 1]['influx']   # outflux is the next soil layer's influx
            elif not self.has_watertable:
                outflux = cur.k   # water flow driven only by gravity for last layer
            else:
                outflux = self.influx_from_watertable()     # influx due to water table

            # ensure a soil layer cannot be too dry (<0.005 m3/m3) or exceed soil saturation
            nextwc = influx + wc - outflux
            drylmt = cur.thick * 0.005
            satlmt = cur.thick * cur.swc.sat
            if nextwc < drylmt:
                outflux = influx + wc - drylmt
            elif nextwc > satlmt:
                outflux = influx + wc - satlmt

            if nxt is not None:
                self.__pf[idx + 1]['influx'] = outflux

            # determine the net fluxes and water content for current layer:
            self.__pf[idx]['outflux'] = outflux
            self.__pf[idx]['netflux'] = self.__pf[idx]['influx'] - self.__pf[idx]['outflux']

            # update at every sub-interval step:
            wc += self.__pf[idx]['netflux'] / self.numintervals
            # cap water content to prevent extreme, out-of-range values in later calculations
            cur.vwc = max(0.005, min(cur.swc.sat, wc / cur.thick))  # vol. water content (m3/m3)
            cur.wc = cur.vwc * cur.thick * 1000  # water content (mm)

            # sum the water fluxes in every sub-interval step to determine final fluxes
            #    at the end of a daily time step
            for field in SoilLayer.flux_fields:
                if firstrun:
                    # first sub-interval run, so do not accumulate values; initialize them
                    self.cf[idx][field] = self.__pf[idx][field] / self.numintervals
                else:
                    # not the first run, so accumulate values
                    self.cf[idx][field] += self.__pf[idx][field] / self.numintervals

    def daily_water_balance(self, petcrop, petsoil):
        """
        Solve for the water content in each soil layer.

        # Arguments
            petcrop (float): potential water loss from the crop (mm/day)
            petsoil (float): potential water loss from the soil (mm/day)

        # Returns
            None:

        """
        # update the values that will not change within a day
        self.netrain = self.net_rainfall()
        self.rootdepth = self.rooting_depth()

        # solve the water balance:
        for i in range(self.numintervals):
            self.calc_water_fluxes(petcrop, petsoil, i == 0)

        # at the end of every daily time step,
        #    update the various water fluxes for all soil layers
        for i, layer in enumerate(self.layers):
            for field in SoilLayer.flux_fields:
                layer.fluxes[field] = self.cf[i][field]

    def update(self, external_info):
        """
        Update the soil water properties by solving the water fluxes.

        # Arguments
            external_info (dict): requires information on potential transpiration and evaporation

        # Returns
            None:

        """
        self.daily_water_balance(external_info['petcrop'], external_info['petsoil'])
        external_info['cropstress'] = self.waterstresses.crop   # info on water stress for Crop
        Crop.update(self, external_info)
