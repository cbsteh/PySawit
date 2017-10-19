<h1 id="pysawit">pysawit <em>module</em></h1>


PySawit: Oil palm growth and yield model.

This program can run in three modes:
```text
    1. Run model simulations (daily and hourly run)
    2. Output weather/meteorology statistics
    3. Create visualization network graph files
```

__OPTION (1a) - DAILY MODEL RUN__


Usage (for daily model simulations):

```text
    pysawit.py run -i <input file>
                   -o <output file>
                   -n <duration>
                   -e <Excel workbook name> (optional)
                   -m <macro name and arguments> (optional)
```

where flags:

```text
    run is to specify either a daily or hourly model run
    -i is the path and filename to the model input (initialization) file
    -o is the path and filename of the model output (results) file
    -n is the number of simulation days
    -e (optional) is the full path name of an Excel workbook
    -m (optional) is the name of the VBA macro in the Excel workbook to run.
       If the flag -e is specified, this flag -m must be specified too.
       If the macro contains one or more arguments, they must be specified after
       the macro name, where each argument is separated by a space.
```

__Example__


On the commandline, you will type the following in only one line

```text
    pysawit.py run -i "C:\Users\adminuser\input.txt"
                   -o "C:\Users\adminuser\output.txt"
                   -n 3650
                   -e "C:\Users\adminuser\export.xlsm"
                   -m ImportResults A1 3650
```
where

```text
    1) "input.txt" is the model input file and "output.txt" is the model output
       file. Both of these files are in the "C:\Users\adminuser\" folder.
    2) The model will run for 10 years (n = 10 x 365 = 3650 days).
    3) Upon model completion, the model results will be exported to "export.xlsm"
       Excel workbook.
    4) "ImportResults" is the name of the macro in "export.xlsm" that will
       triggered to run, such as to import the model results, and "A1" and "3650"
       will be passed into the macro as its arguments.
```

!!! note
    If the flag `-e` is not specified, no export to Excel will be carried out, even if
    the flag `-m` is specified.

!!! important
    Excel export function works only in the Windows operating system.

!!! note
    File paths must be enclosed with double quotes, particularly if the file paths contain spaces.


__OPTION (1b) - HOURLY MODEL RUN__


Usage (for hourly model simulations):

```text
    pysawit.py run -i <input file>
                   -o <output file>
                   -e <Excel workbook name> (optional)
                   -m <macro name and arguments> (optional)
```

where flags

```text
    run is to specify daily or hourly model run
    -i is the path and filename to the model input (initialization) file
    -o is the path and filename of the model output (results) file
    -e (optional) is the full path name of an Excel workbook
    -m (optional) is the name of the VBA macro in the Excel workbook to run.
       If the flag -e is specified, this flag -m must be specified too.
       If the macro contains one or more arguments, they must be specified after
       the macro name, where each argument is separated by a space.
```

!!! note
    Running the hourly model simulation is exactly the same as running for the daily model
    simulations, except without the duration flag `-n`. If the `-n` flag is specified,
    daily model run will be assumed. Removing the `-n` flag runs the hourly model simulations.

!!! note
    Hourly model simuations is always at one hour time increment from hour 0 to 24.

!!! note
    File paths must be enclosed with double quotes, particularly if the file paths contain spaces.


__OPTION (2) - WEATHER STATISTICS__


Usage (for weather/meteorology statistics):

```text
    pysawit.py met -i <input file>
                   -o <weather file>
                   -a
                   -e <Excel workbook name> (optional)
                   -m <macro name and arguments> (optional)
```

where flags

```text
    met is to specify weather/meteorology statistics
    -i is the path and filename to the model input (initialization) file
    -o is the path and filename of the weather file
    -a (optional) means to append the weather stats to the existing weather
       file. If the weather file does not exist, a new one will be created.
       Omit the -a flag to create a new file or to overwrite the existing file.
    -e (optional) is the full path name of an Excel workbook
    -m (optional) is the name of the VBA macro in the Excel workbook to run.
       If the flag -e is specified, this flag -m must be specified too.
       If the macro contains one or more arguments, they must be specified
       after the macro name, where each argument is separated by a space.
```

