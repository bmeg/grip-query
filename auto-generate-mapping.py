#!/usr/bin/env python

import sys
import json
import gripql

conn = gripql.Connection("http://localhost:8201")

name = sys.argv[1]
source = sys.argv[2]

vertices = []
edges = []
for t in conn.listTables():
    if t['source'] == source:
        if len(t['linkMap']) == 0:
            v = {"gid" : t['name'] + ":", "label" : t['name'], "data" : {"collection" : t['name'], "source" : t["source"]}}
            #print(v)
            vertices.append(v)
        else:
            if len(t['linkMap']) == 2:
                a, b = t['linkMap'].keys()
                aLabel = a[2:]
                bLabel = b[2:]
                aE = {
                    "gid" : "%s:%s:%s:" % (t['name'], aLabel, bLabel),
                    "from" : t['linkMap'][a] + ":",
                    "to" : t['linkMap'][b] + ":",
                    "label" : bLabel,
                    "data" : {
                        "source" : t['source'],
                        "collection" : t["name"],
                        "fromField" : a,
                        "toField" : b
                    }
                }
                bE = {
                    "gid" : "%s:%s:%s:" % (t['name'], bLabel, aLabel),
                    "to" : t['linkMap'][a] + ":",
                    "from" : t['linkMap'][b] + ":",
                    "label" : aLabel,
                    "data" : {
                        "source" : t['source'],
                        "collection" : t["name"],
                        "fromField" : b,
                        "toField" : a
                    }
                }
                edges.append(aE)
                edges.append(bE)

print(json.dumps([{
    "graph" : name,
    "vertices" : vertices,
    "edges" : edges
}], indent=4))
