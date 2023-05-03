import matplotlib.pyplot as plt
import networkx as nx
import json
import os
import graphviz
from networkx.algorithms.dominance import reduce

dir_path = os.path.dirname(os.path.realpath(__file__))
full_instance_path = dir_path+'/n10.json'
with open(full_instance_path) as f:
    data = json.load(f)

customers = data["customers"]
distances = data["distances"]
demands = data["demands"]
n = len(customers)

print("customers", len(customers))

# graph from adjacency matrix
g = nx.DiGraph()
g.add_nodes_from(customers)

for i in range(len(distances)):
    for j in range(len(distances[i])):
        d = distances[i][j]
        de = demands[i][j]
        if de > 0: 
            g.add_edge(i, j, weight=d * de)



# print(sum([demands[i][j] for i in range(n) for j in range(n) if j == 2]))


pos = nx.nx_agraph.graphviz_layout(g, "dot")
plt.figure(figsize=(10,12))
nx.draw_networkx(g, with_labels=True, pos=pos, node_size=60,font_size=8)
plt.show()
