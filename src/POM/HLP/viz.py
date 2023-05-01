import matplotlib.pyplot as plt
import networkx as nx
import json
import os
import graphviz

dir_path = os.path.dirname(os.path.realpath(__file__))
full_instance_path = dir_path+'/n10.json'
with open(full_instance_path) as f:
    data = json.load(f)

customers = data["customers"]
distances = data["distances"]
demands = data["demands"]


print("customers", len(customers))

for demand in demands:
    print("demand", demand)

# graph from adjacency matrix
g = nx.Graph()
g.add_nodes_from(customers)
for i in range(len(distances)):
    for j in range(len(distances[i])):
        d = distances[i][j]
        if d > 0: 
            g.add_edge(i, j, weight=d)


for demand in demands:
    print("demand", demand)


# pos = nx.nx_agraph.graphviz_layout(g, "neato")
# nx.draw_networkx(g, with_labels=True, pos=pos)
# plt.show()
