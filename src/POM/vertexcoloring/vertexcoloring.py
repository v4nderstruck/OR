import os
import networkx as nx
import gurobipy.gurobipy as gp
import matplotlib.pyplot as plt
import matplotlib.cm as cm

def solve(instance_path):
    # Read Graph from instance path
    G = nx.read_adjlist(instance_path)

    # Model
    model = gp.Model("Vertex coloring")
    model.modelSense = gp.GRB.MINIMIZE

    # number of colors is given by number of nodes
    colors = range(len(G.nodes))

    # x - binary decision variable of verterxt should have color
    x = {}
    for vertex in G.nodes:
        for color in colors:
            x[vertex, color] = model.addVar(
                name=f"x_{vertex}_{color}", vtype=gp.GRB.BINARY)

    # y - binary decision variable of color is used
    y = {}
    for color in colors:
        y[color] = model.addVar(name=f"y_{color}", vtype=gp.GRB.BINARY)
    # -------------------------------------------------------------------------

    # Update the model to make variables known.
    # From now on, no variables should be added.
    model.update()

    # constraint: each vertex should be colored once
    for vertex in G.nodes:
        model.addConstr(gp.quicksum(x[vertex, color] for color in colors) == 1)

    # constraint: neighbors should not have the same color
    for (node_a, node_b) in G.edges:
        for color in colors: 
            model.addConstr(x[node_a, color] + x[node_b, color] <= 1)

    # constraint: when node is colored, color is used
    for vertex in G.nodes:
        for color in colors:
            model.addConstr(x[vertex, color] <= y[color])

    model.update()
    # For debugging: print your model
    # model.write('model.lp')
    model.optimize()

    # TODO: Adjust your dict keys for y[...] to print out the selected --------
    # colors from your solution and then uncomment those lines.
    # This is not not necessary for grading but helps you confirm that your
    # model works

    # Printing solution and objective value
    def printSolution():
        if model.status == gp.GRB.OPTIMAL:
            print('\n objective: %g\n' % model.ObjVal)
            print("Selected following colors:")
            for color in colors:
                if y[color].x >= 0.9: # for numerical reasons never compare against 1
                    vertices_string = ""
                    for vertex in G.nodes:
                        if x[vertex, color].x >= 0.9:
                            vertices_string += f"{vertex} "
                    print(f"Color {color} is assigned to vertices {vertices_string}")
        else:
            print("No solution!")

    def drawSolution(): 
        newG = nx.Graph()
        for vertex in G.nodes:
            for color in colors:
                if x[vertex, color].x >= 0.9:
                    newG.add_node((vertex,color))
        for (node_a, node_b) in G.edges:
            # find vertex node_a in newG
            (_vertext_a, color_a) = [node for node in newG.nodes if node[0] == node_a][0]
            (_vertext_b, color_b) = [node for node in newG.nodes if node[0] == node_b][0]
            newG.add_edge((node_a, color_a), (node_b, color_b))  

        pos = nx.spring_layout(G)
        # create a copy of dictionary of pos but for keys (vertex, color) matching vertex only
        pos2 = {newk: v for k, v in pos.items() for newk in newG.nodes if newk[0] == k}

        # make the graphs plot next to each other
        fig, ax = plt.subplots(1, 2, figsize=(20, 10))
        nx.draw(G, pos=pos, ax=ax[0], with_labels=True)
        nx.draw(newG, pos=pos2, ax=ax[1], with_labels=True)
        plt.show()

    printSolution()
    drawSolution()
    # Please do not delete the following line
    return model


if __name__ == '__main__':
    dir_path = os.path.dirname(os.path.realpath(__file__))
    solve(instance_path=dir_path+'/data_sets/vertexcoloring_data2.adjlist')
