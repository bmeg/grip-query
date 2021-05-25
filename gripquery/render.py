
import gripql
import networkx


class gripStub:
    def and_(self, *args, **kwargs):
        return gripql.and_(*args, **kwargs)
    def or_(self, *args, **kwargs):
        return gripql.or_(*args, **kwargs)
    def not_(self, *args, **kwargs):
        return gripql.not_(*args, **kwargs)
    def eq(self, *args, **kwargs):
        return gripql.eq(*args, **kwargs)
    def neq(self, *args, **kwargs):
        return gripql.neq(*args, **kwargs)
    def gt(self, *args, **kwargs):
        return gripql.gt(*args, **kwargs)
    def gte(self, *args, **kwargs):
        return gripql.gte(*args, **kwargs)
    def lt(self, *args, **kwargs):
        return gripql.lt(*args, **kwargs)
    def lte(self, *args, **kwargs):
        return gripql.lte(*args, **kwargs)
    def inside(self, *args, **kwargs):
        return gripql.inside(*args, **kwargs)
    def outside(self, *args, **kwargs):
        return gripql.outside(*args, **kwargs)
    def between(self, *args, **kwargs):
        return gripql.between(*args, **kwargs)
    def within(self, *args, **kwargs):
        return gripql.within(*args, **kwargs)
    def without(self, *args, **kwargs):
        return gripql.without(*args, **kwargs)
    def contains(self, *args, **kwargs):
        return gripql.contains(*args, **kwargs)
    def term(self, *args, **kwargs):
        return gripql.term(*args, **kwargs)
    def histogram(self, *args, **kwargs):
        return gripql.histogram(*args, **kwargs)
    def percentil(self, *args, **kwargs):
        return gripql.percentil(*args, **kwargs)

def validateQuery(text):
    try:
        out = eval(str(text), {"V": gripql.query.Query(url="", graph="test").V, "gripql" : gripStub()}, {})
    except Exception as e:
        print(e)
        return False
    if isinstance(out, gripql.query.Query):
        return True
    return False

def parseQuery(text):
    try:
        out = eval(str(text), {"V": gripql.query.Query(url="", graph="test").V, "gripql" : gripStub()}, {})
    except:
        return None
    if isinstance(out, gripql.query.Query):
        return out
    return None

def parsePartialQuery(text):
    if text is None:
        return None
    while len(text) > 3:
        o = parseQuery(text)
        if o is not None:
            return o
        tmp = text.split(".")
        if len(tmp) == 1:
            return None
        text = ".".join(tmp[:-1])

def schemaGraphColor(schema, query):
    if query is None:
        return []
    G = networkx.MultiDiGraph()
    for v in schema['vertices']:
        G.add_node(v['gid'], steps=[])
    for e in schema['edges']:
        G.add_edge(e['from'], e['to'], steps=[], label=e['label'])
    queryData = query.to_dict()['query']
    if queryData == [{"v":[]}]:
        for n in G.nodes:
            G.nodes[n]["steps"] = []
    if len(queryData) > 1 and 'v' in queryData[0]:
        step = 1
        if 'hasLabel' in queryData[1]:
            for l in queryData[1]['hasLabel']:
                if l in G.nodes:
                    G.nodes[l]['steps'].append(step)
                    G.nodes[l]['current'] = True
            step = 2
        while step < len(queryData):
            if 'out' in queryData[step] or 'both' in queryData[step]:
                for e in G.edges:
                    if step-1 in G.nodes[e[0]]['steps']:
                        if len(queryData[step]['out']) == 0 or G.edges[e]['label'] in queryData[step]['out']:
                            G.nodes[e[1]]['steps'].append(step)
            if 'in' in queryData[step] or 'both' in queryData[step]:
                for e in G.edges:
                    if step-1 in G.nodes[e[1]]['steps']:
                        if len(queryData[step]['in']) == 0 or G.edges[e]['label'] in queryData[step]['in']:
                            G.nodes[e[0]]['steps'].append(step)
            step += 1

    out = []
    for n in G.nodes:
        if len(G.nodes[n]['steps'])>0:
            out.append(n)
    return out


def schemaToGraph(schema):
    G = networkx.MultiDiGraph()
    for v in schema['vertices']:
        G.add_node(v['gid'], steps=[])
    for e in schema['edges']:
        G.add_edge(e['from'], e['to'], steps=[], label=e['label'])
    return G

def queryOutLabel(schemaGraph, query):
    curLabel = None
    queryData = query.to_dict()['query']
    if len(queryData) > 1 and 'v' in queryData[0]:
        if 'hasLabel' in queryData[1] and len(queryData[1]['hasLabel']) == 1:
            l = queryData[1]['hasLabel'][0]
            if l in schemaGraph.nodes:
                curLabel = l
        if len(queryData) > 2:
            for s in queryData[2:]:
                if curLabel is not None:
                    if "out" in s:
                        edges = []
                        for src, dst, data in schemaGraph.out_edges(curLabel, data=True):
                            if len(s["out"]) == 0 or data['label'] in s["out"]:
                                edges.append([src,dst])
                        if len(edges) == 1:
                            curLabel = edges[0][1]
                        else:
                            curLabel = None
                    elif "in" in s:
                        edges = []
                        for src, dst, data in schemaGraph.in_edges(curLabel, data=True):
                            if len(s["in"]) == 0 or data['label'] in s["in"]:
                                edges.append([src,dst])
                        if len(edges) == 1:
                            curLabel = edges[0][0]
                        else:
                            curLabel = None
                    # TODO handle both, inE, outE and bothE
    return curLabel

def queryContinuePath(schemaGraph, curLabel, dstLabel):
    try:
        p = networkx.shortest_path(schemaGraph.to_undirected(), curLabel, dstLabel)
        returnCmd = ""
        for i in range(len(p)-1):
            #print(p[i], p[i+1])
            #print(schemaGraph.out_edges(p[i], data=True), schemaGraph.in_edges(p[i], data=True))
            extendCmd = None
            for src, dst, data in schemaGraph.out_edges(p[i], data=True):
                if extendCmd is None:
                    if dst == p[i+1]:
                        extendCmd = '.out("%s")' % (data["label"])
            for src, dst, data in schemaGraph.in_edges(p[i], data=True):
                if extendCmd is None:
                    if src == p[i+1]:
                        extendCmd = '.in_("%s")' % (data["label"])
            returnCmd += extendCmd
        return returnCmd
    except networkx.exception.NetworkXNoPath as e:
        pass
    return ""
