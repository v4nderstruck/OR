import gurobipy.gurobipy as gp
import networkx as nx
import matplotlib.pyplot as plt


def knapgraph(a, p, b):
    G = nx.DiGraph()
    G.add_nodes_from([(c, i) for c in range(b+1) for i in range(len(a))])

    # make edges for unused capacity e.g. cannot fit any more items?
    # make edges for skipping item
    # make edges for using item

    add_edges = [((c, i), (c+1, i), 0)
                 for i in range(len(a)) for c in range(b)]
    add_edges += [((c, i), (c, i+1), 0)
                  for c in range(b+1) for i in range(len(a)-1)]
    add_edges += [((c, i), (c+a[i], i+1), p[i])
                  for i in range(len(a)) for c in range(b-a[i] + 1)]

    G.add_weighted_edges_from(add_edges)

    return G


def grouped(iterable, n):
    return zip(*[iter(iterable)]*n)


def decode_path(path):
    selected_items = []
    for (c, i), (k, j) in zip(path, path[1:]):
        if i + 1 == j and c < k:
            selected_items.append(i)
    return selected_items


# a - size of each item, p - profits, b = capacity
def solve(a, p, b):
    G = knapgraph(a, p, b)
    import shortestpath 
    shortestpath.solve_with_graph(G, (0, 0), (b, len(a)-1))

    # path = nx.dag_longest_path(G)
    # selected_items = decode_path(path)
    # print("Objective", sum(p[i] for i in selected_items))
