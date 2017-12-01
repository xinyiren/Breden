import argparse
import copy

"""
======================================================================
  Complete the following function.
======================================================================
"""

def solve(num_wizards, num_constraints, wizards, constraints):
    """
    Write your algorithm here.
    Input:
        num_wizards: Number of wizards
        num_constraints: Number of constraints
        wizards: An array of wizard names, in no particular order
        constraints: A 2D-array of constraints, 
                     where constraints[0] may take the form ['A', 'B', 'C']i

    Output:
        An array of wizard names in the ordering your algorithm returns   


    num_wizards = 5
    num_constraints = 10
    wizards = ['A', 'D', 'C', 'B', 'E']
    constraints = [['A','B','C'], ['D','A','E'], ['A','B','D'], ['C','D','A'], ['C', 'E', 'B'],
                    ['E', 'D','B'], ['B', 'D', 'A'], ['C','A', 'E'], ['C', 'B', 'E'], ['E', 'D', 'C']]


    """
    super_special = []
    for i in range(len(constraints)):
        a = constraints[i]
        for j in range(i+1, len(constraints)):
            b = constraints[j]
            if three_similar(a,b):
                super_special += [(a,b)]
    ordered = []
    for i in super_special:
        if i[0][2] != i[1][2]:
            j = three_process(list(i[0]),list(i[1]))
        ordered += [j]

    a = set([])
    for i in ordered:
        a.add(i[1])

 


    
    neighbours = {v:[] for v in wizards}
    for i in constraints:
        a,b,c= i[0],i[1],i[2]
        neighbours[a].append(i)
        neighbours[b].append(i)
        neighbours[c].append(i)


    csp = CSP(num_wizards, wizards, constraints, neighbours)

    csp.first_prune_domain(ordered)

    semiresult = backtracking_search(csp)
    result = []

    for i in range(num_wizards):
        result = result + [list(semiresult.keys())[list(semiresult.values()).index(i)]]

    



    return result 

def three_similar(a,b):
    a, b= list(a), list(b)
    c = set(a + b)
    if len(c) == 3:
        return True
    return False
def three_process(a,b):
    result = [a[2],b[2]]
    for i in a:
        if i not in result:
            result = [a[2],i,b[2]]
    return result



class CSP:
    def __init__(self, num_wizards, wizards, constraints, neighbours):
        self.size = num_wizards
        self.var = wizards
        self.domains = {v:list(range(0, num_wizards)) for v in self.var}
        self.constraints = constraints  #constraints now is just the original constraints list
        self.reverse_domains = {i: [] for i in range(0,num_wizards)} # maybe using later
        self.neighbours = neighbours
        self.curr_domains = {}
        self.lcv = True
        self.mc = True
        self.mac = False
        self.fc = False

    def check_violation(self, var, value, assignment, neighbours):

        copy_assignment = copy.deepcopy(assignment)
        copy_assignment[var] = value

        def violate(assignment, constraint):
            a, b, c = assignment.get(constraint[0],None), assignment.get(constraint[1],None), assignment.get(constraint[2],None)
            if a != None and b != None and c != None:
                wrong_position = list(range(min(a,b), max(a,b) + 1))
                if c in wrong_position:
                    return True
                return False
            return False
        return count_if(lambda constraint: violate(copy_assignment, constraint), neighbours)









    def assign(self, var, val, assignment):
        """Add {var: val} to assignment; Discard the old value if any.
        Do bookkeeping for curr_domains and nassigns."""
        assignment[var] = val

        for v in self.var:
            if val in self.domains[v]:
                self.domains[v].remove(val)





    def unassign(self, var, assignment):
        """Remove {var: val} from assignment; that is backtrack.
        DO NOT call this if you are changing a variable to a new value;
        just call assign for that."""
        if var in assignment:
            val = assignment[var]
            # Reset the curr_domain to be the full original domain
            if self.curr_domains:
                self.curr_domains[var] = self.domains[var][:]
            del assignment[var]

            for v in self.var:
                self.domains[v].append(val)




    def first_prune_domain(self, special_constraints): #special constraints specifies (a,b,c) has to be in the order
        def find_category(constraint, exist):
            lib = exist[constraint[1]]
            if constraint[0] in lib[0] or constraint[2] in lib[0]:
                if constraint[2] not in lib[1] and constraint[0] not in lib[1]:
                    if constraint[2] in lib[0]:
                        exist[constraint[1]][1].append(constraint[0])  
                    else:
                        exist[constraint[1]][1].append(constraint[2])
                    return "right side minus one"
                return 'no action'
            elif constraint[0] in lib[1] or constraint[2] in lib[1]:
                if constraint[2] not in lib[0] and constraint[0] not in lib[0]:
                    if constraint[2] in lib[1]:
                        exist[constraint[1]][0].append(constraint[0])  
                    else:
                        exist[constraint[1]][0].append(constraint[2])
                    return "left side minus one"
                return 'no action'
            exist[constraint[1]][0].append(constraint[0]) 
            exist[constraint[1]][1].append(constraint[2]) 
            return 'minus both'


        

        already_considered = {v:list([[],[]]) for v in self.var} #to deal with (a,b,c) (a,b,e) etc.
        for constraint in special_constraints:
            if find_category(constraint, already_considered) == 'minus both':
                self.domains[constraint[1]] = self.domains[constraint[1]][1:len(self.domains[constraint[1]])-1]
            elif find_category(constraint, already_considered) == "left side minus one":
                self.domains[constraint[1]] = self.domains[constraint[1]][1:]
            elif find_category(constraint, already_considered) == 'right side minus one':
                self.domains[constraint[1]] = self.domains[constraint[1]][:len(self.domains[constraint[1]])-1]

        for i in self.var:
    
            for j in self.domains[i]:
                self.reverse_domains[j].append(i)
        


