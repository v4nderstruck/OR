import json
import os
import networkx as nx
from networkx.readwrite import json_graph


def find_max_time(jobs):
    """Find the maximum time in the jobs"""
    max_time = 0
    for _job_id, job in jobs:
        max_time = max(max_time, job["j_d"])
    return max_time


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


def expand_graph(G: nx.DiGraph, jobs):
    """Expands the time-expanded graph by destination sinks with 0 weight (see notes)"""
    for job_id, job in jobs:
        time_start = job["j_r"]
        time_end = job["j_d"]
        destination = job["j_t"]
        G.add_node(("JOB"+job_id, "EOL"))

        for time in range(time_start, time_end + 1):
            G.add_edge((destination, time), ("JOB"+job_id, "EOL"), weight=0)


dir_path = os.path.dirname(os.path.realpath(__file__))
with open(dir_path + "/data_2.json") as f:
    data = json.load(f)
    # print(json.dumps(data["graph"], indent=2))
    streets_graph = json_graph.node_link_graph(data["graph"])
    jobs = data["jobs"]
    G = build_graph(streets_graph, jobs.items())
    expand_graph(G, jobs.items())

    # for job_id, job in jobs.items():
    #     sg_path = nx.dijkstra_path(
    #         G, (job["j_s"], job["j_r"]), ("JOB"+job_id, "EOL"))
    #     print("Job {} Start: ({},{}) End: ({},{}) > {}".format(
    #         job_id, job["j_s"], job["j_r"], job["j_t"], job["j_d"], sg_path))

    # all_flows = ["x_({},{})_{}".format(e1, e2, j).replace(" ", "") for e1, e2 in G.edges for j in jobs]
    # print(all_flows)
    # print("inEdge", G.in_edges((1,1)))

    # print(json.dumps(jobs, indent=2))

    print("Nodes: {}".format(G.nodes))
    # get all cross
    for node in G.nodes:
        # ignore artificial nodes
        if isinstance(node[0], str) and "JOB" in node[0]:
            continue

        in_coming = G.in_edges(node)
        # print("checking In edges for {}: {}".format(node, in_coming))
        for source, into in in_coming:  # type: ignore
            # ignore waiting edges
            if source[1] == into[1] - 1 and source[0] == into[0]:
                continue

            # crossed_edges = [(e1, e2) for e1, e2 in G.edges 
            #                  if e1[0] == into[0] and e2[0] == source[0] 
            #                  and e1[1] in range(into[1] - G[source][into]["weight"], into[1])]
            crossed_edges = [(e1, e2) for e1, e2 in G.edges 
                             if e1[0] == into[0] and e2[0] == source[0] 
                             and e1[1] == into[1] - G[source][into]["weight"]]
            print("Crossed edges for {} -> {} : {}".format(source, into, crossed_edges))
    print("Max time: {}".format(find_max_time(jobs.items())))
    print(len(jobs.items()))
