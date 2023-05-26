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
    all_demand = 0
    for i in customers:
        sum_i = 0
        for j in customers:
            sum_i += demands[j][i]
        all_demand += sum_i
        demand[i] = sum_i


    all_demand = 5 * all_demand
    # assignment[i, k] = 1 if customer i is assigned to hub k
    # assuming: customers list also represents locations
    # forum discussion: https://moodle.rwth-aachen.de/mod/forum/discuss.php?d=196169
    assignment = {}
    for i in customers:
        for k in customers:
            assignment[i, k] = model.addVar(
                vtype="b", obj=1.0, name=f"assignment_{i}_{k}")

    # three index formulation: flow from started at i through hub k and hub l
    y = {}
    for i in customers:
        for k in customers:
            for l in customers:
                y[i, k, l] = model.addVar(
                    vtype="c", lb=0, name=f"y_{i}_{k}_{l}", obj=1.0)

    model.update()
    # --- Constraints ---

    # Constraint 1: dont create more than p hubs
    model.addConstr(quicksum(assignment[i, i] for i in customers) <= p)

    # Constraint 2: each customer is assigned to exactly one hub
    for i in customers:
        model.addConstr(quicksum(assignment[i, k] for k in customers) == 1)

    # Constraint 3: only assign to open hubs
    for i in customers:
        for k in customers:
            model.addConstr(assignment[i, k] <= assignment[k, k])

    for k in customers:
        model.addConstr(quicksum(y[i, k, l] for i in customers for l in customers) <= assignment[k, k] * all_demand)
        # big M constraint - makes sure that y[i, k, l] is only > 0 if l is a true hub
        model.addConstr(quicksum(y[i, l, k] for i in customers for l in customers) <= assignment[k, k] * all_demand)
    # Constraint 4: Supply must flow through open hubs
    # for i in customers:
    #     model.addConstr(y[i, i, i] == supply[i] * assignment[i, i])
    #     for k in customers:
    #         # big M constraint - makes sure that y[i, k, l] is only > 0 if k is a true hub
    #         model.addConstr(quicksum(y[i, k, l] for l in customers) <= assignment[k, k] * all_demand)
    #         # big M constraint - makes sure that y[i, k, l] is only > 0 if l is a true hub
    #         model.addConstr(quicksum(y[i, l, k] for l in customers) <= assignment[k, k] * all_demand)
    #         # a flow can only go through an open hub
    #         for l in customers:
    #             model.addConstr(y[i, k, l] <= assignment[k, k] * supply[i])
    #             model.addConstr(y[i, k, l] <= assignment[l, l] * supply[i])

    # Constraint 4: flow conservation
    for k in customers:
        for i in customers:
            # sum all demands origiting from i using demands
            model.addConstr(
                quicksum(y[i, k, l] for l in customers)
                +
                quicksum(demands[i][j] * assignment[j, k] for j in customers)
                ==
                quicksum(y[i, l, k] for l in customers)
                +
                supply[i] * assignment[i, k]
            )

    # --- Solve model ---
    model.modelSense = GRB.MINIMIZE
    model.setObjective(
        quicksum(alpha * c * distances[k][l] * y[i, k, l]
                 for i in customers for k in customers for l in customers)
        +
        quicksum(distances[i][k] * assignment[i, k] * (c * supply[i] + c * demand[i])
                 for i in customers for k in customers)
    )

    # If you want to solve just the LP relaxation, uncomment the lines below
    # model.update()
    # model = model.relax()
    model.update()
    # model = model.relax()

    model.update()
    # model.setParam(GRB.Param.Heuristics, 0.1)
    # model.setParam(GRB.Param.Cuts, 0)
    # model.setParam(GRB.Param.MIRCuts, 0)
    # model.setParam(GRB.Param.MIPFocus, 3)

    model.optimize()
    # model.write("model.lp")

    # If your model is infeasible (but you expect it to not be), comment out the lines below to compute and write out a infeasible subsystem (Might take very long)
    # model.computeIIS()
    # model.write("model.ilp")

    def printSolution():
        if model.status == GRB.OPTIMAL:

            for flows in y:
                if y[flows].x > 0:
                    i, k, l = flows
                    if assignment[k, k].x < 0.9 or assignment[l, l].x < 0.9:
                        print("{} (k:{},l:{}) {}, i->k({}) invalid".format(
                            y[flows].varName, assignment[k, k].x, assignment[l, l].x, y[flows].x, assignment[i, k].x))

                        print(
                            "     due >= {} * {}".format(assignment[i, k].x, supply[i]))
                    # else:
                    #     print("{} (k:{},l:{}) {} valid".format(
                    #         y[flows].varName, assignment[k, k].x, assignment[l, l].x, y[flows].x))

            for i, k in assignment:
                if i == k and assignment[i, k].x > 0:
                    print(
                        f"hubs {assignment[i,k].varName} {assignment[i,k].x}")
                # elif assignment[i, k].x > 0:
                #     print(
                #         f"assignment {assignment[i,k].varName} {assignment[i,k].x}")
            print('\n objective: %0.3f\n' % model.ObjVal)
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
    import os
    dir_path = os.path.dirname(os.path.realpath(__file__))
    full_instance_path = dir_path+'/n40.json'
    # p, c, alpha, customers, distances, demands = read_instance("n10.json")
    p, c, alpha, customers, distances, demands = read_instance(
        full_instance_path)

    solve(p, c, alpha, customers, distances, demands)
