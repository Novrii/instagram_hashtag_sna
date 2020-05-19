import networkx as nx
import pprint
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.font_manager import FontProperties
import time
import json
import collections

G_symmetric = nx.Graph()
relations = []
start_time = time.time()

def sort_and_small_dict(d, n):
    sorted_dict = collections.OrderedDict(sorted(d.items(), key=lambda x: -x[1]))
    firstnpairs = list(sorted_dict.items())[:n]
    return firstnpairs

def centrality_to_str_arr(centrality):
    str_arr = []
    for item in centrality:
        str_arr.append(item[0] + ' | ' + str(round(item[1], 2)))
    return str_arr

with open('relations.json') as openfile:
    relations = json.load(openfile)

for edge in relations:
    G_symmetric.add_edge(edge['node1'], edge['node2'])

# Betweenness centrality
bet_cen = nx.betweenness_centrality(G_symmetric)
bet_cen = sort_and_small_dict(bet_cen, 5)

# print("bet:",bet_cen)

# Table summarising results
fig, ax = plt.subplots()
fig.patch.set_visible(False)
ax.axis('off')
ax.axis('tight')
data = [centrality_to_str_arr(bet_cen)]
data = np.transpose(data)
table = ax.table(colLabels=['Betweenness Centrality'],
                cellText=data,
                loc='center')
for (row, col), cell in table.get_celld().items():
    if (row == 0) or (col == -1):
        cell.set_text_props(fontproperties=FontProperties(weight='bold'))
fig.tight_layout()
plt.savefig("./bet-cen.png", dpi=300)
print(f"{(time.time() - start_time):.2f} seconds")
plt.show()