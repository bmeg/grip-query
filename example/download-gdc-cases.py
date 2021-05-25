#!/usr/bin/env python

import json
import requests

URL_BASE = "https://api.gdc.cancer.gov/"
PROJECT = "TCGA-BRCA"

filter = {
    "op":"=",
    "content":{
        "field":"project.project_id",
        "value":PROJECT
    }
}

expand = [
"demographic", "diagnoses", "diagnoses.treatments"
"exposures","family_histories","project",
"project.program", "samples", "samples.annotations",
"samples.portions", "samples.portions.analytes",
"samples.portions.analytes.aliquots", "samples.portions.analytes.aliquots.annotations",
"samples.portions.analytes.aliquots.center",
"samples.portions.analytes.annotations", "samples.portions.annotations",
"samples.portions.center", "samples.portions.slides",
"samples.portions.slides.annotations", "tissue_source_site", "type"
]
page_size = 100
params = {
    "expand": ",".join(expand),
    "size": page_size,
    "filters" : json.dumps(filter)
}

case_format = {
    "samples" : {
        "portions" : {
            "analytes" : {
                "aliquots" : {
                    "center" : {},
                    "annotations" : {},
                }
            },
            "slides":{},
            "center" : {},
        }
    },
    "diagnoses": {},
    "center" : {},
    "project": {}
}

def parse_record(data, label, form, handles):
    child_nodes = {}
    for f in form:
        if f in data:
            child_nodes[f] = []
            if isinstance(data[f], list):
                for c in data[f]:
                    if f == "diagnoses":
                        child_label = "diagnosis"
                    elif f.endswith("s"): #dumb hack to deal with plural -> singular
                        child_label = f[:-1]
                    else:
                        child_label = f
                    id = parse_record(c, child_label, form[f], handles)
                    child_nodes[f].append(id)
            else:
                child_label = f
                id = parse_record(data[f], child_label, form[f], handles)
                child_nodes[f].append(id)

    out = {}
    for k, v in data.items():
        if k not in form:
            out[k] = v

    id = data[label + "_id"]
    handles[0].write(json.dumps( {"gid" : id, "label": label, "data":out}) + "\n")

    for f in child_nodes:
        for cid in child_nodes[f]:
            handles[1].write(json.dumps({"from":id, "to":cid, "label":f}) + "\n")
    return id



with open(PROJECT + ".vertices", "w") as vhandle:
    with open(PROJECT + ".edges", "w") as ehandle:
        while True:
            req = requests.get(URL_BASE + "cases", params=params)
            data = req.json()
            data = data['data']
            hits = data.get("hits", [])
            if len(hits) == 0:
                break
            for hit in hits:
                parse_record(hit, "case", case_format, [vhandle, ehandle])
            # Get the next page.
            params['from'] = data['pagination']['from'] + page_size
