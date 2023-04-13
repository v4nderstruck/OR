#!/usr/bin/env python3

# item sizes
a = [7, 4, 6, 4, 5, 4, 3, 4, 6, 7]

# profits
p = [5, 4, 4, 6, 4, 7, 4, 5, 7, 3]

# knapsack capacity
b = 20

# import model and solve
import knapsackmodel
knapsackmodel.solve(a, p, b)
import knapsackgraph
knapsackgraph.solve(a, p, b)

