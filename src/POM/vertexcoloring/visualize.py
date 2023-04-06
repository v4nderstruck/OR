import networkx as nx
import matplotlib.pyplot as plt
import os 

dir_path = os.path.dirname(os.path.realpath(__file__))
data_1 = dir_path + "/data_sets/vertexcoloring_data1.adjlist"
data_2 = dir_path + "/data_sets/vertexcoloring_data2.adjlist"


graph_1 = nx.read_adjlist(data_1)
graph_2 = nx.read_adjlist(data_2)


print(graph_1.edges)
# nx.draw(graph_1, with_labels=True)
# plt.show()
