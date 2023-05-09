from gurobipy import *
import json

# You do not need to modify this function


def read_instance(instance_path):
    with open(instance_path) as f:
        data = json.load(f)
    return data["p"], data["c"], data["alpha"], data["customers"], data["distances"], data["demands"]


def solve(p, c, alpha, customers, distances, demands):
    """Solves the hub location problem using the 3-index formulation.

    Args:
        p (int): number of hubs to open
        c (float): cost factor for flows between customer and hub in money units per demand and distance unit
        alpha (float): discount factor for intra-hub transports
        customers (list[int]): list of customer indices
        distances (list[list[float]]): distance matrix, distances[i][j] is the distance between customer i and customer j
        demands (list[list[float]]): demand matrix, demands[i][j] is the demand from customer i to customer j

    Returns:
        Gurobi.Model: the solved model
    """
    model = Model("Hub Location")

    # test c and alpha
    # c = 1.0
    # alpha = 0.5

    # You can try and disable cutting planes - what happens?
    # model.setParam(GRB.Param.Cuts, 0)
    # NOTE: Please do not turn off cutting planes in your final submission

    supply = {}
    for i in customers:
        sum_i = 0
        for j in customers:
            sum_i += demands[i][j]
        supply[i] = sum_i

    demand = {}
    for i in customers:
        sum_i = 0
        for j in customers:
            sum_i += demands[j][i]
        demand[i] = sum_i

    assignment = {}
    for i in customers:
        for k in customers:
            assignment[i, k] = model.addVar(
                vtype="b", obj=1, name=f"assignment_{i}_{k}")

    # 4 index formulation: flow from started at i through hub k and hub l to j
    x = {}
    for i in customers:
        for j in customers:
            for k in customers:
                for l in customers:
                    x[i, j, k, l] = model.addVar(
                        vtype="b", name=f"x_{i}_{j}_{k}_{l}", obj=1.0)

    model.update()

    # --- Constraints ---
    
    # Constraint 1: maxmimal p hubs
    model.addConstr(quicksum(assignment[i, i] for i in customers) <= p)

    # Constraint 2: each customer is assigned to exactly one hub
    for i in customers:
        model.addConstr(quicksum(assignment[i, k] for k in customers) == 1)

    # Constraint 3: only assign to open hubs
    for i in customers:
        for k in customers:
            model.addConstr(assignment[i, k] <= assignment[k, k])

    # Constraint 4: x[i, *, k, l] if assignment[i, k] == 1 
    for i in customers:
        for j in customers:
            for k in customers:
                model.addConstr(quicksum(x[i, j, k, l] for l in customers) == assignment[i, k])

    # Constraint 5: x[*, j, k, l] if assignment[j, l] == 1
    for i in customers:
        for j in customers:
            for l in customers:
                model.addConstr(quicksum(x[i, j, k, l] for k in customers) == assignment[j,l])

    



    # --- Solve model ---
    model.modelSense = GRB.MINIMIZE

    model.setObjective(
        quicksum(distances[i][k] * assignment[i, k] * (c * supply[i] + c * demand[i])
                 for i in customers for k in customers)
        + 
        quicksum(alpha * c * demands[i][j] * distances[k][l] * x[i, j, k, l] 
                 for i in customers for k in customers for l in customers for j in customers)
    )
    # If you want to solve just the LP relaxation, uncomment the lines below
    # model.update()
    # model = model.relax()
    # model.update()
    # model = model.relax()

    model.update()
    # model.setParam(GRB.Param.Presolve, 0)
    # model.setParam(GRB.Param.Heuristics, 0.1)
    # model.setParam(GRB.Param.Cuts, 0)
    # model.setParam(GRB.Param.MIRCuts, 0)
    # model.setParam(GRB.Param.MIPFocus, 3)

    # model.params.LazyConstraints = 1
    model.optimize()
    # model.optimize()
    # model.write("model.lp")

    # If your model is infeasible (but you expect it to not be), comment out the lines below to compute and write out a infeasible subsystem (Might take very long)
    # model.computeIIS()
    # model.write("model.ilp")

    def printSolution():
        if model.status == GRB.OPTIMAL:
            print('\n objective: %0.3f\n' % model.ObjVal)

            # print(model.getVars())
            # for flows in x:
            #     if x[flows].x > 0:
            #         print(f"{x[flows].varName} {x[flows].x}")
        else:
            print("No solution!")
    printSolution()

    return model


# optimal values:  c = 1.0, alpha = 0.5
# n10: 63661768.81
# n20: 59358110.06
# n30: 61902278.16
# n40: 63294732.74
# n50: 63412465.95
# n60: 53915049.74
# n70: 54459098.68

if __name__ == "__main__":
    pass
    # import os
    # dir_path = os.path.dirname(os.path.realpath(__file__))
    # full_instance_path = dir_path+'/n10.json'
    # # p, c, alpha, customers, distances, demands = read_instance("n10.json")
    # p, c, alpha, customers, distances, demands = read_instance(
    #     full_instance_path)

    # solve(p, c, alpha, customers, distances, demands)
