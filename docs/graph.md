<h1 id="graph">graph <em>module</em></h1>


Graphing the program flow module.

This module aids in understanding the flow of program by creating a visual map (network graph or
map) of the program flow path. The graph map is in DOT and GML (XML) types.

!!! warning "Required installation"
    * pycallgraph (run `pip install pycallgraph`)
    * [Graphviz](http://www.graphviz.org) visualization software

__Author - Christopher Teh Boon Sung__

------------------------------------


<h2 id="graph.Graph">Graph <em>class</em></h2>


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

__METHODS__

- `trace`: traces the program flow and creates (.dot) DOT and (.gml) GML files


<h3 id="graph.Graph.__init__"><em>Constructor</em> __init__</h3>

```python
Graph(self, **kwargs)
```

Create and initialize the Graph object.

__Arguments__

- __kwargs (dict)__: change any attributes or initialize new attributes with
                   this dictionary


<h3 id="graph.Graph.prepare_graph_attributes">prepare_graph_attributes</h3>

```python
Graph.prepare_graph_attributes(self)
```

Override to change the default attributes for graph, nodes, and edges.

__Returns__

`None`:


<h3 id="graph.Graph.node">node</h3>

```python
Graph.node(self, key, attr)
```

Override to delete newlines and number and length of function calls in node labels.

__Returns__

`str`: node label


<h3 id="graph.Graph.edge">edge</h3>

```python
Graph.edge(self, edge, attr)
```

Override to delete edge labels.

__Returns__

`str`: edge label


<h3 id="graph.Graph.done">done</h3>

```python
Graph.done(self)
```

Override to avoid creating the graph picture file.

__Returns__

`None`:


<h3 id="graph.Graph.update">update</h3>

```python
Graph.update(self)
```

Override to avoid warning message to implement all abstract methods.

Does nothing.

__Returns__

`None`:


<h3 id="graph.Graph.trace">trace</h3>

```python
Graph.trace(self, fn, fname, exclude_from_trace=None, strings_to_delete=None, class_colors=None)
```

Trace the program flow and creates DOT (*.dot) and GML (*.gml) files.

__Arguments__

- __fn (object)__: function to call for the entry point to trace the program flow
- __fname (str)__: filename for graph files (do not supply file extension)
- __exclude_from_trace (list)__: names (`str`) to exclude from trace (`None` by default)
- __strings_to_delete (list)__: text (`str`) to remove from graph files (`None` by default)
- __class_colors (dict)__: node colors (`None` by default)

__Returns__

`None`:


