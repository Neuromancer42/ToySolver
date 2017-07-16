import sys

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
        tmps = f.readline()
    f.close()
    print "%s %s" % (num_var, num_cls)

if __name__ == "__main__":
    main()