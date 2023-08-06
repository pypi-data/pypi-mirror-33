from enum import Enum

class SolverType(Enum):
    CDD = 0
    Clp = 1
    OSQP = 2
    Cbc = 3
    GLPK = 4
    CSDP = 5
    ECOS = 6
    SCS = 7
    SDPA = 8
    Pajarito = 9
    NLopt = 10
    Ipopt = 11
    Bonmin = 12
    Couenne = 13

    CPLEX = 14
    Gurobi = 15
    FICO_Xpress = 16
    Mosek = 17
    Artelys_Knitro = 18
    SCIP = 19

    def solver_name(self, solver_type):
        # Note: User regular expression to replace '_' with ' '
        if solver_type == FICO_Xpress or solver_type == Artelys_Knitro:
            return solver_type.name.replace('_', ' ') + '.jl'
        else:
            return solver_type.name + '.jl'

    def solver_object_name(self, solver_type):
        if solver_type == Ipopt:
            return 'IpoptSolver'
        else:
            return solver_type.name
