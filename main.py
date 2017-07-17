import sys

class Clause:
    def __init__(self):
        self.origin = {}
        self.size = 0
        self.istautology = False
        self.removed = []
        self.true_by_var = 0

# add a literal into a clause, true means positive
    def add_var(self, v):
        if self.istautology:
            return
        if v < 0:
            if -v in self.origin:
                if self.origin[-v] == True:
                    self.istautology = True
            else:
                self.origin[-v] = False
                self.size += 1
        else:
            if v in self.origin:
                if self.origin[v] == False:
                    self.istautology = True
            else:
                self.origin[v] = True
                self.size += 1

    def restore_var(self, v, assign):
        if v not in self.origin:
            self.origin[v] = assign
            self.size += 1

    def del_var(self, v):
        if v in self.origin:
            del self.origin[v]
            self.size -= 1



class Formula:
    def __init__(self):
        self.clauses = set()
        self.num_cls = 0

        self.vars = {}
        self.num_var = 0
        self.occ_pos = {}
        self.occ_neg = {}

        self.units = {}

    def set_var(self, n):
        self.vars = dict((v, None) for v in range(1, n+1))
        self.num_var = n
        self.occ_pos = dict((v, set()) for v in range(1, n+1))
        self.occ_neg = dict((v, set()) for v in range(1, n+1))

    def add_clause(self, cls):
        if cls.istautology:
            return
        for k,v in cls.origin:
            if v:
                self.occ_pos[k].add(cls)
            else:
                self.occ_neg[k].add(cls)
        self.clauses.add(cls)
        self.num_cls += 1

    def del_clause(self, cls):
        if cls in self.clauses:
            self.clauses.remove(cls)
            self.num_cls -= 1

    def restore_clause(self, cls):
        if cls not in self.clauses:
            self.clauses.add(cls)
            self.num_cls += 1

    def restore_assigned(self, cur_assigned):
        for v, assign in cur_assigned:
            if assign:
                for pcls in self.occ_pos[v]:
                    if pcls.true_by_var == v:
                        pcls.true_by_var = 0
                        self.restore_clause(pcls)
                for ncls in self.occ_neg[v]:
                    ncls.restore_var(v, assign)
            else:
                for ncls in self.occ_neg[v]:
                    if ncls.true_by_var == v:
                        ncls.true_by_var = 0
                        self.restore_clause(ncls)
                for pcls in self.occ_pos[v]:
                    pcls.restore_var(v, assign)

    def try_assign(self, unit, assign):
        # if the return value is false
        # it means that bcp produces a contradiction
        # newly found units is in self.units
        if assign:
            for ncls in self.occ_neg[unit]:
                if ncls.size == 1:
                    return False
                else:
                    ncls.del_var(unit)
                    # find new unit clause
                    if ncls.size == 1:
                        for nv,nassign in ncls.origin:
                            if nv in self.units:
                                if nassign != self.units[nv]:
                                    return False
                            else:
                                self.units[nv] = nassign
            for pcls in self.occ_pos[unit]:
                if pcls.true_by_var == 0:
                    pcls.true_by_var = unit
                    self.del_clause(pcls)
        else:
            for pcls in self.occ_pos[unit]:
                if pcls.size == 1:
                    return False
                else:
                    pcls.del_var(unit)
                    # find new unit clause
                    if pcls.size == 1:
                        for pv,passign in pcls.origin:
                            if pv in self.units:
                                if passign != self.units[pv]:
                                    return False
                                else:
                                    self.units[pv] = passign
            for ncls in self.occ_neg[unit]:
                if ncls.true_by_var == 0:
                    ncls.true_by_var = unit
                    self.del_clause(ncls)
        return True

    def solve(self):
        if self.num_cls == 0:
            return True

        cls = next(iter(self.clauses))

        cur_assigned = {}

        # if it is a unit clause
        if cls.size == 1:
            v,assign = cls.origin.popitem
            self.units[v] = assign
            while len(self.units) > 0:
                k,v = self.units.popitem()
                cur_assigned[k] = v
                if not self.try_assign(k, v):
                    self.restore_assigned(cur_assigned)
                    return False
            if self.solve():
                return True
            else:
                # restore clauses before backtrack
                self.restore_assigned(cur_assigned)
                return False
        else:
            for v,assign in cls.origin:
                if self.try_assign(v, assign) & self.solve():
                        return True
                else:
                    self.restore_assigned({v : assign})
                    if self.try_assign(v, ~assign) & self.solve():
                        return True
                    else:
                        self.restore_assigned({v : ~assign})
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
                for c in p:
                    ic = int(c)
                    if ic == 0:
                        form.add_clause(cls_tmp)
                    else:
                        cls_tmp.add_var(ic)
        tmps = f.readline()
    f.close()
    if form.solve():
        print 's SATISFIABLE'
    else:
        print 's UNSATISFIABLE'

if __name__ == "__main__":
    main()