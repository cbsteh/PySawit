"""
Graphing the program flow module.

This module aids in understanding the flow of program by creating a visual map (network graph or
map) of the program flow path. The graph map is in DOT and GML (XML) types.

!!! warning "Required installation"
    * pycallgraph (run `pip install pycallgraph`)
    * [Graphviz](http://www.graphviz.org) visualization software

# Author - Christopher Teh Boon Sung
------------------------------------

"""


import os
import re

import pycallgraph
from pycallgraph.output import GraphvizOutput


class Graph(GraphvizOutput):
    """
    Graph class.

    Creates a network map by showing/tracing the program flow. DOT and GML (XML) files will be
    created to show the flow. Use a dedicated Graph Editor like [yEd](
    http://www.yworks.com/products/yed) to view the network map.

    Inherits the `pycallgraph.output.GraphvizOutput` class to modify certain default
    output/behavior. Override the following base methods

    ```text
        prepare_graph_attributes
        node
        edge
        done
        update
    ```

    # METHODS
        trace: traces the program flow and creates (.dot) DOT and (.gml) GML files

    """
    def __init__(self, **kwargs):
        """
        Create and initialize the Graph object.

        # Arguments
            kwargs (dict): change any attributes or initialize new attributes with
                           this dictionary

        """
        self.graph_attributes = None
        GraphvizOutput.__init__(self, **kwargs)

    def prepare_graph_attributes(self):
        """
        Override to change the default attributes for graph, nodes, and edges.

        # Returns
            None:

        """
        # change the font name and size and to have arrows for edges
        self.graph_attributes = {
            'graph': {
                'overlap': 'scalexy',
                'fontname': 'Arial',
                'fontsize': 9,
                'fontcolor': '#000000ff',   # black
            },
            'node': {
                'fontname': 'Arial',
                'fontsize': 9,
                'fontcolor': '#000000ff',
                'style': 'filled',
                'shape': 'rect',
            },
            'edge': {
                'arrowhead': 'normal',
                'fontname': 'Arial',
                'fontsize': 9,
                'fontcolor': '#000000ff',
            }
        }

    def node(self, key, attr):
        """
        Override to delete newlines and number and length of function calls in node labels.

        # Returns
            str: node label

        """
        for k in attr.keys():
            attr[k] = re.sub(r'\\n.*', '', attr[k])
        return '"{}" [{}];'.format(key, self.attrs_from_dict(attr))

    def edge(self, edge, attr):
        """
        Override to delete edge labels.

        # Returns
            str: edge label

        """
        return '"{0.src_func}" -> "{0.dst_func}"'.format(edge, self.attrs_from_dict(attr))

    def done(self):
        """
        Override to avoid creating the graph picture file.

        # Returns
            None:

        """
        pass    # do nothing (bypass the parent's done function)

    def update(self):
        """
        Override to avoid warning message to implement all abstract methods.

        Does nothing.

        # Returns
            None:

        """
        pass

    @staticmethod
    def _colorize(txt, cls_dict):
        """
        Change the color of nodes depending on class.

        !!! note
            `_colorize` is a static method.

        # Arguments
            txt (str): DOT text
            cls_dict (dict): node colors (`None` by default)

        # Returns
            str: color text

        """
        # cls is the class name; clr is its node color (in hexadecimal, must be 8 letters long)
        for cls, clr in cls_dict.items():
            fmt = cls + r'\..*color = "#.{8}"'
            for match in re.finditer(fmt, txt):
                nend = match.end()
                txt = txt[:nend - 9] + clr + txt[nend - 1:]   # substitute for the desired color
        return txt

    def trace(self, fn, fname, exclude_from_trace=None, strings_to_delete=None, class_colors=None):
        """
        Trace the program flow and creates DOT (*.dot) and GML (*.gml) files.

        # Arguments
            fn (object): function to call for the entry point to trace the program flow
            fname (str): filename for graph files (do not supply file extension)
            exclude_from_trace (list): names (`str`) to exclude from trace (`None` by default)
            strings_to_delete (list): text (`str`) to remove from graph files (`None` by default)
            class_colors (dict): node colors (`None` by default)

        # Returns
            None:

        """
        # 1. filter out some unwanted functions and classes:
        config = pycallgraph.Config()
        if exclude_from_trace is not None:
            config.trace_filter = pycallgraph.GlobbingFilter(exclude=exclude_from_trace)

        # 2. trace the program flow:
        with pycallgraph.PyCallGraph(output=self, config=config):
            fn()    # entry point for tracing the program flow
        dotstr = self.generate()

        # 3. customize the output:
        # 3a. delete strings
        if strings_to_delete is not None:
            for rx in strings_to_delete:
                dotstr = rx.sub('', dotstr)

        # 3b. customization: change color for class nodes
        if class_colors is not None:
            dotstr = Graph._colorize(dotstr, class_colors)

        # 4. create the DOT file
        fname_dot = fname + '.dot'
        with open(fname_dot, 'wt') as fdot:
            fdot.write(dotstr)

        # 5. create the GML (XML) file
        fname_gml = fname + '.gml'
        cmd = 'dot ' + fname_dot + ' | gv2gml >' + fname_gml
        os.system(cmd)      # use the dot.exe to convert the DOT file into GML file
