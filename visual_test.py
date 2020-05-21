import networkx as nx
import matplotlib.pyplot as plt
import json
import time

G_symmetric = nx.Graph()
relations = []
start_time = time.time()

with open('relations.json') as openfile:
    relations = json.load(openfile)

for edge in relations:
    G_symmetric.add_edge(edge['node1'], edge['node2'])


pos = nx.spring_layout(G_symmetric)
betCent = nx.betweenness_centrality(G_symmetric, normalized=True, endpoints=True)
node_color = [20000.0 * G_symmetric.degree(v) for v in G_symmetric]
node_size =  [v * 10000 for v in betCent.values()]
plt.figure(figsize=(10,10))
nx.draw_networkx(G_symmetric, pos=pos, with_labels=False,
                node_color=node_color,
                node_size=node_size )
plt.title('Graph #earth', fontsize = 20)
plt.axis('off')
print(f"{(time.time() - start_time):.2f} seconds")
plt.show()