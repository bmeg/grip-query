#!/usr/bin/env python

import json
import gripql
import networkx
from gripquery.render import parsePartialQuery, schemaGraphColor

GRIP="https://bmeg.io"
CRED="bmeg_credentials.json"
graph="rc5"

with open("schema.json") as handle:
    schema = json.loads(handle.read())

tests = [
    {"query" : 'V().hasLabel("Case").out("samples")', "result" : ['Case', 'Sample'] },
    {"query" : 'V()', "result" : [] }, # FIXME: Is this the desired behavior ?
    {"query" : 'V().hasLabel("Case").out()', "result" : ['Case', 'Phenotype', 'Sample', 'Compound', 'Project'] },
    {"query" : 'V().hasLabel("Case").in_()', "result" : ['Case', 'Phenotype', 'Sample', 'Compound', 'Project'] },
    {"query" : 'V().hasLabel("Case").ou', "result" : ['Case'] },

]

for t in tests:
    q = parsePartialQuery(t['query'])
    out = schemaGraphColor(schema, q)
    #print(out)
    if out != t['result']:
        print("%s != %s" % (out, t['result']))
