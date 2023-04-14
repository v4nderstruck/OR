#!/usr/bin/env python3
import gurobipy as gp
import json
import networkx as nx
from networkx.readwrite import json_graph


def find_max_time(jobs):
    """Find the maximum time in the jobs"""
    max_time = 0
    for _job_id, job in jobs:
        max_time = max(max_time, job["j_d"])
    return max_time


def expand_graph(G: nx.DiGraph, jobs):
    """Expands the time-expanded graph by destination sinks with 0 weight (see notes)"""
    for job_id, job in jobs:
        time_start = job["j_r"]
        time_end = job["j_d"]
        destination = job["j_t"]
        G.add_node(("JOB"+job_id, "EOL"))

        for time in range(time_start, time_end + 1):
            G.add_edge((destination, time), ("JOB"+job_id, "EOL"), weight=0)

# --- TODO ---
# This function is missing not only its content but also proper documentation! We recommend you to finish the docstring
# As a sidenote, in most code editors you can add function comment strings like below automatically with a key combination. For VSC, the extension autoDocstring is necessary.


def build_graph(g_street, jobs):
    """Constructs the time-expanded graph

    Args:
        g_street (nx.Graph): Graph describing the street network
        jobs (dict_items): list of jobs (job_id, {j_s, j_t, j_r, j_d})

    Returns:
        time expanded graph (nx.DiGraph)
    """

    # New directed graph
    g_time_expanded = nx.DiGraph()
    max_time = find_max_time(jobs)

    # building time expanded graph for each time plane, create nodes
    nodes = []
    for i in range(max_time + 1):
        for node in g_street.nodes:
            nodes.append((node, i))

    # adding weighted edges, each neihgbouring node in the street graph is
    # connected directionally to the time layer offsetted by the weight, we keep the
    # weight for calculations later.
    edges = []

    # first edges where we may move the container!
    for node in g_street.nodes:
        for neighbor in g_street.neighbors(node):
            for time in range(max_time + 1):
                if time + g_street[node][neighbor]["weight"] <= max_time:
                    edges.append(
                        (
                            (node, time),
                            (neighbor, time +
                             g_street[node][neighbor]["weight"]),
                            g_street[node][neighbor]["weight"]
                        )
                    )
    # then the waiting edges
    for node in g_street.nodes:
        for time in range(max_time):
            edges.append(((node, time), (node, time + 1), 1))

    # finally, build the graph
    g_time_expanded.add_nodes_from(nodes)
    g_time_expanded.add_weighted_edges_from(edges)

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
    jobs, g_street = read_instance(full_instance_path)

    # Construct graph --- NOTE: Please use networkx for this task, it is necessary for the plots in the Jupyter file.
    g_time_expanded = build_graph(g_street, jobs.items())
    expand_graph(g_time_expanded, jobs.items())

    # === Gurobi model ===
    model = gp.Model("AGV")

    # --- Variables ---

    # Commodity arc variables
    x = {}  # --- TODO ---
    for e1, e2 in g_time_expanded.edges:
        for job in jobs:
            x[e1, e2, job] = model.addVar(
                obj=1, vtype=gp.GRB.BINARY, name="x_({},{})_{}".format(e1, e2, job).replace(" ", ""))

    # Potentially additional variables? --- TODO ---

    # --- Constraints

    # find a short path for each job
    for job_id, job in jobs.items():
        start_node = (job["j_s"], job["j_r"])
        end_node = ("JOB"+job_id, "EOL")
        for node in g_time_expanded.nodes:
            any_in_edges = g_time_expanded.in_edges(node)
            any_out_edges = g_time_expanded.out_edges(node)
            # sum to 1
            if node == start_node:
                model.addConstr(
                    gp.quicksum(x[e1, e2, job_id]
                                for e1, e2 in any_out_edges)  # type: ignore
                    -
                    gp.quicksum(x[e1, e2, job_id]
                                for e1, e2 in any_in_edges) == 1,  # type: ignore
                )

            # sum to -1
            elif node == end_node:
                model.addConstr(
                    gp.quicksum(x[e1, e2, job_id]
                                for e1, e2 in any_out_edges)  # type: ignore
                    -
                    gp.quicksum(x[e1, e2, job_id]
                                for e1, e2 in any_in_edges) == -1,  # type: ignore

                )
            # sum to 0
            else:
                model.addConstr(
                    gp.quicksum(x[e1, e2, job_id]
                                for e1, e2 in any_out_edges)  # type: ignore
                    -
                    gp.quicksum(x[e1, e2, job_id]
                                for e1, e2 in any_in_edges) == 0,  # type: ignore
                )
    # Paths are used only once at a time
    
    # nodes can only hold one waiting job

    # Solve the model
    model.update()
    model.optimize()
    # If your model is infeasible (but you expect it to not be), comment out the lines below to compute and write out a infeasible subsystem (Might take very long)
    # model.computeIIS()
    # model.write("model.ilp")

    return model, g_time_expanded
