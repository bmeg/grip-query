
import gripql
import networkx

def parseQuery(text):
    try:
        out = eval(str(text), {"V": gripql.query.Query(url="", graph="test").V}, {})
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
