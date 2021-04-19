
import argparse
import os
import yaml
import gripql
from glob import glob
import dash
import json
import dash_table
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, MATCH, ALL
from flask import Flask, send_from_directory

import dash_cytoscape as cyto

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css', dbc.themes.BOOTSTRAP]
#external_stylesheets = [dbc.themes.BOOTSTRAP]

server = Flask(__name__)
app = dash.Dash(__name__, server=server, external_stylesheets=external_stylesheets)

PORT="8050"
HOST="localhost"
GRIP="https://exa.compbio.ohsu.edu/bmeg-etl"
CRED=None

GRAPHS = []

def schemaGraph():
    return html.Div([
        cyto.Cytoscape(
            id='cytoscape-two-nodes',
            layout={'name': 'preset'},
            style={'width': '100%', 'height': '400px'},
            elements=[
                {'data': {'id': 'one', 'label': 'Node 1'}, 'position': {'x': 75, 'y': 75}},
                {'data': {'id': 'two', 'label': 'Node 2'}, 'position': {'x': 200, 'y': 200}},
                {'data': {'source': 'one', 'target': 'two'}}
            ]
        )
    ])

def query_validate(text):
    try:
        out = eval(str(text), {"V": gripql.query.Query(url="", graph="test").V}, {})
    except:
        return False
    if isinstance(out, gripql.query.Query):
        return True
    return False

def query_parse(text):
    try:
        out = eval(str(text), {"V": gripql.query.Query(url="", graph="test").V}, {})
    except:
        return None
    if isinstance(out, gripql.query.Query):
        return out
    return None

#@app.callback(
#    Output("query-parsed", "children"),
#    [Input("grip-query", "value")],
#)
def query_view(text):
    q = query_parse(text)
    if q is not None:
        return html.Div(q.to_json())
    return html.Div("")


def navbar():
    navbar = dbc.Navbar(
        [
            html.A(
                # Use row and col to control vertical alignment of logo / brand
                dbc.Row(
                    [
                        dbc.Col(dbc.NavbarBrand("GRIP", className="ml-2")),
                    ],
                    align="center",
                    no_gutters=True,
                ),
                href="https://bmeg.github.io/grip/",
            ),
        ],
        color="dark",
        dark=True,
    )
    return navbar

def app_setup():
    conn = gripql.Connection(GRIP, credential_file=CRED)
    GRAPHS = []
    for i in conn.listGraphs():
        GRAPHS.append(i)
    
    dialog =  dcc.Input(
        id="grip-query",
        type="text",
        size="120",
        debounce=True,
    )

    app.layout = html.Div([
        navbar(),
        html.Div(
            dcc.Dropdown(
            id='query-graph',
            options=list( {"label":i, "value":i} for i in GRAPHS ),
            value=GRAPHS[0]
        )),
        html.Div(dialog),
        html.Div(id="query-text"),
        html.Button('Run Query', id='submit-val', n_clicks=0),
        #schemaGraph(),
        #html.Div(id="query-parsed"),
        html.Div(id="query-results"),
    ])
    
def results_columns(results):
    c = set()
    for row in results:
        if 'label' in row and 'data' in row:
            c.update(list(row['data'].keys()))
    return list( {"name":i, "id": i} for i in c )

def results_data(results):
    out = []
    for row in results:
        if 'label' in row and 'data' in row:
            r = {}
            for k, v in row['data'].items():
                r[k] = str(v)
            out.append(r)
    return out

def query_viewer(graph, query, num):
    conn = gripql.Connection(GRIP, credential_file=CRED)
    q = query_parse(query)
    q.base_url = GRIP
    q.graph = graph
    q.credential_file = CRED
    q.url = GRIP + "/v1/graph/" + graph + "/query"
    results = list(q.limit(10))
    
    columns = results_columns(results)
    data = results_data(results)

    table = dash_table.DataTable(
        id='table',
        columns=columns,
        data=data,
    )
    
    card = dbc.Card(
        [
            #dbc.CardImg(src="/static/images/placeholder286x180.png", top=True),
            dbc.CardHeader("Query %d" % (num)),
            dbc.CardBody(
                [
                    html.H4(query, className="card-title"),
                    table,
                    dbc.Button("Delete", id={
                        "type" : "result-card-delete",
                        "index" : num
                    }, color="primary"),
                ]
            ),
        ],
        style={"width": "100%"},
        #outline=True,
        color="primary",
        id={
            "type" : "result-card",
            "index": num
        },
        className="mb-3",
    )
    return card


@app.callback(
    Output('query-results', 'children'),
    [Input('submit-val', 'n_clicks'), Input({'type': 'result-card-delete', 'index': ALL}, 'n_clicks')],
    [Input('query-graph', 'value'), State('grip-query', 'value'), State('query-results', 'children') ])
def update_output(n_clicks, result_delete, graph, query, results):
    ctx = dash.callback_context
    if not ctx.triggered:
        button_id = 'No clicks yet'
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == "submit-val":
        if query_validate(query):
            o = query_viewer(graph, query, n_clicks)
        else:
            return results
        if results is None:
            return [o]
        else:
            return [o] + results
    else:
        if "index" in button_id:
            button_data = json.loads(button_id)
            o = []
            for i in results:
                print(i)
                if i["props"]['id']['index'] != button_data['index']:
                    o.append(i)
            results = o
    return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default=HOST)
    parser.add_argument("-p", "--port", default=PORT)
    parser.add_argument("-g", "--grip", default=GRIP)
    parser.add_argument("-c", "--cred", default=CRED)    
    
    args = parser.parse_args()
    HOST = args.host
    PORT = args.port
    GRIP = args.grip
    CRED = args.cred

    app_setup()

    app.run_server(debug=True,
        port=PORT,
        host=HOST)