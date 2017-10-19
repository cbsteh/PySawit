<h1 id="utils">utils <em>module</em></h1>


utils module.

General-purpose utilities.

__Author - Christopher Teh Boon Sung__

------------------------------------


<h2 id="utils.AFGen">AFGen <em>class</em></h2>


Table lookup class.

Linear inter- or extrapolation for a given set of tabulated (x,y) data. Stores (x,y) values
and uses linear inter- or extrapolation, if needed, to return y based on a given x.

Sorts the data based on x values in an ascending order.

__METHODS__

- `val`: Given x, return its corresponding y for a list of (x,y) pairs


<h3 id="utils.AFGen.__init__"><em>Constructor</em> __init__</h3>

```python
AFGen(self, xydict)
```

Create and initialize the AFGen object.

__Arguments__

- __xydict (dict)__: dictionary holding the (x,y) pairs of values


<h3 id="utils.AFGen.val">val</h3>

```python
AFGen.val(self, x)
```

Given x, return y, using linear extra- or interpolation if needed.

__Arguments__

- __x (int/float)__: the x in (x,y) pair of values

__Returns__

`int/float`: y value


<h2 id="utils.Float">Float <em>class</em></h2>


Proxy class for floats (can also be used for integers).

Wraps a float number, so that whenever its value is used, a function is called first
to returned a desired value This wrapper class allows some pre-computations (to be
done by the stored function) to be carried out first before returning the desired value.

__ATTRIBUTES__

- `fn`: Function to be called when the value of the float is used
- `args`: Variable length arguments to be passed into `fn`, if any
- `kwargs`: Dictionary to be passed into `fn`, if any

__METHODS__

- `real`: Calls the stored function
- `__float__`: Float conversion will call the stored functon

__EXAMPLE__

```python
def power(base, exponent):
    return base ** exponent

def foo(val):
    print(val.real)     # prints whatever value that has been passed into foo

foo(8)                  # prints an integer: 8
foo(8.0)                # prints a float: 8.0
f = Float(power, 2, 3)  # will call power(2,3) when f is used
foo(f)                  # prints an integer: 8
foo(float(f))           # prints a float: 8.0
f.args = [3,2]          # change the base to 3 and exponent to 2
foo(f)                  # prints an integer: 9
```


<h3 id="utils.Float.__init__"><em>Constructor</em> __init__</h3>

```python
Float(self, fn, *args, **kwargs)
```

Create and initialize the Float object.

Setup the function to call and its required arguments, if any.

__Arguments__

- __fn__: function to call, with its paramaters, if any
- __args__: positional parameters of `fn` function
- __kwargs__: dictionary parameters of `fn` function

!!! note
    `fn` function must return the intended object/value


<h3 id="utils.Float.__float__">__float__</h3>

```python
Float.__float__(self)
```

Override `__float__` conversion method.

The saved function `fn()` is called when float() conversion is applied to this class.

__Returns__

`float`: return value of `fn()`


<h3 id="utils.Float.real">real</h3>


Override `real` property.

The saved function `fn()` is called when the value of the float is used.

__Returns__

`float`: return value of `fn()`


<h2 id="utils.set_common_path">set_common_path <em>function</em></h2>

```python
set_common_path(path='')
```

Return a wrapper function that prefix the same, common path to all file names.

A shortcut to avoid typing or specifying the same path to all files. This method will
check if specified path exists.

__Arguments__

- __path (str)__: the common path to all files

__Raises__

- `IOError`: if invalid or non-existant file path or file name (see Example)

__Example__


```python
addpath = set_common_path('C:\\Users\\adminuser')
print(addpath('ini.txt')        # this will print: C:\Users\adminuser\ini.txt
print(addpath('ini.txt', True)  # set the second argument to True (default is False)
                                #   to check if file 'ini.txt' exist, else raises
                                #   IOError exception. If the second argument is set
                                #   to False, no check for the file name is done.
                                #   Set the second argument to False (or leave it
                                #   unspecified) if the file is an output file, but
                                #   for an input or initialization file that will
                                #   read, this file must already exist, so set the
                                #   second argument to True for all input files.
```

Whether the second argument is `True` or `False`, this function will check if
the specified file path (excluding the file name) exist. If not, the exception
`IOError` is raised.

This function will append the folder slash symbol if the path has no such
slash as the end of the path, e.g., `'C:\\Users\\adminuser'`


