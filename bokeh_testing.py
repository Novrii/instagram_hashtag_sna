import networkx as nx

from bokeh.io import output_file, show
from bokeh.models import (BoxSelectTool, Circle, EdgesAndLinkedNodes, HoverTool,
                        MultiLine, NodesAndLinkedEdges, Plot, Range1d, TapTool, 
                        BoxZoomTool, ResetTool)
from bokeh.palettes import Spectral4
from bokeh.plotting import from_networkx

import json

# Prepare Data
G_symmetric = nx.Graph()
relations = []
# start_time = time.time()

with open('relations.json') as openfile:
    relations = json.load(openfile)

for edge in relations:
    G_symmetric.add_edge(edge['node1'], edge['node2'])

# pos = nx.spring_layout(G_symmetric)
# betCent = nx.betweenness_centrality(G_symmetric, normalized=True, endpoints=True)
# node_color = [20000.0 * G_symmetric.degree(v) for v in G_symmetric]
# node_size =  [v * 10000 for v in betCent.values()]
# nx.draw_networkx(G_symmetric, pos=pos, with_labels=False,
#                 node_color=node_color,
#                 node_size=node_size )

# Show with Bokeh
plot = Plot(plot_width=800, plot_height=800,
            x_range=Range1d(-1.1,1.1), y_range=Range1d(-1.1,1.1))
plot.title.text = "Graph Interaction Demonstration"

plot.add_tools(HoverTool(), TapTool(), BoxSelectTool(), BoxZoomTool(), ResetTool())

graph_renderer = from_networkx(G_symmetric, nx.spring_layout, scale=5, center=(0,0))

graph_renderer.node_renderer.glyph = Circle(size=15, fill_color=Spectral4[0])
graph_renderer.node_renderer.selection_glyph = Circle(size=15, fill_color=Spectral4[2])
graph_renderer.node_renderer.hover_glyph = Circle(size=15, fill_color=Spectral4[1])

graph_renderer.edge_renderer.glyph = MultiLine(line_color="#CCCCCC", line_alpha=0.8, line_width=1)
graph_renderer.edge_renderer.selection_glyph = MultiLine(line_color=Spectral4[2], line_width=1)
graph_renderer.edge_renderer.hover_glyph = MultiLine(line_color=Spectral4[1], line_width=1)

graph_renderer.selection_policy = NodesAndLinkedEdges()
graph_renderer.inspection_policy = EdgesAndLinkedNodes()

plot.renderers.append(graph_renderer)

output_file("interactive_graphs.html")
show(plot)