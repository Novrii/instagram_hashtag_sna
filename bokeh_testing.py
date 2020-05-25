import networkx as nx
import pandas as pd
import seaborn as sns
import numpy as np

from bokeh.io import output_file, show
from bokeh.models import (BoxZoomTool, Circle, HoverTool, ColumnDataSource, LinearColorMapper, MultiLine, Plot, Range1d, ResetTool,)
from bokeh.palettes import Spectral4
from bokeh.plotting import from_networkx

# Prepare Data
G = nx.karate_club_graph()

SAME_CLUB_COLOR, DIFFERENT_CLUB_COLOR = "black", "red"
edge_attrs = {}

for start_node, end_node, _ in G.edges(data=True):
    edge_color = SAME_CLUB_COLOR if G.nodes[start_node]["club"] == G.nodes[end_node]["club"] else DIFFERENT_CLUB_COLOR
    edge_attrs[(start_node, end_node)] = edge_color

nx.set_edge_attributes(G, edge_attrs, "edge_color")

bc = nx.degree_centrality(G)

# Some Random index
node_color = {k:30*v for k, v in bc.items()}

#just to make the sizes visible
node_size = {k:100*v for k,v in bc.items()} 

# print(bc)

## set node attributes
nx.set_node_attributes(G, node_color, 'node_color')
nx.set_node_attributes(G, node_size, 'node_size')

# Map cubehelix_palette
palette = sns.cubehelix_palette(21)
pal_hex_lst = palette.as_hex()

source = ColumnDataSource(pd.DataFrame.from_dict({k:v for k,v in G.nodes(data=True)},orient='index'))
mapper = LinearColorMapper(palette=pal_hex_lst, low=0, high=21)

# Show with Bokeh
plot = Plot(plot_width=400, plot_height=400,
            x_range=Range1d(-1.1, 1.1), y_range=Range1d(-1.1, 1.1))
plot.title.text = "Graph Interaction Demonstration"

node_hover_tool = HoverTool(tooltips=[("index", "@index"), ("club", "@club")])
plot.add_tools(node_hover_tool, BoxZoomTool(), ResetTool())

graph_renderer = from_networkx(G, nx.spring_layout, scale=1, center=(0, 0))

graph_renderer.node_renderer.glyph = Circle(size='node_size', fill_color={'field': 'node_color', 'transform': mapper})
graph_renderer.edge_renderer.glyph = MultiLine(line_color="edge_color", line_alpha=0.8, line_width=1)
plot.renderers.append(graph_renderer)

output_file("interactive_graphs.html")
show(plot)