__Example__


On the commandline, you will type the following in only one line

```text
    pysawit.py met -i "C:\Users\adminuser\input.txt"
                   -w "C:\Users\adminuser\wthr-stats.txt"
```

where

```text
    1) "input.txt" is the model input file
    2) "wthr-stats.txt" is the weather file. This is the file in which the
       weather statistics will be written.
    3) Since the -a flag is not specified, the weather file will be created.
       If the 'wthr-stats.txt' file already exists, it will be overwritten
       without notice.
```

!!! note
    Both of the input and weather files are in the `"C:\Users\adminuser\"` folder.

!!! note
    File paths must be enclosed with double quotes, particularly if the file paths contain spaces.


__OPTION (3) - NETWORK GRAPH__


Usage (for creating visualization graph files):

```text
    pysawit.py net -i <input file>
                   -o <visualization graph file>
                   -e <Excel workbook name> (optional)
                   -m <macro name and arguments> (optional)
```

where flags

```text
    net is to specify the creation of network graphs to depict program flow
    -i is the path and filename to the model input (initialization) file
    -o is the path and filename of the visualization graph files (DO NOT specify
       the file extension)
    -e (optional) is the full path name of an Excel workbook
    -m (optional) is the name of the VBA macro in the Excel workbook to run.
       If the flag -e is specified, this flag -m must be specified too.
       If the macro contains one or more arguments, they must be specified after
       the macro name, where each argument is separated by a space.
```

__Example__


On the commandline, you will type the following in only one line

```text
    pysawit.py net -i "C:\Users\adminuser\input.txt"
                   -o "C:\Users\adminuser\network"
```

where

```text
    1) "input.txt" is the model input file
    2) "network" is the network file name (without extension). Upon completion,
       two network graph files will be created: a DOT (file extension .dot) and
       a GML (file extension .gml) file. In this case, two files 'network.dot'
       and 'network.gml' will be created.
```

!!! warning
    DO NOT supply file extensions for network file name. If you do, ".dot" and ".gml" will
    be appended to the provided file extension.

!!! note
    Both of the input and network files are in the `"C:\Users\adminuser\"` folder.

!!! note
    File paths must be enclosed with double quotes, particularly if the file paths contain spaces.

__SUMMARY__


General commandline options:

```text
    pysawit.py {run|met|net} [-h]
```

`run` mode:

```text
    pysawit.py run -i -o [-n] [-e -m[...]] [-h]
```

`met` mode:

```text
    pysawit.py met -i -o [-a] [-e -m[...]] [-h]
```

`net` mode:

```text
    pysawit.py net -i -o [-e -m[...]] [-h]
```

- Flags `-i` and `-o` are required for all modes.
- Flags `-e` and `-m` are optional but if specified, they must be specified together.

__Author - Christopher Teh Boon Sung__

------------------------------------


<h2 id="pysawit.printmsg">printmsg <em>function</em></h2>

```python
printmsg(msg, printtrace=False, wait=False)
```

Print a list of messages then, if needed, wait for keypress to resume (usually to exit).

__Arguments__

- __msg (list)__: list of messages (`str`) to print to screen
- __printtrace (bool)__: `True` to print error messages to error log file,
                       else `False` to suppress
- __wait (bool)__: `True` to wait for Enter key press before exiting, else
                 `False` to exit immediately

__Returns__

`None`:


<h2 id="pysawit.main">main <em>function</em></h2>

```python
main()
```

Main entry point for the program.

__Returns__

`int`: Error codes

```text
    0 = no error
    1 = error during model operation (e.g., simulation run) (exception errors)
    2 = error in commandline flags/options
```


