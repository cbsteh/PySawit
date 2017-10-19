r"""
PySawit: Oil palm growth and yield model.

This program can run in three modes:
```text
    1. Run model simulations (daily and hourly run)
    2. Output weather/meteorology statistics
    3. Create visualization network graph files
```

# OPTION (1a) - DAILY MODEL RUN

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

# Example

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


# OPTION (1b) - HOURLY MODEL RUN

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


# OPTION (2) - WEATHER STATISTICS

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

# Example

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


# OPTION (3) - NETWORK GRAPH

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

# Example

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

# SUMMARY

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

# Author - Christopher Teh Boon Sung
------------------------------------

"""


import argparse
import os
import sys
import traceback

from facade import Facade
from utils import set_common_path


def printmsg(msg, printtrace=False, wait=False):
    """
    Print a list of messages then, if needed, wait for keypress to resume (usually to exit).

    # Arguments
        msg (list): list of messages (`str`) to print to screen
        printtrace (bool): `True` to print error messages to error log file,
                           else `False` to suppress
        wait (bool): `True` to wait for Enter key press before exiting, else
                     `False` to exit immediately

    # Returns
        None:

    """
    if printtrace:
        # print errors to log file
        path = os.getcwd()
        errfile = path + '/errorlog.txt'
        traceback.print_exc(file=open(errfile, 'wt'))
        msg.append('Check "errorlog.txt" file in "{0}" for the error messages.'.format(path))
    for txt in msg:
        print(txt)
    if wait:
        keypressmsg = 'Press the Enter/Return key ...'
        input(keypressmsg)


def main():
    """
    Main entry point for the program.

    # Returns
        int: Error codes

    ```text
        0 = no error
        1 = error during model operation (e.g., simulation run) (exception errors)
        2 = error in commandline flags/options
    ```

    """
    # create the following commandline options:
    #   [-h] -i [-e -m [...]] [-p] [-o [-n | -a]]
    maingrp = argparse.ArgumentParser(add_help=False)   # avoid multiple provisions of help
    rungrp = argparse.ArgumentParser(add_help=False)    # model run option
    metgrp = argparse.ArgumentParser(add_help=False)    # weather statistics option
    netgrp = argparse.ArgumentParser(add_help=False)    # network graph option
    parser = argparse.ArgumentParser(parents=[maingrp])     # help provided only by this level

    mainman = maingrp.add_argument_group('required arguments')
    # required flags:
    mainman.add_argument('-i', required=True, metavar='filename',
                         help='path and filename for model initialization')
    mainman.add_argument('-o', required=True, metavar='filename',
                         help='path and filename for output')
    # optional flags:
    maingrp.add_argument('-e', required='-m' in sys.argv, metavar='workbook',
                         help='path and filename of Excel workbook')
    maingrp.add_argument('-m', required='-e' in sys.argv, nargs='+', metavar=('macro', 'args'),
                         help='name of Excel VBA macro, followed by its arguments, if any')
    maingrp.add_argument('-p', action='store_true', help=argparse.SUPPRESS)
    # daily model run flag:
    rungrp.add_argument('-n', metavar='days', type=int,
                        help='number of simulation days to run the model')
    # weather statistics flag:
    metgrp.add_argument('-a', action='store_true',
                        help='append to existing weather statistics file')

    subparsers = parser.add_subparsers(dest='mode')
    subparsers.add_parser('run', parents=[maingrp, rungrp])     # inherit the options
    subparsers.add_parser('met', parents=[maingrp, metgrp])
    subparsers.add_parser('net', parents=[maingrp, netgrp])

    args = parser.parse_args()
    if len(sys.argv) == 1:
        printmsg([__doc__])
        return 2

    try:
        if args.mode == 'run':
            fac = Facade(args.i, args.o)
            fac.run_simulation(True if args.n else False, args.n)
        elif args.mode == 'met':
            fac = Facade(args.i, '')   # output file not needed since no simulation runs
            fac.output_weather_stats(args.o, args.a)
        elif args.mode == 'net':
            outfile = '~temp~.txt'  # temporary output file just for tracing the program flow
            fac = Facade(args.i, outfile)
            fac.trace(args.o)
            os.remove(outfile)      # done tracing, so delete the temporary output file

        # check if calling an Excel macro is requested:
        if args.e and args.m:
            macroname = args.m[0]     # name of Excel VBA macro/subroutine
            macroargs = args.m[1:]    # VBA macro/subroutine arguments, if any
            Facade.runxlmacro(args.e, macroname, *macroargs)
    except (ArithmeticError, Exception) as e:
        printmsg(['\n', str(e), 'Aborting.'], printtrace=True, wait=args.p)
        return 1

    return 0


# main function will be called only when this file is run from the commandline
if __name__ == "__main__":
    sys.exit(main())


def __test():
    """
    Test function for debugging work.

    Do not use.

    """
    addpath = set_common_path('C:\\Users\\adminuser\\Dropbox\\cbd\\')
    fac = Facade(addpath('ini.txt', True), addpath('output.txt'))
    fac.trace('debug')
