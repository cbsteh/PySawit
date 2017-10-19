<h1 id="facade">facade <em>module</em></h1>


Facade module.

Front-end of the model.
Coordinate model simulations and handle the model output.

!!! warning "Required installation"
    * [Anaconda](https://www.continuum.io/downloads) for `matplotlib` and `numpy` for chart
      plotting
    * `progressbar2` (run `pip install progresbar2`) for showing model run progress
    * `xlwings` (run `pip install xlwings`) for running Excel macros

__Author - Christopher Teh Boon Sung__

------------------------------------


<h2 id="facade.Facade">Facade <em>class</em></h2>


Facade class.

Coordinate model simulations, show the progress of a model run, format and write model
simulation results to a file, trace a program flow, model debugging, and export model results
into Excel for further data processing and plotting.

__ATTRIBUTES__

- `fname_in (str)`: file name and path for model input parameters
- `fname_out (str)`: file name and path for model simulation results
- `fname_aux (str)`: file name and path for auxiliary simulation results (for debugging)
- `fout (io.TextIOWrapper)`: file object for daily data results
- `faux (io.TextIOWrapper)`: file object for auxiliary data results
- `out (OrderedDict)`: holds values for daily model simulation results
- `auxlist (list)`: auxiliary list of model parameters to additionally
                    output along wih model output (for debugging)
- `progbar (ProgressBar)`: progressbar object to display progress of model run
- `bdailyrun (bool)`: `True` for daily runs, else `False` for hourly runs
- `model (EnergyBal)`: the model (oil palm model)

__METHODS__

- `create_network_graph`: Create network graphs to track program flow
- `print_elapsed_time`: Format and print the elapsed time
- `runxlmacro`: Export model results to an Excel workbook
- `close_files`: Close all files
- `dump`: Dump the values of all or selected model parameters to a file
- `trace`: Trace a single daily model run to create the network graphs, showing
           the complete program flow through the model components
- `set_auxiliaries`: Set the auxiliary model parameters to additionally output
- `output_auxiliary`: Write auxiliary results to auxiliary file (for debugging)
- `output_dailyrun`: Initialize or retrieve and store daily model output results
- `output_hourlyrun`: Initialize or retrieve and store hourly model output results
- `output_headers`: Output the column headers (titles) to file
- `output_results`: Save the model simulation results, and write results to file and screen
- `run_simulation`: Run daily or hourly model simulations
- `plot_weather`: Plot charts on weather properties


<h3 id="facade.Facade.__init__"><em>Constructor</em> __init__</h3>

```python
Facade(self, fname_in, fname_out)
```

Create and initialize the Facade object.

__Arguments__

- __fname_in (str)__: path and filename of the model initialization file
- __fname_out (str)__: path and filename of the model simulation reults file


<h3 id="facade.Facade.__del__">__del__</h3>

```python
Facade.__del__(self)
```

Class destructor.

Override to call `close_files()` to ensure all opened files, if any, are closed before
this object is destroyed.

__Returns__

`None`:


<h3 id="facade.Facade.close_files">close_files</h3>

```python
Facade.close_files(self)
```

Close all files.

__Returns__

`None`:


<h3 id="facade.Facade.set_auxiliaries">set_auxiliaries</h3>

```python
Facade.set_auxiliaries(self, fname_aux, auxlist)
```

Set the auxiliaries to output (used for debugging or checking calculation results).

Set attributes `fname_aux` and `auxlist` to the given auxiliary file name
and auxiliary model parameters to output, respectively.

__Arguments__

- __fname_aux (str)__: path and filename to store auxiliary results
- __auxlist (list)__: list of variables to output during a model run

__Example__


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

__Returns__

`None`:


<h3 id="facade.Facade.dump">dump</h3>

```python
Facade.dump(self, fname, include=('.', '*'), exclude=None)
```

Dump the values of all or selected model parameters.

The user can specify which model parameters to include and exclude in the dump.

!!! note
    `SoilLayer` objects have links to other `SoilLayer` objects, so these
    links create an infinite recursion during program flow tracing,
    so `SoilLayer.prevlayer` and `SoilLayer.nextlayer` attributes must be excluded.
    This method automatically appends these two parameters in the `exclude` argument.

__Arguments__

- __fname (str)__: path and name of file to store the model dump
- __include (list)__: list of model parameters to include in the dump
                    (default is to include all)
- __exclude (list)__: list of model parameters to exclude in the dump
                    (default is to exclude none -- but see Note above)

__Example__

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

__Returns__

`None`:


<h3 id="facade.Facade.create_network_graph">create_network_graph</h3>

```python
Facade.create_network_graph(fname, fn, *args)
```

!!! note
    `create_network_graph` is a static method

Trace the program flow to aid in understanding the structure of the whole model.

Two graph files will be created: a DOT (.dot) file and a GML (.gml) file type.

__Arguments__

- __fname (str)__: file name (without extension) for DOT and GML graph files to create
- __fn__: the function which serves as the entry point to trace the program flow
- __args__: variable lengh arguments, if any, for the entry point function `fn()`

__Returns__

`None`:


<h3 id="facade.Facade.trace">trace</h3>

```python
Facade.trace(self, fname)
```

Create a network map to trace the program flow.

Program flows begins from `Facade.run_simulation()` method. A single daily run, just
to capture the one cycle of the program flow through the model components/classes/methods.

__Arguments__

- __fname (str)__: files for DOT and GML map (do not specify the file extension)

__Returns__

`None`:


<h3 id="facade.Facade.print_elapsed_time">print_elapsed_time</h3>

```python
Facade.print_elapsed_time(totsecs)
```

!!! note
    `print_elapsed_time` is a static method

Format and print the elapsed time from total secs to hrs, mins, and secs.

__Arguments__

- __totsecs (int)__: total number of seconds elapsed

__Returns__

`None`:


<h3 id="facade.Facade.output_auxiliary">output_auxiliary</h3>

```python
Facade.output_auxiliary(self)
```

Write auxiliary results to the auxiliary file (for debugging).

__Returns__

`None`:


<h3 id="facade.Facade.output_dailyrun">output_dailyrun</h3>

```python
Facade.output_dailyrun(self, initialize=False)
```

Prepare the list of daily model output, then retrieve and store their results.

__Arguments__

- __initialize (bool)__: `True` to initialize the output dictionry, else
                       `False` to retrieve and store model output results in dictionary

__Returns__

`None`:


<h3 id="facade.Facade.output_hourlyrun">output_hourlyrun</h3>

```python
Facade.output_hourlyrun(self, initialize=False)
```

Prepare the list of hourly model output, then retrieve and store their results.

__Returns__

`None`:


<h3 id="facade.Facade.output_headers">output_headers</h3>

```python
Facade.output_headers(self)
```

Output the column headers (titles) to file.

__Returns__

`None`:


<h3 id="facade.Facade.output_results">output_results</h3>

```python
Facade.output_results(self)
```

Save the model simulation results, and write results to file and screen.

__Returns__

`None`:


<h3 id="facade.Facade.run_simulation">run_simulation</h3>

```python
Facade.run_simulation(self, bdailyrun, duration=None, auxfile=None, auxlist=None)
```

Model simulation runs.

Run the model for a selected number of days or hours. Allow for auxiliary model paramters
to be outputted and stored in a file. Auxiliaries are for debugging purposes to monitor
the values of certain model parameters.

__Arguments__

- __bdailyrun (bool)__: `True` for daily simulation runs, else `False` for hourly simulation
                      runs
- __duration (int)__: no. of simulation days to run (default is 1 day)
- __auxfile (str)__: auxiliary file name and path to store the output of selected model
                   parameters
- __auxlist (list)__: list of model parameters to additionally output

!!! note
    For hourly runs, the `duration` argument is always set for 24 simulation hours,
    regardless of the supplied argument value.

__Example__

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

__Returns__

`None`:


<h3 id="facade.Facade.runxlmacro">runxlmacro</h3>

```python
Facade.runxlmacro(xl_fname, xl_macroname, *args)
```

!!! note
    `runxlmacro` is a static method

Run Excel macro stored in an Excel workbook (needs `xlwings` to be installed).
Can be used, for instance, to export model results into Excel for charting or
data analysis.

__Arguments__

- __xl_fname (str)__: name of Excel workbook to receive the model output (and has the macro)
- __xl_macroname (str)__: the name of the Excel macro in xl_fname
- __args__: variable length arguments, if any, to pass into `xl_macroname` macro function

__Returns__

`None`:


<h3 id="facade.Facade.plot_weather">plot_weather</h3>

```python
Facade.plot_weather(self, fig_no, annwthr, fname)
```

Plot charts showing the distribution and statistics of several weather properties.

__Arguments__

- __fig_no (int)__: figure number, used to create multiple windows
- __annwthr (dict)__: dictionary holding the annual daily weather data
- __fname (str)__: weather stats file name and path

__Returns__

`None`:


<h3 id="facade.Facade.output_weather_stats">output_weather_stats</h3>

```python
Facade.output_weather_stats(self, fname, append_to_file=False)
```

Write to file the daily weather parameters for the whole year and their statistics.

Daily weather parameters to be written to an output file are min. and max. air
temperatures, wind speed, rain, and solar irradiance. Some basic statistics will
be computed and written together to the file as well.

Charts will be drawn as visual output.

__Arguments__

- __fname (str)__: output file (plain text file)
- __append_to_file (bool)__: `False` (default) to create a new output file, else
                           `True` to append output to an exisiting file

__Returns__

`None`:


