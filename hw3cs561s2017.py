import copy
import itertools


def main():

    global queries
    queries = []

    global network
    network = dict()

    global conditionalQueries
    conditionalQueries = []

    global eUQueries
    eUQueries = []

    global mEUQueries
    mEUQueries = []

    global order
    order = []

    global dNodes
    dNodes = []

    global solution
    solution = dict()

    infile = open("input.txt", "r")
    obtainQueries(infile)
    buildNetwork(infile)
    #print network
    obtainConditionalQueries()
    obtainEUQueries()
    obtainMEUQueries()
    solvePQueries()
    solveEUQueries()
    solveMEUQueries()
    infile.close()

    opfile = open("output.txt", "w")
    for i in range(0, len(queries)):
        if i == len(queries) - 1:
            opfile.write(solution[queries[i]])
        else:
            opfile.write(solution[queries[i]]+"\n")
        #print solution[queries[i]]
    opfile.close()


def obtainQueries(infile):

    for line in infile:
        if line.strip() == '******':
            break
        #print line.strip()
        solution[line.strip()] = ""
        queries.append(line.strip())


def obtainConditionalQueries():

    for i in range(0, len(queries)):
        if queries[i][0] == 'P':
            conditionalQueries.append(queries[i])


def obtainEUQueries():

    for i in range(0, len(queries)):
        if queries[i][0] == 'E':
            eUQueries.append(queries[i])


def getParent(m):

    if len(m) == 0:
        return m
    else:
        m.remove(m[0])
        return m


def getChildren():

    for key, value in network.iteritems():
        if len(network[key]['parent']) == 0:
            g = 1  # Do nothing
        else:
            for j in range(0, len(network[key]['parent'])):
                network[network[key]['parent'][j]]['children'].append(key)


def arrangeTable():

    for key, value in network.iteritems():
        dtable = dict()
        node = key

        for f in range(0, len(network[node]['table'])):
            v = network[node]['table'][f][0]
            del network[node]['table'][f][0]

            for g in range(0, len(network[node]['table'][f])):
                if network[node]['table'][f][g] == '+':
                    network[node]['table'][f][g] = True
                elif network[node]['table'][f][g] == '-':
                    network[node]['table'][f][g] = False
            dtable[tuple(network[node]['table'][f])] = v

        network[node]['table'] = dtable


def buildNetwork(infile):

    for line in infile:

        temp = dict()
        prob = -1

        m = line.strip().split()
        node = m[0]
        order.append(node)
        m.remove(node)

        # Assign parents & children
        parent = getParent(m)
        temp['parent'] = parent
        temp['children'] = []

        # Assign probability
        if len(parent) == 0:
            for line1 in infile:
                prob = line1.strip().split()
                if prob == "decision":
                    prob = "decision"
                break
            temp['prob'] = prob
        else:
            temp['prob'] = prob

        # Assign table
        table = []
        for line2 in infile:
            if line2.strip() == "******":
                break

            if line2.strip() == "***":
                break
            t = line2.strip().split()
            table.append(t)
        temp['table'] = table

        # Add to Network
        network[node] = temp

    getChildren()
    arrangeTable()

    if order[0] == "utility":
        del order[0]


def normalize(p):

    sum = p[0] + p[1]
    x = p[0]/sum
    y = p[1]/sum
    return [x, y]


def removeDecisionNodes():

    for key, value in network.iteritems():
        l = ["decision"]
        if network[key]['prob'] == l and key in order:
            dNodes.append(key)
            order.remove(key)


def solvePQueries():

    for i in range(0, len(conditionalQueries)):
        evidence = True
        #print "**** Solving", conditionalQueries[i], "****"
        q = conditionalQueries[i]

        # Separate Query/Evidence Variables
        if '|' in q:
            qv = q[2:-1].split("|")[0].strip()
            ev = q[2:-1].split("|")[1].strip()
        else:
            qv = q[2:-1].strip()
            ev = []
            evidence = False

        # Checking Query Variables
        if ',' in qv:
            qv = qv.split(",")
        else:
            qv = [qv]
        for j in range(0, len(qv)):
            qv[j] = qv[j].strip()


        # Checking Evidence Variables
        if evidence:
            if ',' in ev:
                ev = ev.split(",")
            else:
                ev = [ev]
        for j in range(0, len(ev)):
            ev[j] = ev[j].strip()

        p = callEnumeration(qv, ev)
        solution[conditionalQueries[i]] = "%.2f" % round(p, 2)
        #print "%.2f" % round(p, 2)


