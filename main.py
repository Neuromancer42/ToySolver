import sys

class Clause:
    def __init__(self):
        self.vars = {}
        self.istautology = False
        self.true_by_var = 0
        self.not_assigned = None

# add a literal into a clause, true means positive
    def add_var(self, v):
        if self.istautology:
            return
        if v < 0:
            if -v in self.vars:
                if self.vars[-v] == True:
                    self.istautology = True
            else:
                self.vars[-v] = False
        else:
            if v in self.vars:
                if self.vars[v] == False:
                    self.istautology = True
            else:
                self.vars[v] = True

class Formula:
    def __init__(self):
        self.clauses = set()

        self.occ = {}

        self.unit_by_dom = {0:{}}
        self.unit_to_dom = {}
        self.isparadox = False

        self.num_sat = 0
        self.unassigned = set()

    def set_var(self, n):
        self.unassigned = set(range(1, n+1))

    def add_clause(self, cls):
        if cls.istautology:
            return
        for var,assign in cls.vars.iteritems():
            if var not in self.occ:
                self.occ[var] = {True:set(), False:set()}
            self.occ[var][assign].add(cls)
        if len(cls.vars) == 1:
            var,assign = next(cls.vars.iteritems())
            if not self.add_units(var, assign, 0):
                self.isparadox = True
        cls.not_assigned = set(cls.vars.keys())
        self.clauses.add(cls)

    # the unit clause is caused by assignment of dom
    def add_units(self, var, assign, dom):
        if dom not in self.unit_by_dom:
            self.unit_by_dom[dom] = {}
        if var in self.unit_to_dom:
            d = self.unit_by_dom[var]
            return (self.unit_by_dom[d][var] == assign)
        else:
            self.unit_to_dom[var] = dom
            self.unit_by_dom[dom][var] = assign
            return True

    def try_assign(self, var, assign):
        # first, handle all unsat yet clauses
        new_units = {}
        iscapbale = True
        for cls in self.occ[var][not assign]:
            cls.not_assigned.remove(var)
            if len(cls.not_assigned) == 1:
                v = next(iter(cls.not_assigned))
                if v in self.unit_to_dom:
                    d = self.unit_to_dom[v]
                    if self.unit_by_dom[d][v] != cls.vars[v]:
                        iscapbale = False
                        break
                else:
                    new_units[v] = cls.vars[v]
        # if not assignable, restore modified clauses
        if not iscapbale:
            for cls in self.occ[var][not assign]:
                cls.not_assigned.add(var)
        else:
            # second, handle all sat clauses
            for cls in self.occ[var][assign]:
                for v,a in cls.vars.iteritems():
                    if v != var:
                        self.occ[v][a].remove(cls)
            self.num_sat += len(self.occ[var][assign])
            for v in new_units:
                self.unit_to_dom[v] = var
            self.unit_by_dom[var] = new_units
            self.unassigned.remove(var)

        return iscapbale

    def restore_assigned(self, l):
        for v,a,d in reversed(l):
            for cls in self.occ[v][a]:
                for ov,oa in cls.vars.iteritems():
                    if ov != v:
                        self.occ[ov][oa].add(cls)
            for cls in self.occ[v][not a]:
                cls.not_assigned.add(v)

            self.unassigned.add(v)
            self.num_sat -= len(self.occ[ov][oa])

            # if the assignment generate units or is a unit
            # the records need cleanign
            if d != -1:
                self.unit_to_dom[v] = d
            if v in self.unit_by_dom:
                for sv in self.unit_by_dom[v]:
                    del self.unit_to_dom[sv]
                del self.unit_by_dom[v]

    def solve(self):
        cur_assigned = []
        while len(self.unit_to_dom) > 0:
            var,dom = self.unit_to_dom.popitem()
            assign = self.unit_by_dom[dom][var]
            if self.try_assign(var, assign):
                cur_assigned.append((var, assign, dom))
            else:
                self.unit_to_dom[var] = dom
                self.restore_assigned(cur_assigned)
                return False

        if self.num_sat == len(self.clauses):
            return True

        max_num = 0
        to_assign = 0
        for v in self.unassigned:
            vl = len(self.occ[v][True]) + len(self.occ[v][False])
            if vl > max_num:
                to_assign = v
                max_num = vl

        if to_assign > 0:
            if self.try_assign(to_assign, True):
                if self.solve():
                    return True
            self.restore_assigned([(to_assign, True, -1)])

            if self.try_assign(to_assign, False):
                if self.solve():
                    return True
            self.restore_assigned([(to_assign, False, -1)])

        self.restore_assigned(cur_assigned)
        return False

def main():
    format = ""
    num_var = 0
    num_cls = 0
    filename = ""

    if len(sys.argv) != 2:
        print "Error: Arguments mismatch!\nUsage: python main.py <filename>.\n"
        exit(-1)
    else:
        filename = sys.argv[1]
    f = open(filename, 'r')
    tmps = f.readline()
    cls_tmp = Clause()
    form = Formula()
    while (tmps != ''):
        if (tmps[0] != 'c'):
            if (tmps[0] == 'p'):
                prob = tmps.split()
                if prob[1] != 'cnf':
                    print "Error: Problem fromat is not CNF"
                    exit(-1)
                else:
                    num_var = int(prob[2])
                    num_cls = int(prob[3])
                    form.set_var(num_var)
            else:
                p = tmps.split()
                ic = 0
                for c in p:
                    ic = int(c)
                    if ic == 0:
                        form.add_clause(cls_tmp)
                        cls_tmp = Clause()
                    else:
                        cls_tmp.add_var(ic)
                if ic != 0:
                    form.add_clause(cls_tmp)
        tmps = f.readline()
    f.close()
    if form.isparadox:
        print 's UNSATISFIABLE'
    else:
        if form.solve():
            print 's SATISFIABLE'
        else:
            print 's UNSATISFIABLE'

if __name__ == "__main__":
    main()