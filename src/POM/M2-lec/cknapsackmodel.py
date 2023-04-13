#!/usr/bin/env python3

import gurobipy.gurobipy as gp

# item sizes a, item profits p, capacity b, conflicts c
def solve(a, p, b, c):
    model = gp.Model("knapsack")
    # use item i
    x = []
    for _i in range(len(a)):
        x.append(model.addVar(obj=1, vtype=gp.GRB.BINARY, name="X"))

    # capacity constraint

    model.addConstr(gp.quicksum(a[i]*x[i]
                    for i in range(len(a))) <= b, "Capacity")

    # conflicts 
    for (i, j) in c: 
        model.addConstr(x[i] + x[j] <= 1, "Conflict of {}_{}".format(i,j))

    # set object to maximize profit

    model.setObjective(gp.quicksum(p[i]*x[i]
                       for i in range(len(x))), gp.GRB.MAXIMIZE)

    model.update()
    model.optimize()

    def printSolution():
        if model.status == gp.GRB.OPTIMAL:
            print('\n objective: %g\n' % model.ObjVal)
            # for i,item in enumerate(x):
            #     print(' Selected items ', i, ": ", item.x)
        else:
            print("No solution!")
    printSolution()
# optimize
