from networkx.readwrite import json_graph


def helper():
    import os
    import agv
    import json

    dir_path = os.path.dirname(os.path.realpath(__file__))
    full_instance_path = dir_path+'/data_3.json'
    with open(full_instance_path) as f:
        data = json.load(f)
        g_street = json_graph.node_link_graph(data['graph'])
        agv.solve(full_instance_path)

        # print(json.dumps(jobs, indent=2))

helper()
