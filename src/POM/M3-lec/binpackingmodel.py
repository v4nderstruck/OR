import gurobipy as gp


def solve(bins_n, items_size_list, capacity):
    model = gp.Model("binpacking")

    print(range(len(items_size_list)))
    y = {}
    for j in range(bins_n):
        y[j] = model.addVar(vtype=gp.GRB.BINARY, obj=1, name="y_%s" % j)

    x = {}
    for j in range(bins_n):
        for i in range(len(items_size_list)):
            x[i, j] = model.addVar(vtype=gp.GRB.BINARY,
                                   name="x_%s_%s" % (i, j))

    # constraint: assign every item
    for i in range(len(items_size_list)):
        model.addConstr(gp.quicksum(x[i, j] for j in range(bins_n)) == 1)

    # constraint: capacity
    for j in range(bins_n):
        model.addConstr(gp.quicksum(
            items_size_list[i] * x[i, j] for i in range(len(items_size_list))) <= capacity * y[j])

    for j in range(bins_n):
        for i in range(len(items_size_list)):
            model.addConstr(x[i, j] <= y[j])

    model.modelSense = gp.GRB.MINIMIZE
    model.setObjective(gp.quicksum(y[j] for j in range(bins_n)))

    # display output

    model.update()
    model.optimize()

    def printSolution():
        if model.status == gp.GRB.OPTIMAL:
            print('\n objective: %g\n' % model.ObjVal)
        else:
            print("No solution!")
    printSolution()
