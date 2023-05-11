#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 00:31:05 2020

@author: luebbecke
"""

from gurobipy import *

# item sizes a, item profits p, capacity b
def solve(a, p, b):
    model = Model("knapsack")   

    # a binary variable per item (selected or not); gives profit if selected
    x = {}
    for i in range(len(a)):
        x[i] = model.addVar(vtype='b', obj=p[i])
    
    # capacity constraint
    model.addConstr(quicksum(a[i] * x[i] for i in range(len(a))) <= b)    
    
    # by default gurobi is minimizing
    model.ModelSense = GRB.MAXIMIZE
    
    # write model to file, helps in debugging
    model.write("model.lp")
    
    # off we go
    model.optimize()
    
    # trivial output
    print("we select the following items:")
    for i in range(len(a)):
        if x[i].x > 0.1:
            print(i)
    print("the profit of this packing is " + str(model.objval))
        