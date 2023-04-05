# minimum cost assignment problem
# > m persons and n machines
# > minize assignment cost
# > constraints: every machine must be operated, a person can operate only one

from typing import Dict
import gurobipy.gurobipy as gp
from gurobipy.gurobipy import GRB, Var, quicksum, tupledict

# modeling using gurobi
model: gp.Model = gp.Model("assignment")

# i = person, j = machine
i = 4
j = 4

# cost matrix
c = [
    [9, 2, 7, 8],
    [1, 3, 4, 5],
    [6, 5, 3, 2],
    [3, 6, 2, 7]
]
print("cost matrix", c)

# assignment matrix as variable of the model, a binary matrix
a = {}
for person in range(0, i):
    for machine in range(0, j):
        a[person, machine] = model.addVar(name="{}-{}".format(person, machine),
                                          obj=c[person][machine], vtype=GRB.BINARY)

print("assignment matrix", a.keys())

# constraint: every machine must be operated
for machine in range(0, j):
    model.addConstr(quicksum(a[person, machine]
                    for person in range(0, i)) == 1)

# constraint: a person can operate only one machine at max

for person in range(0, i):
    model.addConstr(quicksum(a[person, machine]
                    for machine in range(0, j)) <= 1)

# set objective function: minimize total assignment cost
model.setObjective(quicksum(a[person, machine] * c[person][machine]
                            for machine in range(0, j)
                            for person in range(0, i)), GRB.MINIMIZE)

# optimize model
model.optimize()

# get solution
for v in model.getVars():
    print(v.VarName, v.X)

print('Obj:', model.ObjVal)
