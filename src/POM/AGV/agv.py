#!/usr/bin/env python3
import gurobipy as gp
import json
import networkx as nx
from networkx.readwrite import json_graph

# --- TODO ---
# This function is missing not only its content but also proper documentation! We recommend you to finish the docstring
# As a sidenote, in most code editors you can add function comment strings like below automatically with a key combination. For VSC, the extension autoDocstring is necessary.
def build_graph(g_street, jobs):
    """Constructs the time-expanded graph

    Args:
        g_street (which datatype?): What is this?
        jobs (which datatype?): Good documentation is important!

    Returns:
        (some datatype(s)): what do you want to return?
    """

    # New directed graph
    g_time_expanded = nx.DiGraph()

    # Adding nodes --- TODO ---

    # Adding arcs --- TODO ---

    return g_time_expanded

# You do not need to change anything in this function
def read_instance(full_instance_path):
    """Reads JSON file

    Args:
        full_instance_path (string): Path to the instance

    Returns:
        Dictionary: Jobs
        nx.DiGraph: Graph of the street network
    """
    with open(full_instance_path) as f:
        data = json.load(f)
    return (data['jobs'], json_graph.node_link_graph(data['graph']))


# Lots of work to do in this function!
def solve(full_instance_path):
    """Solving function, takes an instance file, constructs the time-expanded graph, builds and solves a gurobi model

    Args:
        full_instance_path (string): Path to the instance file to read in

    Returns:
        model: Gurobi model after solving
        G: time-expanded graph
    """

    # Read in the instance data
    jobs, g_street= read_instance(full_instance_path)

    # Construct graph --- NOTE: Please use networkx for this task, it is necessary for the plots in the Jupyter file.
    g_time_expanded = build_graph(g_street, jobs)

    # === Gurobi model ===
    model = gp.Model("AGV")

    # --- Variables ---

    # Commodity arc variables
    x = {}  # --- TODO ---

    # Potentially additional variables? --- TODO ---

    # --- Constraints
    # --- TODO ---

    # Solve the model
    model.update()
    model.optimize()
    # If your model is infeasible (but you expect it to not be), comment out the lines below to compute and write out a infeasible subsystem (Might take very long)
    # model.computeIIS()
    # model.write("model.ilp")

    return model, g_time_expanded 
