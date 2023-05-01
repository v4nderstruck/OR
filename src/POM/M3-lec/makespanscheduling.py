import gurobipy as gp


def solve(m_machines, jobs_durations, capacity):
    model = gp.Model("makespanscheduling")
    n_jobs = len(jobs_durations)

    c = model.addVar(vtype=gp.GRB.INTEGER, name="c")

    x = {}
    for j in range(m_machines):
        for i in range(n_jobs):
            x[i, j] = model.addVar(vtype=gp.GRB.BINARY,
                                   name="x_%s_%s" % (i, j))

    # constraint: assign every job
    for i in range(n_jobs):
        model.addConstr(gp.quicksum(x[i, j] for j in range(m_machines)) == 1)

    #  total duration max
    for j in range(m_machines):
        model.addConstr(gp.quicksum(jobs_durations[i] * x[i, j] for i in range(n_jobs)) <= c)

    model.addConstr(c <= 70)

    model.modelSense = gp.GRB.MINIMIZE
    model.setObjective(c)


    model.update()
    model.optimize()

    def printSolution():
        if model.status == gp.GRB.OPTIMAL:
            print('\n objective: %g\n' % model.ObjVal)
        else:
            print("No solution!")
    printSolution()
