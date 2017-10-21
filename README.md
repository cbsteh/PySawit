# PySawit v. 0.0.1 (README)

Oil Palm Growth and Yield Model

by [Christopher Teh Boon Sung](http://www.christopherteh.com)

## Overview

PySawit is a model, written in Python language, to simulate the growth and yield of oil palm. The following are various conditions among which PySawit is able to simulate:

* different planting densities
* different weather conditions (such as air temperature, rainfall, *etc.*)
* different soil properties (such as soil texture)
* different crop physiological conditions (such as flower sex ratios, specific leaf area, plant nutrient content, photosynthetic parameters, *etc.*)

At the moment, PySawit simulates crop production level 2, where oil palm is limited only by meteorological and soil water availability. Nutrients, pests, diseases, weeds, and other field practices are assumed to be optimally managed.

Read the [`brief report on PySawit.`](https://github.com/cbsteh/PySawit/blob/master/docs/pysawit.pdf)

## Installation

1. To simplify the installation process, download the [`Anaconda`](https://www.anaconda.com/download/) suite. **Make sure you only choose the Python version 3.5 or higher (NOT ver 2.7).** Downloading the [`Anaconda`](https://www.anaconda.com/download/) suite will include not only the Python interpreter but also the `matplotlib`, `numpy`, and `xlwings` modules which are required by PySawit.

1. Then, at your system's command line or prompt, type: `pip install pysawit`
to download and install the PySawit.

1. If you want the Excel user-interface to PySawit and the example files, just download the files from the `examples` folder. Or download the entire [`PySawit`](https://github.com/cbsteh/PySawit/archive/master.zip) repository.

1. You may also want to download and install [`Graphviz`](http://www.graphviz.org/Download.php) if you are planning to use PySawit's tracing feature to plot out a map of the program flow. Ensure you read the [`Graphviz`](http://www.graphviz.org/Download.php) website on how to set up the environment variable to recognize the location of graphviz files.

## How to use

Call Python on [`pysawit.py`](http://christopherteh.com/pysawit/pysawit/index.html). See this file's documentation on the commandline flags or options.

## Citation

Preliminary work of PySawit was progressively published in several conference proceedings, but the full or complete work of PySawit was first published in:

`TEH, C.B.S., & CHEAH, S.S. (2017). Modelling crop growth and yield in palm oil cultivation. In Rival, A. (Ed.) Achieving sustainable cultivation of oil palm. Cambridge, UK: Burleigh Dodds Science Publishing (In Press).`
