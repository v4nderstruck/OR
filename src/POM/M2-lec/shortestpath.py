from typing import List
import gurobipy.gurobipy as gp
import networkx as nx

def solve_with_graph(G, s, t):
    model = gp.Model("shortestpath")

    # add variables to indicate path from i to j
    x = {}
    for (i, j) in G.edges:
        x[i, j] = model.addVar(obj=1, vtype=gp.GRB.BINARY,
                               name="EDGE_{}_{}".format(i, j))

    # add weights
    weight = model.addVar(obj=1, vtype=gp.GRB.INTEGER, name="WEIGHT")
    # add flow constraints, sum of in edges = sum of out edges  for non source/target
    # for source node it should be 1
    # for target node it should be -1
    for i in G.nodes:
        in_edges = G.in_edges(i)
        out_edges = G.out_edges(i)
        if i == s:
            model.addConstr(
                gp.quicksum(x[k, l] for (k, l) in out_edges)  # type: ignore
                - gp.quicksum(x[n, m] for (n, m) in in_edges) == 1, "Source")  # type: ignore
        elif i == t:
            model.addConstr(
                gp.quicksum(x[k, l] for (k, l) in out_edges)  # type: ignore
                - gp.quicksum(x[n, m] for (n, m) in in_edges) == -1, "Target")  # type: ignore
        else:
            model.addConstr(
                gp.quicksum(x[k, l] for (k, l) in out_edges)  # type: ignore
                - gp.quicksum(x[n, m] for (n, m) in in_edges) == 0, "Node_{}".format(i))  # type: ignore


    # add weight constraint
    model.addConstr(gp.quicksum(
        x[i, j] * G[i][j]['weight'] for (i, j) in G.edges) == weight,
        "Weight")

    model.update()
    # add objective, weights of edges in shortest path, minimize steps
    model.setObjective(weight, gp.GRB.MAXIMIZE) 
    

    model.optimize()

    def printSolution():
        if model.status == gp.GRB.OPTIMAL:
            print('\n objective: %g\n' % model.ObjVal)
            path = []
            for (i, _j), value in x.items():
                if value.x > 0.9:
                    path.append(i)

            path.append(t)
            # print("MIP solition: ", path)
        else:
            print("No solution!")
    printSolution()
    
# repurpose for knapsack problem
# n number of vertices, s source node, t target, E edges with weight as tuplelist
def solve(n, E, s, t):
    G = nx.DiGraph()
    # add nodes from 0 to n-1
    G.add_nodes_from(range(n))
    # add edges
    G.add_weighted_edges_from(E)
    solve_with_graph(G, s, t)

    # print("Nodes of graph: ", G.nodes)
    # print("Edges of graph: ", G.edges)
    # print("IsWeighted: ", nx.is_weighted(G))
    # sp = nx.dijkstra_path(G, s, t)
    # print("Shortest Path: ", sp)

