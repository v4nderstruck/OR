# transportation problem
# given a set of sources and a set of destinations that have some amount of
# supplies and demand, and a cost matrix of transportation

# assuming single item
# > find a cost minimal cost transport solution that satifies all demands and ships every supply

import gurobipy.gurobipy as gp

model: gp.Model = gp.Model("transportation")

# i = source, j = destination
i = 4
j = 8

# cost matrix, cost per unit of transport
c = [
    [2, 1, 3, 4, 5, 6, 7, 8],
    [12, 1, 1222, 3, 1, 56, 2, 2],
    [1, 12, 55, 12, 4, 5, 67, 2],
    [92, 2, 45, 67, 112, 42, 1, 2]
]

# demand at destination
demand = [10, 10, 20, 21, 102, 223, 1, 45]

# supply at source
supply = [100, 204, 150, 14]

# assignment a, ammount of units to be transported
a = {}
for source in range(i):
    for dest in range(j):
        a[source, dest] = model.addVar(
            name=f"{source}_{dest}", vtype=gp.GRB.INTEGER)

# constraints: do not exceed supplies
for source in range(i):
    model.addConstr(gp.quicksum(a[source, dest]
                    for dest in range(j)) <= supply[source])

# constraints: satisfy demand or deliver more
for dest in range(j):
    model.addConstr(gp.quicksum(a[source, dest]
                    for source in range(i)) >= demand[dest])

# set objective to minimize cost
model.setObjective(gp.quicksum(c[source][dest] * a[source, dest]
                  for source in range(i) for dest in range(j)), gp.GRB.MINIMIZE)

model.optimize()

# get solution
for v in model.getVars():
    print(v.VarName, v.X)

print('Obj:', model.ObjVal)

