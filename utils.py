"""
utils module.

General-purpose utilities.

# Author - Christopher Teh Boon Sung
------------------------------------

"""

import bisect
import os


class AFGen(object):
    """
    Table lookup class.

    Linear inter- or extrapolation for a given set of tabulated (x,y) data. Stores (x,y) values
    and uses linear inter- or extrapolation, if needed, to return y based on a given x.

    Sorts the data based on x values in an ascending order.

    # METHODS
        val: Given x, return its corresponding y for a list of (x,y) pairs

    """

    def __init__(self, xydict):
        """
        Create and initialize the AFGen object.

        # Arguments
            xydict (dict): dictionary holding the (x,y) pairs of values

        """
        self.__xy = xydict
        xkey = list(xydict.keys())  # store the dictionary keys (x values)
        xkey.sort()  # now sort the keys
        self.__xkey = xkey

    def val(self, x):
        """
        Given x, return y, using linear extra- or interpolation if needed.

        # Arguments
            x (int/float): the x in (x,y) pair of values

        # Returns
            int/float: y value

        """
        idx = bisect.bisect_left(self.__xkey, x)  # get the key closest matching x
        if idx >= len(self.__xkey):  # past max value, so use extrapolation
            y1, y2 = self.__xy[self.__xkey[idx - 2]], self.__xy[self.__xkey[idx - 1]]
            x1, x2 = self.__xkey[idx - 2], self.__xkey[idx - 1]
        elif idx == 0:  # possibly less than min. value, so use extrapolation
            y1, y2 = self.__xy[self.__xkey[0]], self.__xy[self.__xkey[idx + 1]]
            x1, x2 = self.__xkey[0], self.__xkey[idx + 1]
        else:  # interpolation between two existing pairs of values
            y1, y2 = self.__xy[self.__xkey[idx - 1]], self.__xy[self.__xkey[idx]]
            x1, x2 = self.__xkey[idx - 1], self.__xkey[idx]
        return y1 + (y2 - y1) / (x2 - x1) * (x - x1)


class Float(object):
    """
    Proxy class for floats (can also be used for integers).

    Wraps a float number, so that whenever its value is used, a function is called first
    to returned a desired value This wrapper class allows some pre-computations (to be
    done by the stored function) to be carried out first before returning the desired value.

    # ATTRIBUTES
        fn: Function to be called when the value of the float is used
        args: Variable length arguments to be passed into `fn`, if any
        kwargs: Dictionary to be passed into `fn`, if any

    # METHODS
        real: Calls the stored function
        __float__: Float conversion will call the stored functon

    # EXAMPLE
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

    """

    def __init__(self, fn, *args, **kwargs):
        """
        Create and initialize the Float object.

        Setup the function to call and its required arguments, if any.

        # Arguments
            fn: function to call, with its paramaters, if any
            args: positional parameters of `fn` function
            kwargs: dictionary parameters of `fn` function

        !!! note
            `fn` function must return the intended object/value

        """
        self.fn = fn    # function to be called
        self.args = args  # the function fn's arguments
        self.kwargs = kwargs

    def __float__(self):
        """
        Override `__float__` conversion method.

        The saved function `fn()` is called when float() conversion is applied to this class.

        # Returns
            float: return value of `fn()`

        """
        return float(self.real)     # must return a float

    @property
    def real(self):
        """
        Override `real` property.

        The saved function `fn()` is called when the value of the float is used.

        # Returns
            float: return value of `fn()`

        """
        return self.fn(*self.args, **self.kwargs)


def set_common_path(path=''):
    r"""
    Return a wrapper function that prefix the same, common path to all file names.

    A shortcut to avoid typing or specifying the same path to all files. This method will
    check if specified path exists.

    # Arguments
        path (str): the common path to all files

    # Raises
        IOError: if invalid or non-existant file path or file name (see Example)

    # Example

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

    """
    def wrapper(filename, filename_must_exist=False, p=path):
        """
        Concatenate file path and file name.

        This function will check if specified path is valid and if it exists.

        # Arguments
            filename (str): name of file
            filename_must_exist (bool): set to `True` to check if file exist (default is `False`)
            p (str): full path (excluding filename) to file

        # Raises
            IOError: if invalid or non-existent file path or file name

        """
        if p != '' and not os.path.exists(p):
            raise IOError('Invalid path specified or path does not exist.')
        sep = '\\'      # default path character
        if p == '' or p[-1] == '\\' or p[-1] == '/':
            sep = ''
        elif p.find('\\') >= 0:
            sep = '\\'
        elif p.find('/') >= 0:
            sep = '/'
        fullpath = sep.join([p, filename])
        if filename_must_exist and not os.path.exists(fullpath):
            raise IOError(filename + ' does not exist in the specified path.')
        return fullpath

    return wrapper
