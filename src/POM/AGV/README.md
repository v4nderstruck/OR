# Automated Guided Vehicles

## Your Goal for this Task

In this task, you will solve a so-called Automated Guided Vehicle problem. To
model the problem, we will create a time-expanded graph, a concept commonly
encountered in optimization problems with a time component. Also, you will
learn how to use the networkx library which can be helpful for future tasks.

## The Scenario

You work in an operations research team at a cargo transport company for
harbours. At a given harbour, they operate automated guided vehicles (AGV) that
transport containers around the harbour area, for example from the location
where a truck dropped it off to another location where a crane will load it
onto a ship. We assume there are always enough AGVs available and they can
transport exactly one container. Each container `j` has the following
attributes:

- Departure location: The location in the harbour where the container first
  arrives, denoted as `s[j]: V` where `V` is the set of locations where
  containers can be picked up or delivered.
- Destination location: The location where the container should be shipped to
  (denoted as `t[j]: V`)
- Release time: The time step `r[j]: int` at which the container arrives at the
  harbour and can be picked up by an AGV.
- Deadline: The last time step at which the container has to arrive at `d[j]`
  so that it can be further processed.

For simplicity, we assume that loading and unloading containers can be done
immediately. Since there are always enough AGVs available, we will model
directly the movements of the containers and ignore what the AGV does before or
after the transport is finished. To avoid collisions of the AGVs, at most one
AGV (and thus container) can move along a street connecting two locations in
the harbour at the same time. This also means that two AGVs can not travel
along the same street in opposite directions at the same time. A container may
wait at a location for arbitrary many time steps, but there is only space for
one container to wait at each location. Starting from its release time, a
container may wait at its starting location or may be transported immediately.
If a container reaches its destination, it is immediately processed and
therefore does not take up the waiting space.

Your task is to plan the routes for the containers, such that every container
is transported starting at `r[j]` and arriving at the latest at `d[j]`. The
locations and the possible streets for the AGVs between the locations are given
by an undirected weighted graph `G=(V,E)`, where the nodes represent the
locations and the edges represent the streets. The weight of an edge `w[e]:
int` represents the duration to travel along the corresponding street. The time
steps are defined by `K = 0,...,kmax` is the latest deadline of any job.

To reduce congestion at the port, the objective of the problem is to minimize
the sum of the required number of time steps to transport all containers. For
example, if a container is released at time step 5 and arrives at its
destination at time step 8, its contribution to the objective function would be
3.

**Time-Expanded Graph**

To solve this task, you need to generate a directed time-expanded graph from 
`G=(V,E)`. For this, fill in the `build_graph()` function.

The resulting Graph should look as follows:

- Create a copy of each node for every time step
- For every edge `(v1, v2)` and every timestep `0 <= k <= kmax - w`, create an
  arc from node `v1` at time `k` to `v2` at time `k+w`
- We also provide waiting arcs from a node at time step `k` to the same node at
  time step `k+1`, as long as the last time step is not exceeded.

With this time-expanded graph, the problem can be modeled as a multi-commodity
flow problem (with a few additional constraints), where a commodity represents
the movement of a container from its departure location to its destination
location over time.

## Your Submission

Modify the `agv.py` so that it solves the AGV problem by editing the file at
the highlighted positions. Your model needs to contain at least the variables
for commodity flows `x[v1, v2, j]: boolean` for every arc `(v1, v2)` and
container `j`. Iff the variable is 1 the container is transported along that
street at that time. The naming scheme should follow exactly this example

`x_((0,1),(1,3))_4,`

which represents that container 4 moves from location  0 at time step 1 to
location 1 at time step 3. 

You can partially test your model and your graphs by solving the instances
`data_1.json, data_2.json or data_3.json` in the `agv_output.ipynb` file. This
file is not part of the grading, it is just meant to assist you. Therefore, it
should not be uploaded to tutOR.

Make sure that your solve() function has the correct function signature, as
given in the file already: Its only argument is the full path to the instance
file to be solved and its return value has to have the fully solved Gurobi
model as the first element.

Note that this assignment has to be solved by each student individually.
Plagiarizing (sharing or copying the code of others) will lead to failing the
course immediately.

## Hints

**Modelling and Implementation**

- First write down the definition of the time-expanded graph and your MIP model
  on paper. We encourage you to bring it to the coding workshop and discuss it
  with us.
- By adding a few more nodes and arcs to the graph, it is possible to model the
  problem with just the x variables for every job and arc in the graph...
- ... for example you could add a sink node for each container which can be
  reached from any nodes representing the destination node at time steps before
  the deadline.
- You may use the Jupyter Notebook agv_output.ipynb to visualize your
  time-expanded graph for small instances.

**Technical** 

- Please ensure that your model is linear. If you multiply different variables,
  this will result in 0 points.
- The optimal objective value is 5 for data_1.json, 152 for data_2.json and 783
  for data_3.json.
- You can add additional variables, but the specified variables have to be in
  your model. Otherwise, you will receive 0 points.
- You may import gurobipy, as well as json, networkx.
- Make sure to upload one file named agv.py.
- Using the bitshift or implication operator is not allowed.

## Model

**Input data**
- We have containers `j` at a arrival and destination location with timestamps.
  - given in the data.json as object `data["jobs"]`: 
    ```ts
     container_id : {
      "j_s": number, // arrival node 
      "j_t": number, // destination node 
      "j_r": number, // arrival time
      "j_d": number, // deadline
     }
    ```
- A Graph with `Node: location` and `Edges: streets between locations`
 - given in data.json as object `data["graph"]`, can be parsed directly into a
   weighted graph using nx


### Solution

**Graph-Model**

Use a time expanded graph with one plane for each timestep built using given data
- total: 0...kmax planes (timesteps)
- Node: `(location, timestep)`
  - note: for each container add a sink node with edges from `(destination,
    *)` with `*` for each time step. We can use this for the route finding.
- Edges: undirected `(node, node, weight)`
  - Edges for moving container: `((location, k), (next, k+w), w)`
  - Edges for waiting: `((location,k), (location,k+1), 1)` 

**MIP Model**

> ~~we may use G.neighbors() and filter by time to find in-coming / out-going edges~~
> We can convert the nx.Graph to an nx.DiGraph during graph building. This
> allows us to get in/out-edges simplier

Variables: X
- X: `X[v1,v2,j]: boolean`
  - Move container j from node to node (in graph model)
  - note: each container, can move from time `j_r` to `j_d`
  - use name in format `x_((0,1),(1,3))_4`

Constraint
- Constraint: paths (undirected) only used by one container at a time
  - `sum(X[(location, k),(next, k+w),j]) + sum(X[(next, k), (location, k+w), j]) <= 1` 
  - note: essentially walk over all edges for each container
- Constraint: at a location, there can only be one container at a time
  - `sum(X[(prev, k), (location, k+w), j]) <= 1`
  - note: walk over all all in-edges for each container, except for when
    location is the destination
- Constraint: find a path from start to finish
  - `sum(in-edges) + sum(out-edges) = {1,-1,0}`
  - for `(start, finish, intermediate)` nodes 
  - note: we introduce a finish node for each container `(-1337, -1337)` (with
    edge weight 0) which all `(destination, *)` will lead to. This node will be
    used as target.

Optimizer: Minimize total time steps for all containers
  - `sum(X[v1,v2,*] * timediff)` over all containers
  - timediff: weight of edge (v1,v2)
  - since the last timestep will have an edge of weight 0, this should be fine!
