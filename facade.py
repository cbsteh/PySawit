"""
Facade module.

Front-end of the model.
Coordinate model simulations and handle the model output.

!!! warning "Required installation"
    * [Anaconda](https://www.continuum.io/downloads) for `matplotlib` and `numpy` for chart
      plotting
    * `progressbar2` (run `pip install progresbar2`) for showing model run progress
    * `xlwings` (run `pip install xlwings`) for running Excel macros

# Author - Christopher Teh Boon Sung
------------------------------------

"""

import calendar
import datetime
import json
import math
import os
import platform
import re
import webbrowser
from collections import OrderedDict

import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import numpy as np
import progressbar
import xlwings

import graph
import meteostats
from energybal import EnergyBal
from simweather import SimWeather


class Facade(object):
    """
    Facade class.

    Coordinate model simulations, show the progress of a model run, format and write model
    simulation results to a file, trace a program flow, model debugging, and export model results
    into Excel for further data processing and plotting.

    # ATTRIBUTES
        fname_in (str): file name and path for model input parameters
        fname_out (str): file name and path for model simulation results
        fname_aux (str): file name and path for auxiliary simulation results (for debugging)
        fout (io.TextIOWrapper): file object for daily data results
        faux (io.TextIOWrapper): file object for auxiliary data results
        out (OrderedDict): holds values for daily model simulation results
        auxlist (list): auxiliary list of model parameters to additionally
                        output along wih model output (for debugging)
        progbar (ProgressBar): progressbar object to display progress of model run
        bdailyrun (bool): `True` for daily runs, else `False` for hourly runs
        model (EnergyBal): the model (oil palm model)

    # METHODS
        create_network_graph: Create network graphs to track program flow
        print_elapsed_time: Format and print the elapsed time
        runxlmacro: Export model results to an Excel workbook
        close_files: Close all files
        dump: Dump the values of all or selected model parameters to a file
        trace: Trace a single daily model run to create the network graphs, showing
               the complete program flow through the model components
        set_auxiliaries: Set the auxiliary model parameters to additionally output
        output_auxiliary: Write auxiliary results to auxiliary file (for debugging)
        output_dailyrun: Initialize or retrieve and store daily model output results
        output_hourlyrun: Initialize or retrieve and store hourly model output results
        output_headers: Output the column headers (titles) to file
        output_results: Save the model simulation results, and write results to file and screen
        run_simulation: Run daily or hourly model simulations
        plot_weather: Plot charts on weather properties

    """

    def __init__(self, fname_in, fname_out):
        """
        Create and initialize the Facade object.

        # Arguments
            fname_in (str): path and filename of the model initialization file
            fname_out (str): path and filename of the model simulation reults file

        """
        self.fname_in = fname_in  # file name for model input parameters
        self.fname_out = fname_out  # file name for daily data results
        self.fname_aux = None  # file name for auxiliary data results (for debugging)
        self.fout = None  # file handle for daily data results
        self.faux = None  # file handle for auxiliary data results
        self.out = OrderedDict()  # holds values for daily model output
        self.auxlist = []  # auxiliary list
        self.progbar = None   # progressbar object
        self.bdailyrun = True    # True for daily runs, else False for hourly runs
        self.model = EnergyBal(fname_in)    # the engine: oil palm model object
        # internal use:
        self.__count = 0  # current counter to keep track of output
        self.__str = ['', '']  # column headers/titles for daily model output
        self.__straux = ['', '']  # column headers/titles for auxiliary model output
        self.__nspan = 15  # number of spaces for each column output
        self.__bn = []   # Button widget (matplotlib)

    def __del__(self):
        """
        Class destructor.

        Override to call `close_files()` to ensure all opened files, if any, are closed before
        this object is destroyed.

        # Returns
            None:

        """
        self.close_files()  # close all files before object destruction

    def close_files(self):
        """
        Close all files.

        # Returns
            None:

        """
        if self.fout is not None:
            self.fout.close()
        if self.faux is not None:
            self.faux.close()

    def set_auxiliaries(self, fname_aux, auxlist):
        """
        Set the auxiliaries to output (used for debugging or checking calculation results).

        Set attributes `fname_aux` and `auxlist` to the given auxiliary file name
        and auxiliary model parameters to output, respectively.

        # Arguments
            fname_aux (str): path and filename to store auxiliary results
            auxlist (list): list of variables to output during a model run

        # Example

        For example, we want to save the trunk maintenance and water influx into the 2nd soil
        layer at the end of every run cycle. To access these parameters, we would normally
        call them like the this:

        ```python
        self.model.parts.trunk.maint   # maintenance of the trunk
        self.model.layers[1].fluxes['influx'] # influx of water into second soil layer
        ```

        but for brevity, just use:

        ```python
        parts.trunk.maint
        layers[1].fluxes['influx']
        ```

        where 'self.model.' will be prefixed in this class for each item in the `auxlist`.
        So, our sample code could look like this:

        ```python
        # a list of what we want to output (remember: remove 'self.model.'):
        aux = ['parts.trunk.maint', "layers[1].fluxes['influx']"]

        # debug.txt is the file name to store the auxiliary results:
        fac.set_auxiliaries('debug.txt', aux)  # fac is a Facade object

        # the usual model output plus the auxiliary results
        fac.run_simulation(True, 365)
        ```

        # Returns
            None:

        """
        self.fname_aux = fname_aux
        # add the prefix 'self.model.' to every item in the auxiliary list.
        #    besides for coding brevity and convenience, prefix with 'self.model.' is a safety
        #    feature to ensure only calls to self.model model components are allowed, without
        #    access to any OS commands, for instance.
        self.auxlist = ['self.model.' + cmd for cmd in auxlist]

    def _json(self, incl, excl, obj=None):
        """
        Produce a JSON-formatted string for an object.

        # Arguments
            incl (list): inclusion list of model classes, parameters, etc.
            excl (list): exclusion list
            obj: model object

        # Returns
            str: JSON-formatted string

        """
        # check if a key is found in the list of patterns to either include or exclude in dump
        def _hasmatch(key, registry):
            bfound = False
            gen = (re.search(pattern, key) for pattern in registry)
            # check every pattern until found, then exit (or until patterns exhausted)
            while not bfound:
                try:
                    bfound = gen.__next__() is not None
                except StopIteration:   # reached end of patterns, so exit (result: not found)
                    break
            return bfound

        # recursively, check if to dump every model parameter
        # noinspection PyProtectedMember
        def _drilldown(o, path):
            if (isinstance(o, tuple) and hasattr(o, "_fields") and
                hasattr(o, "_asdict") and callable(o._asdict)):    # namedtuple
                dt = dict()
                for key in o._asdict():
                    dt[key] = _drilldown(o._asdict()[key], path + "/" + key)
                return dt
            elif isinstance(o, tuple) or isinstance(o, list) or isinstance(o, set):
                l = list()
                i = 0
                for item in o:
                    l.append(_drilldown(item, path + "/[" + str(i) + "]"))
                    i += 1
                return l
            elif isinstance(o, datetime.datetime):  # datetime
                if o.utcoffset() is not None:
                    o -= o.utcoffset()
                millis = int(calendar.timegm(o.timetuple()) * 1000 + float(o.microsecond) / 1000)
                return millis
            elif isinstance(o, dict):  # dict
                rd = dict()
                for key in o:
                    rd[key] = _drilldown(o[key], path + "/" + str(key))
                return rd
            elif (isinstance(o, str) or isinstance(o, int) or
                  isinstance(o, float) or isinstance(o, complex) or
                  isinstance(o, bool) or type(o).__name__ == "NoneType"):
                return o
            else:
                dt = dict()
                for key in o.__dict__:
                    # check if current parameter should be dumped
                    binclude = _hasmatch(key, incl)      # True means dump
                    bexclude = excl is not None and _hasmatch(key, excl)     # True means no dump
                    if binclude and not bexclude:
                        # exclusion from dump overrides inclusion to dump
                        dt[key] = _drilldown(o.__dict__[key], path + "/" + key)
                return dt

        obj = obj or self.model
        return json.dumps(_drilldown(obj, "/"), sort_keys=True, indent=4)

    def dump(self, fname, include=tuple(r'.*'), exclude=None):
        """
        Dump the values of all or selected model parameters.

        The user can specify which model parameters to include and exclude in the dump.

        !!! note
            `SoilLayer` objects have links to other `SoilLayer` objects, so these
            links create an infinite recursion during program flow tracing,
            so `SoilLayer.prevlayer` and `SoilLayer.nextlayer` attributes must be excluded.
            This method automatically appends these two parameters in the `exclude` argument.

        # Arguments
            fname (str): path and name of file to store the model dump
            include (list): list of model parameters to include in the dump
                            (default is to include all)
            exclude (list): list of model parameters to exclude in the dump
                            (default is to exclude none -- but see Note above)

        # Example
        A list of model parameters to include (uses regular expression)

        ```python
        incl = [r'.*Meteo',
                r'.*Crop']
        ```

        and a list of model parameters to exclude (uses regular expression)

        ```python
        excl = [r'_Meteo__g$',
                r'_Crop__assim4gen',
                r'.*wind',
                r'.box*',
                r'.*ini']
        ```
        If `incl` argument is omitted, all will be included by default (unless excluded by
        `excl`). If `excl` argument is omitted, none will be excluded (unless `incl` specfies
        what to include). If `incl` contradicts `excl`, `excl` wins (i.e., a parameter will
        be excluded even though `incl` specified that this parameter should be included).

        # Returns
            None:

        """
        print('Dumping current values of model parameters to file...')
        with open(fname, mode='wt') as fout:
            # SoilLayer objects have links to other SoilLayer objects, so these
            #    links create an infinite recursion, so exclude these two fields
            addexcl = [r'prevlayer', r'nextlayer']
            if exclude:
                exclude += addexcl
            else:
                exclude = addexcl
            fout.write(self._json(incl=include, excl=exclude))
        print('done.')

    @staticmethod
    def create_network_graph(fname, fn, *args):
        """
        !!! note
            `create_network_graph` is a static method

        Trace the program flow to aid in understanding the structure of the whole model.

        Two graph files will be created: a DOT (.dot) file and a GML (.gml) file type.

        # Arguments
            fname (str): file name (without extension) for DOT and GML graph files to create
            fn: the function which serves as the entry point to trace the program flow
            args: variable lengh arguments, if any, for the entry point function `fn()`

        # Returns
            None:

        """
        # specify the function which is the entry point to trace the program flow
        def _entry_point(f, *f_args):  # name of function and its arguments, if any
            def wrapper():
                f(*f_args)  # entry point of the program flow
            return wrapper

        # classes to ignore in the program flow
        # bug in pycallgraph? '__main__' cannot be ignored (need to remove later; see below)
        exclude = [
            'pycallgraph.*',
            '*.<*',
            '__new__',
            'KeysView.*',
            'ValuesView.*'
            'OrderedDict.*',
            'AFGen.*',
            'facade.*',
        ]
        # node colors (in hexadecimal and 8 characters long) for classes
        clsdict = {
            'meteo': '00FFFFFF',      # aqua
            'crop': '00FF00FF',       # lime
            'soilwater': 'F4A460FF',  # sandy brown
            'photosyn': 'FF00FFFF',   # magenta
            'energybal': 'FF6347FF'   # tomato red
        }
        # delete unwanted strings (such as clusters and nodes) in the network files
        # must use regular expression and compile it as a search expression
        delstrings = [
            re.compile(r'EnergyBal.'),  # "EnergyBal." appears in all labels, so delete it
            re.compile(r'subgraph "cluster___main__".*}'),  # rid the orphan __main__
            re.compile(r'"__main__.*;')
        ]

        # start tracing and two network graph files will be created after this call
        func = _entry_point(fn, *args)
        graph.Graph().trace(
            fn=func,
            fname=fname,
            exclude_from_trace=exclude,
            strings_to_delete=delstrings,
            class_colors=clsdict
        )

    def trace(self, fname):
        """
        Create a network map to trace the program flow.

        Program flows begins from `Facade.run_simulation()` method. A single daily run, just
        to capture the one cycle of the program flow through the model components/classes/methods.

        # Arguments
            fname (str): files for DOT and GML map (do not specify the file extension)

        # Returns
            None:

        """
        print('Creating network graph DOT and GML files...')
        self.create_network_graph(fname, self.run_simulation, True)
        print('done.')

    @staticmethod
    def print_elapsed_time(totsecs):
        """
        !!! note
            `print_elapsed_time` is a static method

        Format and print the elapsed time from total secs to hrs, mins, and secs.

        # Arguments
            totsecs (int): total number of seconds elapsed

        # Returns
            None:

        """
        hr, sc = divmod(totsecs, 3600)
        mn, sc = divmod(sc, 60)
        txt = ''
        if hr > 0:
            txt += '{:d} hr '.format(int(hr))
        if mn > 0 or hr > 0:
            txt += '{:d} min '.format(int(mn))
        txt += '{:.1f} s'.format(sc)
        print('\nCompleted in {}'.format(txt))

    def output_auxiliary(self):
        """
        Write auxiliary results to the auxiliary file (for debugging).

        # Returns
            None:

        """
        if self.auxlist:
            # safe use of the eval function because of the earlier forced 'self.model.' prefix
            scope = locals()    # ensure eval used only in locals scope
            output = [eval(cmd, scope) for cmd in self.auxlist]
            if self.__count == 1:
                # first time output: write the headings to file and prepare the format for output:
                # column space to fit the longest variable/title
                auxlist = [aux.replace('self.model.', '') for aux in self.auxlist]
                nspan = len(max(auxlist, key=len)) + 1
                self.__straux = ['', '']
                for i, out in enumerate(output):
                    if i > 0:
                        self.__straux[0] += ','
                        self.__straux[1] += ','
                    if isinstance(out, float):
                        self.__straux[0] += '{:>' + str(nspan) + '.3f}'  # 3 decimal places
                    else:
                        self.__straux[0] += '{:>' + str(nspan) + '}'
                    self.__straux[1] += '{:>' + str(nspan) + '}'
                # write the column headings
                self.faux.write(self.__straux[1].format(*auxlist) + '\n')
            self.faux.write(self.__straux[0].format(*output) + '\n')  # write the results

    def output_dailyrun(self, initialize=False):
        """
        Prepare the list of daily model output, then retrieve and store their results.

        # Arguments
            initialize (bool): `True` to initialize the output dictionry, else
                               `False` to retrieve and store model output results in dictionary

        # Returns
            None:

        """
        out = self.out
        ops = self.model
        if not initialize:
            # 1. get results for daily properties:
            ag_growth = ops.parts.pinnae.growth + ops.parts.rachis.growth + ops.parts.trunk.growth
            veg_growth = ag_growth + ops.parts.roots.growth
            out['age'] = ops.treeage
            out['tmin'] = ops.daytmin
            out['tmax'] = ops.daytmax
            out['totalrad'], out['directrad'], out['diffuserad'] = ops.dayrad
            out['wind'] = ops.daywind
            out['rain'] = ops.dayrain
            out['netrain'] = ops.netrain
            out['ambientCO2'] = ops.co2ambient
            out['LAI'] = ops.lai
            out['pinnae'] = ops.parts.pinnae.weight
            out['rachis'] = ops.parts.rachis.weight
            out['trunk'] = ops.parts.trunk.weight
            out['roots'] = ops.parts.roots.weight
            out['male'] = ops.parts.maleflo.weight
            out['female'] = ops.parts.femaflo.weight
            out['bunches'] = ops.parts.bunches.weight
            out['flowersex'] = ops.flowersex
            out['VDM'] = ops.vdmwgt
            out['TDM'] = ops.tdmwgt
            out['assim_photosyn'] = ops.dayassim
            out['assim_maint'] = ops.assim4maint
            out['assim_growth'] = ops.assim4growth
            out['assim_gen'] = ops.assim4gen
            out['VDM_growth'] = ag_growth
            out['TDM_growth'] = veg_growth
            out['yield'] = ops.bunchyield
            out['trunk_hgt'] = ops.trunkhgt
            out['rootdepth'] = ops.rootdepth
            out['rootzone_VWC'] = ops.rootwater.vwc
            out['waterstress'] = ops.waterstresses.crop
            out['actual_E'] = ops.aet.soil
            out['actual_T'] = ops.aet.crop
            out['pot_T'] = ops.dayet.crop
            # add soil layers output to the list
            for n in range(ops.numlayers):
                out['layer' + str(n + 1) + '_VWC'] = ops.layers[n].vwc
                out['layer' + str(n + 1) + '_influx'] = ops.layers[n].fluxes['influx'] * 1000
                out['layer' + str(n + 1) + '_outflux'] = ops.layers[n].fluxes['outflux'] * 1000
                out['layer' + str(n + 1) + '_netflux'] = ops.layers[n].fluxes['netflux'] * 1000
                out['layer' + str(n + 1) + '_e'] = ops.layers[n].fluxes['e'] * 1000
                out['layer' + str(n + 1) + '_t'] = ops.layers[n].fluxes['t'] * 1000
        else:
            # model parameters to output daily:
            out['age'] = 0
            out['tmin'] = 0.0
            out['tmax'] = 0.0
            out['totalrad'] = 0.0
            out['directrad'] = 0.0
            out['diffuserad'] = 0.0
            out['wind'] = 0.0
            out['rain'] = 0.0
            out['netrain'] = 0.0
            out['ambientCO2'] = 0.0
            out['LAI'] = 0.0
            out['pinnae'] = 0.0
            out['rachis'] = 0.0
            out['trunk'] = 0.0
            out['roots'] = 0.0
            out['male'] = 0.0
            out['female'] = 0.0
            out['bunches'] = 0.0
            out['flowersex'] = 0.0
            out['VDM'] = 0.0
            out['TDM'] = 0.0
            out['assim_photosyn'] = 0.0
            out['assim_maint'] = 0.0
            out['assim_growth'] = 0.0
            out['assim_gen'] = 0.0
            out['VDM_growth'] = 0.0
            out['TDM_growth'] = 0.0
            out['yield'] = 0.0
            out['trunk_hgt'] = 0.0
            out['rootdepth'] = 0.0
            out['rootzone_VWC'] = 0.0
            out['waterstress'] = 0.0
            out['actual_E'] = 0.0
            out['actual_T'] = 0.0
            out['pot_T'] = 0.0
            # add soil layers to the model output list (daily):
            for n in range(ops.numlayers):
                out['layer' + str(n + 1) + '_VWC'] = 0.0
                out['layer' + str(n + 1) + '_influx'] = 0.0
                out['layer' + str(n + 1) + '_outflux'] = 0.0
                out['layer' + str(n + 1) + '_netflux'] = 0.0
                out['layer' + str(n + 1) + '_e'] = 0.0
                out['layer' + str(n + 1) + '_t'] = 0.0

    def output_hourlyrun(self, initialize=False):
        """
        Prepare the list of hourly model output, then retrieve and store their results.

        # Returns
            None:

        """
        out = self.out
        ops = self.model
        if not initialize:
            # 1. get results for daily properties:
            out['hour'] = ops.solarhour
            out['doy'] = ops.doy
            out['solarinc'] = math.degrees(ops.solarpos.inc)
            out['rad_et'] = ops.etrad
            out['rad_total'] = ops.rad.total
            out['rad_dr'] = ops.rad.direct
            out['rad_df'] = ops.rad.diffuse
            out['airtemp'] = ops.airtemp
            out['canopytemp'] = ops.canopytemp
            out['svp'] = ops.svp
            out['vp'] = ops.vp
            out['vpd'] = ops.vpd
            out['rh'] = ops.rh
            out['u'] = ops.windspd
            out['co2internal'] = ops.co2internal
            out['kdr'] = ops.extcoef.kdr
            out['kdf'] = ops.extcoef.kdf
            out['lai_sunlit'] = ops.laicomp.sunlit
            out['lai_shaded'] = ops.laicomp.shaded
            out['par_outdr'] = ops.par.outdr
            out['par_outdf'] = ops.par.outdf
            out['par_indrscatter'] = ops.par.indrscatter
            out['par_inscatter'] = ops.par.inscatter
            out['par_indf'] = ops.par.indf
            out['par_abs_sunlit'] = ops.par.abssunlit
            out['par_abs_shaded'] = ops.par.absshaded
            out['mm_co2'] = ops.assimcoef.mmco2
            out['mm_o2'] = ops.assimcoef.mmo2
            out['specificity'] = ops.assimcoef.specificity
            out['vcmax'] = ops.assimcoef.vcmax
            out['co2pt'] = ops.assimcoef.co2pt
            out['assim_vc'] = ops.leafassim.vc
            out['assim_vqsl'] = ops.leafassim.vqsl
            out['assim_vqsh'] = ops.leafassim.vqsh
            out['assim_vs'] = ops.leafassim.vs
            out['assim_sunlit'] = ops.leafassim.sunlit
            out['assim_shaded'] = ops.leafassim.shaded
            out['d'] = ops.d
            out['z0'] = ops.z0
            out['windext'] = ops.windext
            out['fn_water'] = ops.stressfn.water
            out['fn_vpd'] = ops.stressfn.vpd
            out['fn_par'] = ops.stressfn.par
            out['a'] = ops.availegy.total
            out['ac'] = ops.availegy.crop
            out['as'] = ops.availegy.soil
            out['rn'] = ops.availegy.net
            out['g'] = ops.availegy.g
            out['u*'] = ops.ustar
            out['uh'] = ops.ucrophgt
            out['rsa'] = ops.res.rsa
            out['raa'] = ops.res.raa
            out['rca'] = ops.res.rca
            out['rst'] = ops.res.rst
            out['rcs'] = ops.res.rcs
            out['rss'] = ops.res.rss
            out['et_total'] = ops.et.total
            out['et_crop'] = ops.et.crop
            out['et_soil'] = ops.et.soil
            out['h_total'] = ops.h.total
            out['h_crop'] = ops.h.crop
            out['h_soil'] = ops.h.soil
        else:
            # model parameters to output hourly:
            out['hour'] = 0.0
            out['doy'] = 0
            out['solarinc'] = 0.0
            out['rad_et'] = 0.0
            out['rad_total'] = 0.0
            out['rad_dr'] = 0.0
            out['rad_df'] = 0.0
            out['airtemp'] = 0.0
            out['canopytemp'] = 0.0
            out['svp'] = 0.0
            out['vp'] = 0.0
            out['vpd'] = 0.0
            out['rh'] = 0.0
            out['u'] = 0.0
            out['co2internal'] = 0.0
            out['kdr'] = 0.0
            out['kdf'] = 0.0
            out['lai_sunlit'] = 0.0
            out['lai_shaded'] = 0.0
            out['par_outdr'] = 0.0
            out['par_outdf'] = 0.0
            out['par_indrscatter'] = 0.0
            out['par_inscatter'] = 0.0
            out['par_indf'] = 0.0
            out['par_abs_sunlit'] = 0.0
            out['par_abs_shaded'] = 0.0
            out['mm_co2'] = 0.0
            out['mm_o2'] = 0.0
            out['specificity'] = 0.0
            out['vcmax'] = 0.0
            out['co2pt'] = 0.0
            out['assim_vc'] = 0.0
            out['assim_vqsl'] = 0.0
            out['assim_vqsh'] = 0.0
            out['assim_vs'] = 0.0
            out['assim_sunlit'] = 0.0
            out['assim_shaded'] = 0.0
            out['d'] = 0.0
            out['z0'] = 0.0
            out['windext'] = 0.0
            out['fn_water'] = 0.0
            out['fn_vpd'] = 0.0
            out['fn_par'] = 0.0
            out['a'] = 0.0
            out['ac'] = 0.0
            out['as'] = 0.0
            out['rn'] = 0.0
            out['g'] = 0.0
            out['u*'] = 0.0
            out['uh'] = 0.0
            out['rsa'] = 0.0
            out['raa'] = 0.0
            out['rca'] = 0.0
            out['rst'] = 0.0
            out['rcs'] = 0.0
            out['rss'] = 0.0
            out['et_total'] = 0.0
            out['et_crop'] = 0.0
            out['et_soil'] = 0.0
            out['h_total'] = 0.0
            out['h_crop'] = 0.0
            out['h_soil'] = 0.0

    def _init_output(self):
        """
        Initialize the output dictionaries and format the output.

        # Returns
            None:

        """
        # dictionary keys are the parameters names and used as headers
        # model parameters will appear in the output file in the order they are defined here
        self.__count = 0  # reset counter
        self.close_files()  # close all previous files if they are opened
        self.fout = open(self.fname_out, 'wt')  # file handle for daily model output
        if self.fname_aux is not None:
            self.faux = open(self.fname_aux, 'wt')  # file handle for auxiliary model output
        # prepare the output list:
        if self.bdailyrun:
            self.output_dailyrun(True)
        else:
            self.output_hourlyrun(True)
        # now format the output:
        nspan = self.__nspan
        n = 0
        self.__str = ['', '']
        for v in self.out.values():
            if n > 0:
                self.__str[0] += ','
                self.__str[1] += ','
            if isinstance(v, float):
                self.__str[0] += '{:>' + str(nspan) + '.3f}'  # 3 decimal places
            else:
                self.__str[0] += '{:>' + str(nspan) + '}'
            self.__str[1] += '{:>' + str(nspan) + '}'
            n += 1

    def output_headers(self):
        """
        Output the column headers (titles) to file.

        # Returns
            None:

        """
        # prepare what to output:
        self._init_output()
        # print comments in the files
        today = datetime.datetime.today()
        comment1 = '# {:%d-%b-%Y %I:%M %p}\n'.format(today)
        comment2 = '# seed {}\n'.format(self.model.seed)
        self.fout.write(comment1)
        self.fout.write(comment2)
        comment3 = self.__str[1].format(*list(i + 1 for i in range(self.__str[1].count('{'))))
        comment3 = comment3.replace(' ', '#', 2).replace(',', ' ')
        self.fout.write(comment3 + '\n')
        # print column headers/titles
        o = self.__str[1].format(*self.out.keys())
        self.fout.write(o + '\n')

    def output_results(self):
        """
        Save the model simulation results, and write results to file and screen.

        # Returns
            None:

        """
        self.__count += 1  # new line of output
        # 1. retrieve and store the values from model variables
        if self.bdailyrun:
            self.output_dailyrun(False)
        else:
            self.output_hourlyrun(False)
        # 2. output daily results:
        output = self.__str[0].format(*self.out.values())
        self.fout.write(output + '\n')
        # 3. output any auxiliaries:
        self.output_auxiliary()
        # 4. show progress of run
        if self.bdailyrun:
            self.progbar.update(self.__count)

    def run_simulation(self, bdailyrun, duration=None, auxfile=None, auxlist=None):
        """
        Model simulation runs.

        Run the model for a selected number of days or hours. Allow for auxiliary model paramters
        to be outputted and stored in a file. Auxiliaries are for debugging purposes to monitor
        the values of certain model parameters.

        # Arguments
            bdailyrun (bool): `True` for daily simulation runs, else `False` for hourly simulation
                              runs
            duration (int): no. of simulation days to run (default is 1 day)
            auxfile (str): auxiliary file name and path to store the output of selected model
                           parameters
            auxlist (list): list of model parameters to additionally output

        !!! note
            For hourly runs, the `duration` argument is always set for 24 simulation hours,
            regardless of the supplied argument value.

        # Example
        Example of an auxiliary list:

        ```python
        aux = ['doy',
               'sla',
               'lookup_sla_lai()[1]',
               'parts.trunk.maint',
               'layers[1].fluxes["influx"]']
        ```

        will output the following model parameters

        ```text
            doy (day of year)
            sla (specific leaf area),
            lai (leaf area index),
            trunk maintenance, and
            water influx into the first soil layer
        ```

        # Returns
            None:

        """
        # auxiliary model output will be carried out after model output
        if auxfile and auxlist:
            self.set_auxiliaries(auxfile, auxlist)

        self.bdailyrun = bdailyrun
        self.output_headers()  # writes column headers and comments to output files
        if bdailyrun:
            nxt = self.model.next_day  # daily run generator
            if duration is None:
                duration = 1  # default: run only 1 day
        else:
            nxt = self.model.next_hour  # hourly run generator
            if duration is None:
                duration = 24  # default: run every hour for 24 hours

        print('Running...', flush=True)
        if bdailyrun:
            self.progbar = progressbar.ProgressBar(max_value=duration)  # progress bar

        # now start the model run (nxt is a day or hour generator)
        for _ in nxt(duration):
            # write the model results to the output files after every end of a cycle
            self.output_results()

        # model run ended, so close all files and print end run
        self.close_files()
        if bdailyrun:
            Facade.print_elapsed_time(self.progbar.data()['total_seconds_elapsed'])
        else:
            print('done.')

    @staticmethod
    def runxlmacro(xl_fname, xl_macroname, *args):
        """
        !!! note
            `runxlmacro` is a static method

        Run Excel macro stored in an Excel workbook (needs `xlwings` to be installed).
        Can be used, for instance, to export model results into Excel for charting or
        data analysis.

        # Arguments
            xl_fname (str): name of Excel workbook to receive the model output (and has the macro)
            xl_macroname (str): the name of the Excel macro in xl_fname
            args: variable length arguments, if any, to pass into `xl_macroname` macro function

        # Returns
            None:

        """
        # open line of communication with Excel using xlwings
        if platform.system() == 'Windows':  # works only in Windows
            msg = 'Exporting results to Excel workbook "{0}" ... '.format(xl_fname)
            print(msg, flush=True, end='')
            wb = xlwings.Book(xl_fname)  # open and connect to the Excel file
            macro = wb.macro(xl_macroname)
            if len(args) > 0:
                macro(*args)  # calls the Excel macro and pass the arguments
            else:
                macro()     # macro has no arguments (cannot pass a None or empty list to Excel)
            wb.save()
            print('done.')
        else:
            raise OSError('Export to Excel works only in Windows.')

    def plot_weather(self, fig_no, annwthr, fname):
        """
        Plot charts showing the distribution and statistics of several weather properties.

        # Arguments
            fig_no (int): figure number, used to create multiple windows
            annwthr (dict): dictionary holding the annual daily weather data
            fname (str): weather stats file name and path

        # Returns
            None:

        """
        def binlist():
            """Return a series of equally-spaced x-axis values for histogram plotting."""
            # use the Freedman–Diaconis rule to determine bin size:
            iqr = np.percentile(data, 75) - np.percentile(data, 25)     # interquartile range
            binsize = 2 * iqr / len(data) ** (1 / 3)    # bin size/width
            mn = min(data)
            mx = max(data)
            numbins = int(math.ceil((mx - mn) / binsize))   # no. of bins
            return np.linspace(math.floor(mn), math.ceil(mx), numbins)  # equally-spaced x-values

        def openstatsfile(event):
            """Open the weather stats file using the OS's default program."""
            del event
            editor = os.getenv('EDITOR')
            if editor:
                os.system(editor + ' ' + fname)
            else:
                webbrowser.open(fname)

        plt.figure(fig_no)  # new chart window
        x = [doy + 1 for doy in range(365)]     # series of x values
        xvals = (1,) + SimWeather.cumulative_days   # labels for the x-axis
        # min. and max. air temperature:
        y1 = annwthr['tmin']
        y2 = annwthr['tmax']
        plt.subplot(3, 2, 1)
        plt.plot(x, y1, color='blue', label='min.')
        plt.plot(x, y2, color='red', label='max.')
        plt.xlim(1, 365)
        plt.xticks(xvals)
        plt.xlabel('DOY')
        plt.ylabel(r'air temperature ($^\circ$C)')
        plt.text(x[-1], y1[-1], ' min.')
        plt.text(x[-1], y2[-1], ' max.')
        # solar radiation and its components:
        y1 = annwthr['totrad']
        y2 = annwthr['drrad']
        y3 = annwthr['dfrad']
        plt.subplot(3, 2, 2)
        plt.plot(x, y1, color='blue', label='total')
        plt.plot(x, y2, color='red', label='direct')
        plt.plot(x, y3, color='black', label='diffuse')
        plt.xlim(1, 365)
        plt.xticks(xvals)
        plt.xlabel('DOY')
        plt.ylabel('solar irradiance (MJ m$^{-2}$)')
        plt.text(x[-1], y1[-1], ' total')
        plt.text(x[-1], y2[-1], ' direct')
        plt.text(x[-1], y3[-1], ' diffuse')
        # wind speed:
        y = annwthr['wind']
        plt.subplot(3, 2, 3)
        plt.plot(x, y, color='blue', label='wind')
        plt.xlim(1, 365)
        plt.xticks(xvals)
        plt.xlabel('DOY')
        plt.ylabel(r'wind speed (m s$^{-1}$)')
        # rainfall:
        y = annwthr['rain']
        plt.subplot(3, 2, 4)
        plt.plot(x, y, color='blue', label='rain')
        plt.xlim(1, 365)
        plt.xticks(xvals)
        plt.xlabel('DOY')
        plt.ylabel('rain (mm)')
        # histogram for wind speed distribution:
        data = annwthr['wind']
        plt.subplot(3, 2, 5)
        plt.hist(data, bins=binlist(), color='blue', label='wind')
        plt.xlabel('wind speed (m/s)')
        plt.ylabel('no. of days')
        # histogram for rainfall distribution:
        data = [r for r in annwthr['rain'] if r > 0]   # rainfall distribution without zero amounts
        plt.subplot(3, 2, 6)
        plt.hist(data, bins=binlist(), color='blue', label='rain')
        plt.xlabel('rain (mm)')
        plt.ylabel('no. of days')
        # place a button to open weather stats file:
        axbutton = plt.axes([0, 0, 0.1, 0.05])
        axbutton.spines['left'].set_visible(False)      # borderless button
        axbutton.spines['right'].set_visible(False)
        axbutton.spines['top'].set_visible(False)
        axbutton.spines['bottom'].set_visible(False)
        self.__bn.append(Button(axbutton, 'View Data', color=plt.rcParams['figure.facecolor']))
        self.__bn[-1].on_clicked(openstatsfile)
        # change window title to show just the year number and file name
        plt.gcf().canvas.set_window_title('Year {0} - {1}'.format(fig_no, fname))

    def output_weather_stats(self, fname, append_to_file=False):
        """
        Write to file the daily weather parameters for the whole year and their statistics.

        Daily weather parameters to be written to an output file are min. and max. air
        temperatures, wind speed, rain, and solar irradiance. Some basic statistics will
        be computed and written together to the file as well.

        Charts will be drawn as visual output.

        # Arguments
            fname (str): output file (plain text file)
            append_to_file (bool): `False` (default) to create a new output file, else
                                   `True` to append output to an exisiting file

        # Returns
            None:

        """
        ms = meteostats.MeteoStats(self.model)
        # compute and write the weather data and statistics to file
        print('Writing annual weather data and their statistics to file...')
        ms.output_stats(fname, append_to_file)
        print('done.')
        # now prepare the plots
        self.__bn = []
        # disable warning of having too many opened charts
        plt.rcParams.update({'figure.max_open_warning': 0})
        for i in range(len(ms.metdata)):
            self.plot_weather(i + 1, ms.metdata[i], fname)
        # all set, now show all charts
        plt.show()
