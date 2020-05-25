# https://github.com/bokeh/bokeh/issues/7112
# https://stackoverflow.com/questions/46397671/using-bokeh-how-does-one-plot-variable-size-nodes-and-node-colors
import networkx as nx
import seaborn as sns

from bokeh.io import output_file, show
from bokeh.models import HoverTool, ColumnDataSource, LinearColorMapper, BoxSelectTool, Circle,  MultiLine, NodesAndLinkedEdges, Plot, Range1d, TapTool, BoxZoomTool, ResetTool, WheelZoomTool, PanTool
from bokeh.palettes import Spectral4
from bokeh.plotting import from_networkx, figure
from bokeh.embed import components

import json

# Prepare Data
G = nx.Graph()

# Data testing
# G.add_edge('Steven',  'Laura')
# G.add_edge('Steven',  'Marc')
# G.add_edge('Steven',  'John')
# G.add_edge('Steven',  'Michelle')
# G.add_edge('Laura',   'Michelle')
# G.add_edge('Michelle','Marc')
# G.add_edge('George',  'John')
# G.add_edge('George',  'Steven')

# Data hashtag
relations = []
with open('relations.json') as openfile:
    relations = json.load(openfile) # load json relasi hashtag
for edge in relations:
    G.add_edge(edge['node1'], edge['node2']) # add edge dari data json

# Centrality
dc = nx.degree_centrality(G)

# Set node size and color
node_size = {k:100*v for k, v in dc.items()}
node_color = {k:15*v for k, v in dc.items()}

for i in dc.items():
    if i[1] < 0.1:
        print(i[0])
        G.remove_node(i[0])

# print(G['Steven'])

# Set node attribute
nx.set_node_attributes(G, node_color, 'node_color')
nx.set_node_attributes(G, node_size, 'node_size')

# Map cubehelix_palette (Untuk Warna)
palette = sns.cubehelix_palette(21)
pal_hex_lst = palette.as_hex()

mapper = LinearColorMapper(palette=pal_hex_lst, low=0, high=21)

# Init Plot
plot = Plot(x_range=Range1d(-1.1,1.1), y_range=Range1d(-1.1,1.1))
plot.title.text = "Graph Interaction Demonstration"

plot.add_tools(HoverTool(tooltips=[("index", "@index")]), TapTool(), BoxSelectTool(), ResetTool(), BoxZoomTool(), WheelZoomTool(), PanTool())

# Graph render
graph = from_networkx(G, nx.spring_layout, scale=1, center=(0,0))

graph.node_renderer.glyph = Circle(size='node_size', fill_color={'field': 'node_color', 'transform': mapper})

graph.edge_renderer.glyph = MultiLine(line_color="#CCCCCC", line_alpha=0.8, line_width=1)
graph.edge_renderer.selection_glyph = MultiLine(line_color=Spectral4[2], line_width=1)
graph.edge_renderer.hover_glyph = MultiLine(line_color=Spectral4[1], line_width=1)

graph.selection_policy = NodesAndLinkedEdges()

plot.renderers.append(graph)

show(plot)

# Save div and script
script, div = components(plot)
# print(div)
# print(script)
visual_html = []
visual_html.append({
    'div' : div,
    'script' : script
})
with open('earth_html.json', 'w') as outfile:
    json.dump(visual_html, outfile) # save html part
    print("Saved")