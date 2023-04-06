# Vertex coloring problem
# given a graph, find a coloring of the vertices such that no two adjacent vertices 
# have the same color

# goal use minimal number of colors

import gurobipy.gurobipy as gp

model: gp.Model = gp.Model("vertex_coloring")


