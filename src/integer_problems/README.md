# more problems

- Knapsack: maximize profits under given capacity constraint
  - $v_i$ value of item i, number
  - $x_i$ use item i, binary
  - $a_i$ weight of item i, number
  - $b$ capacity of knapsack
  - goal: maximize sum of $v_i*x_i$
  - conditions: 
    - sum of $a_i*x_i \leq b$ - stay in capacity

- Bin Packing Problem: pack items in minimum number of bins respecting bin capacity
  - $y_i$ use bin i, binary
  - $x_{ij}$ pack item i into bin j, binary
  - $a_i$ size of item i, number
  - $b$ bin capacity, number
  - goal: minimize sum of $y_i$
  - conditions:
    - sum of $x_{ij} = 1$ - pack every item
    - $a_{i} * x_{ij} \leq b * y_j$  - respect bin capacity

- Cutting Stock Problem: cut minimum number of rolls into items such that demands are satisfied
  - $y_i$ use roll i, binary
  - $x_{ij}$ how often cut item i from roll j
  - $a$ length of item 
  - $b$ length of roll 
  - $d$ demand of item 
  - goal: minimize sum of $y_i$
  - conditions:
    - sum of $x_{ij} \geq d_i$
    - sum of $a_i * x_{ij} \leq b * y_i$

- Facility Location: open Facility and assign client to opened Facilities with minimal cost
  - $y$ open facility j, binary
  - $x$ assign client i to facility j, binary
  - $c$ cost of assigning client i to facility j, number
  - $f$ cost of opening a facility i, number
  - goal: min sum of $f_i$ + sum of $c_{ij} * x_{ij}$
  - conditions:
    - $x_{ij} \leq y_{j}$ - facility must be opened for assignment
    - sum of $x_{ij} = 1$ - assign each client

- Parallel Machine Scheduling: assign job to machines with start time (Gantt chart) least total time
  - $x$ assign job i to machine k
  - $C$ timespan until all jobs are done
  - $p$ processing time of job i
  - goal: minmax $C$
  - conditions: 
    - $C \geq 0$ 
    - sum of $p_i * x_{ik} \leq C$ - timespan of the jobs
    - sum of $x_{ik} = 1$ - assing every job
  - note: it's a bin packing problem where we minmax bin sizes! 
  - note: for overlapping job constraints, order constraints. Use a graph!

- Parallel Scheduling with Precedence: in addition to above
  - $t$ start time of job i, number
  - $u$ disjunction operator stating job i comes before job j, binary, see Big M Techniques
  - goal: minmax $C$
  - conditions:
    - $t_i + p_i \leq t_j$  - job precedence: i must be before j
    - $t_i + p_i \leq t_j + (1-u_{ij}) * M$ - disjunction, job is either before
    - $t_j + p_j \leq t_i + u_{ij}) * M$ - disjunction, or after another job
    - $t_j + p_j \leq C$  - timespan
    - $C \geq 0$
    - $t_j \geq 0$  - job start time
  - note: solver may directly solve Big M constraint 
    - `model.addConstr((u[i,j] == 1) >> (t[i] + p[i] <= t[j]))`
  - note: we may also want to include deadlines, and earliest possible start
  - note: using discrete time slots is also possible (see big M Techniques)

## Techniques

- Linearization of min, max
  - min: $y \leq x_i$ y is smaller then all values
  - max: $y \geq x_i$ y is bgigger then all values
- Linearization of minmax, maxmin
  - use min, max linearization
  - minmax: min y with $y \geq x_i$
  - maxmin: max y with $y \leq x_i$
- Big M Constraints:
  - given some equivalence `u = 1 -> T` and `u = 0 -> Z`
  - we can linearize it as: Choose a large M (large enough for problem)
    - T: $t_i + p_i \leq t_j$ -> $t_i + p_i \leq t_j + M * (1-u)$ 
    - Z: $t_j + p_j \leq t_i$ -> $t_j + p_j \leq t_i + M * u$ 
  - sometimes (e.g. in time domain) we may linearize time in discrete slots with a variable e.g. $x_{jt}$ (job j starts at time t) to avoid using big M