def solveEUQueries():

    for i in range(0, len(eUQueries)):
        evidence = True
        #print "**** Solving", eUQueries[i], "****"
        q = eUQueries[i]

        # Separate Query/Evidence Variables
        if '|' in q:
            qv = q[3:-1].split("|")[0].strip()
            ev = q[3:-1].split("|")[1].strip()
        else:
            qv = q[3:-1].strip()
            ev = []
            evidence = False

        # Checking Query Variables
        if ',' in qv:
            qv = qv.split(",")
        else:
            qv = [qv]
        for j in range(0, len(qv)):
            qv[j] = qv[j].strip()


        # Checking Evidence Variables
        if evidence:
            if ',' in ev:
                ev = ev.split(",")
            else:
                ev = [ev]
        for j in range(0, len(ev)):
            ev[j] = ev[j].strip()

        p = prepareForEnumeration(qv, ev)
        solution[eUQueries[i]] = str(int(round(p)))
        #print int(round(p))


def setParentValue(t, i, v):

    u = []
    for s in range(0, len(t)):
        if t[s][i] == v:
            u.append(t[s])
    return u


def prepareForEnumeration(qv, ev):

    while len(qv) > 0:
        ev.append(qv.pop())
    actualParents, dec, normalParents, decisionParents = network['utility']['parent'], ['decision'], [], []

    for i in range(0, len(actualParents)):
        if network[actualParents[i]]['prob'] != dec:
            normalParents.append(actualParents[i])
        else:
            decisionParents.append(actualParents[i])

    t = list(itertools.product([False, True], repeat=len(actualParents)))

    for i in range(0, len(actualParents)):
        if actualParents[i] in decisionParents:
            for j in range(0, len(ev)):
                if ev[j].split("=")[0].strip() == actualParents[i]:
                    if ev[j].split("=")[1].strip() == "+":
                        t = setParentValue(t, i, True)
                    else:
                        t = setParentValue(t, i, False)

    p = 0
    for i in range(0, 2**len(normalParents)):
        l = []
        for j in range(0, len(normalParents)):
            if t[i][j]:
                sign = '+'
            else:
                sign = '-'
            l.append(normalParents[j]+" = "+sign)
        evi = copy.deepcopy(ev)
        p += callEnumeration(l, evi) * float(network['utility']['table'][t[i]])

    return p


def obtainMEUQueries():

    for i in range(0, len(queries)):
        if queries[i][0] == 'M':
            mEUQueries.append(queries[i])


def solveMEUQueries():

    for i in range(0, len(mEUQueries)):
        evidence = True
        #print "**** Solving", mEUQueries[i], "****"
        q = mEUQueries[i]

        # Separate Query/Evidence Variables
        if '|' in q:
            qv = q[4:-1].split("|")[0].strip()
            ev = q[4:-1].split("|")[1].strip()
        else:
            qv = q[4:-1].strip()
            ev = []
            evidence = False

        # Checking Query Variables
        if ',' in qv:
            qv = qv.split(",")
        else:
            qv = [qv]
        for j in range(0, len(qv)):
            qv[j] = qv[j].strip()

        # Checking Evidence Variables
        if evidence:
            if ',' in ev:
                ev = ev.split(",")
            else:
                ev = [ev]
        for j in range(0, len(ev)):
            ev[j] = ev[j].strip()

        t = list(itertools.product(['+', '-'], repeat=len(qv)))
        p = []

        for j in range(0, 2**len(qv)):
            l = []
            for k in range(0, len(qv)):
                l.append(qv[k]+" = "+t[j][k])
            ev1 = copy.deepcopy(ev)
            p.append(prepareForEnumeration(l, ev1))
        #print p
        maxIndex, max = 0, p[0]
        for k in range(len(p)):
            if p[k] > max:
                max, maxIndex = p[k], k

        s = ""
        for k in range(0, len(qv)):
            s += t[maxIndex][k] + " "
        s += str(int(round(max)))
        solution[mEUQueries[i]] = s
        #print s


def callEnumeration(qv, ev):

    X = []  # For Query Variables
    e = dict()  # For Evidence Variables

    # Process Evidence
    for k in range(0, len(ev)):
        e[ev[k].split("=")[0].strip()] = ev[k].split("=")[1].strip()
    for key, value in e.iteritems():
        if e[key] == '+':
            e[key] = True
        if e[key] == '-':
            e[key] = False
    # Process Query Variables
    for j in range(0, len(qv)):
        X.append(qv[j].strip().split("=")[0].strip())

    p, q = 1.0, len(X) - 1
    while len(qv) > 0:

        a = qv.pop()
        variable = str(a).split("=")[0].strip()
        value = str(a).split("=")[1].strip()
        if value == "+":
            value = True
        elif value == "-":
            value = False
        t = eliminationASK(X[q], e)
        t = normalize(t)
        if value:
            p *= float(t[1])
        else:
            p *= float(t[0])

        X.pop()
        e[variable] = value
        q -= 1

    return p