def backtracking_search(csp, mcv=False, lcv=False, fc=False, mac=False):
    """Set up to do recursive backtracking search. Allow the following options:
    mcv - If true, use Most Constrained Variable Heuristic
    lcv - If true, use Least Constraining Value Heuristic
    fc  - If true, use Forward Checking
    mac - If true, use Maintaining Arc Consistency.              [Fig. 5.3]
    >>> backtracking_search(australia)
    {'WA': 'B', 'Q': 'B', 'T': 'B', 'V': 'B', 'SA': 'G', 'NT': 'R', 'NSW': 'R'}
    """
    if fc or mac:
        csp.curr_domains, csp.pruned = {}, {}
        for v in csp.vars:
            csp.curr_domains[v] = csp.domains[v][:]
            csp.pruned[v] = []
    return recursive_backtracking({}, csp)
    

def recursive_backtracking(assignment, csp):
    """Search for a consistent assignment for the csp.
    Each recursive call chooses a variable, and considers values for it."""
    if len(assignment) == csp.size:
        return assignment
    var = select_unassigned_variable(assignment, csp)
    for val in order_domain_values(var, assignment, csp):
        if csp.check_violation(var, val, assignment, csp.neighbours[var]) == 0:
            csp.assign(var, val, assignment)
            result = recursive_backtracking(assignment, csp)
            if result is not None:
                return result
        csp.unassign(var, assignment)
    return None

def select_unassigned_variable(assignment, csp):
    "Select the variable to work on next.  Find"
    if csp.mc: # Most Constrained Variable
        unassigned = [v for v in csp.var if v not in assignment]
        return min(unassigned,
                     key = lambda var: -num_legal_values(csp, var, assignment))
    else: # First unassigned variable
        for v in csp.var:
            if v not in assignment:
                return v

def order_domain_values(var, assignment, csp):
    "Decide what order to consider the domain variables."
    if csp.curr_domains:
        domain = csp.curr_domains[var]
    else:
        domain = csp.domains[var][:]
    if csp.lcv:
        # If LCV is specified, consider values with fewer conflicts first
        key = lambda val: - csp.check_violation(var, val, assignment, csp.neighbours[var])
        domain.sort(key = key)
    while domain:
        yield domain.pop()

def num_legal_values(csp, var, assignment):
    if csp.curr_domains:
        return len(csp.curr_domains[var])
    else:
        return count_if(lambda val: csp.check_violation(var, val, assignment, csp.neighbours[var]) == 0,
                        csp.domains[var])
def count_if(func, values):
    return sum(1 if func(x) else 0 for x in values)





 

"""
======================================================================
   No need to change any code below this line
======================================================================
"""


def read_input(filename):
    with open(filename) as f:
        num_wizards = int(f.readline())
        num_constraints = int(f.readline())
        constraints = []
        wizards = set()
        for _ in range(num_constraints):
            c = f.readline().split()
            constraints.append(c)
            for w in c:
                wizards.add(w)

    wizards = list(wizards)
    return num_wizards, num_constraints, wizards, constraints


def write_output(filename, solution):
    with open(filename, "w") as f:
        for wizard in solution:
            f.write("{0} ".format(wizard))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Constraint Solver.")
    parser.add_argument("input_file", type=str, help="___.in")
    parser.add_argument("output_file", type=str, help="___.out")
    args = parser.parse_args()

    num_wizards, num_constraints, wizards, constraints = read_input(args.input_file)
    solution = solve(num_wizards, num_constraints, wizards, constraints)
    write_output(args.output_file, solution)