def parentProb(y, e):

    if network[y]['prob'] == -1:
        parentsInE = []
        for i in range(0, len(network[y]['parent'])):
            parentsInE.append(e[network[y]['parent'][i]])
        parentsInE = tuple(parentsInE)
        if e[y]:
            z = float(network[y]['table'][parentsInE])
        else:
            z = 1 - float(network[y]['table'][parentsInE])
    else:
        if e[y]:
            z = float(network[y]['prob'][0])
        else:
            z = 1 - float(network[y]['prob'][0])
    return z


def removeEliminated(vars, elim):

    v = []
    for i in range(0, len(order)):
            if vars[i] not in elim:
                v.append(vars[i])
    return v


def removeNotEliminatedChildren(vars, elim):

    v = []
    for i in range(0, len(vars)):
        children = network[vars[i]]['children']
        flag = True
        for j in range(0, len(children)):
            if children[j] in elim:
                flag = True
            else:
                flag = False
                break

        if flag is True:
            v.append(vars[i])
    return v


def eliminationASK(X, e):
    f, elim, variables, h = [], [], [], 0
    vars = copy.deepcopy(order)

    while len(elim) < len(order):

        variables = removeEliminated(vars, elim)
        variables = removeNotEliminatedChildren(variables, elim)
        factorVariables = dict()

        for v in variables:
            temp = []
            parents = network[v]['parent']
            for p in parents:
                if p not in e:
                    temp.append(p)
            if v not in e:
                temp.append(v)
            factorVariables[v] = temp

        h = sorted(factorVariables.keys(), key=lambda j: (len(factorVariables[j]), j))[0]

        if len(factorVariables[h]) > 0:
            d = getFactors(h, factorVariables, e)
            f.append(d)

        if h not in e and h != X:
            f = getSum(h, f)

        elim.append(h)

        for fact in f:
            temp = dict()
            for o in list(itertools.product([False, True], repeat=len(fact[0]))):
                temp2 = zip(fact[0], o)
                for k in temp2:
                    temp[k[0]] = k[1]

    if len(f) > 1:
        r, g = f[0], f[1:]
        for j in range(0, len(g)):
            r = pointwise(r, g[j])
    else:
        r = f[0]

    f, t = tuple([False]), tuple([True])
    fValue, tValue = r[1][f], r[1][t]
    return fValue, tValue


def getFactors(c, factors, e):

    parents, v = factors[c], copy.deepcopy(network[c]['parent'])
    v.append(c)

    et, a = {}, {}
    for o in list(itertools.product([False, True], repeat=len(v))):
        flag = False
        for t in zip(v, o):
            if t[0] in e and e[t[0]] != t[1]:
                flag = True
                break
            a[t[0]] = t[1]

        if flag:
            continue

        t = tuple()
        for i in range(0, len(parents)):
            t = t + (a[parents[i]],)

        p = parentProb(c, a)
        et[t] = p

    return (parents, et)


def prepareForGetSum(v, factors):

    fVar, position = [], []

    for i in range(0, len(factors)):
        if v in factors[i][0]:
            position.append(i)
            fVar.append(factors[i])

    if len(fVar) > 1:
        temp = position[::-1]
        for j in temp:
            factors.remove(factors[j])
        r = fVar[0]

        temp = fVar[1:]
        for j in range(0, len(temp)):
            r = pointwise(r, temp[j])
        factors.append(r)

    return factors


def getSum(v, factors):

    factors = prepareForGetSum(v, factors)

    for i in range(0, len(factors)):
        alphas = factors[i][0]
        for a in range(0,len(alphas)):
            if v == alphas[a]:

                newVars = alphas[:a] + alphas[a+1:]
                temp2 = dict()

                for row in factors[i][1]:

                    key = tuple(list(row)[:a] + list(row)[a+1:])
                    row = list(row)
                    row[a] = True
                    p1 = factors[i][1][tuple(row)]
                    row[a] = False
                    p2 = factors[i][1][tuple(row)]
                    temp2[key] = p1 + p2

                factors[i] = (newVars, temp2)
                if len(newVars) == 0:
                    factors.remove(factors[i])
    return factors


def pointwise(f1, f2):

    result, a, v, temp, p = dict(), dict(), [], [], 0.0
    first, second = f1[0], f2[0]
    for i in first:
        temp.append(i)
    for i in second:
        temp.append(i)
    for i in temp:
        if i not in v:
            v.append(i)
    v = list(set(v))

    for o in list(itertools.product([True, False], repeat=len(v))):
        for t in zip(v, o):
            a[t[0]] = t[1]

        t1, t2, t3 = [], [], []

        for j in range(0, len(v)):
            t1 = t1 + [a[v[j]]]

        for j in range(0, len(first)):
            t2 = t2 + [a[first[j]]]

        for j in range(0, len(second)):
            t3 = t3 + [a[second[j]]]

        p = f1[1][tuple(t2)] * f2[1][tuple(t3)]

        result[tuple(t1)] = p

    return (v, result)


if __name__ == "__main__": main()

