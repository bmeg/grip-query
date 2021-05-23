
import json
from .app import app
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, MATCH, ALL
import dash_core_components as dcc
import dash_html_components as html
import dash_cytoscape as cyto
import dash_table

from gripquery.render import parsePartialQuery, schemaGraphColor
import dash
import gripql
from .conn import connect, GRIP, CRED

base_cyto_stylesheet = [
     {
        'selector': 'node',
        'style': {
            'content': 'data(label)'
        }
    },
    {
        'selector': '.red',
        'style': {
            'background-color': 'red',
            'line-color': 'red'
        }
    }
]

schema_holder_style = {
    "position": "fixed",
    "top": 0,
    "right": 0,
    "bottom": 0,
    "width": "300px",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

def schemaGraph():
    return html.Div([
        cyto.Cytoscape(
            id='schema-graph',
            layout={'name': 'cose'},
            stylesheet=base_cyto_stylesheet,
            style={'width': '100%', 'height': '100%'},
            elements=[]
        )],
        style=schema_holder_style,
        id="schema-holder"
    )

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

def query_validate(text):
    try:
        out = eval(str(text), {"V": gripql.query.Query(url="", graph="test").V, "gripql" : gripStub()}, {})
    except Exception as e:
        print(e)
        return False
    if isinstance(out, gripql.query.Query):
        return True
    return False

def query_parse(text):
    try:
        out = eval(str(text), {"V": gripql.query.Query(url="", graph="test").V, "gripql" : gripStub()}, {})
    except:
        return None
    if isinstance(out, gripql.query.Query):
        return out
    return None


def query_view(text):
    q = query_parse(text)
    if q is not None:
        return html.Div(q.to_json())
    return html.Div("")



def setup(graphs):
    dialog =  dcc.Textarea(
        id="query-text",
        style={'width': '100%', 'fontSize':20, "height":150}
    )

    return html.Div([
        html.Div([
            dbc.Row([                
                dbc.Col(html.Div(dialog), width=11),
                dbc.Col([
                    dbc.Button(html.Span("play_arrow", className="material-icons"), color="primary", className="mb-3", id='submit-val', n_clicks=0),
                    dbc.Button(html.Span("schema", className="material-icons"), color="primary", className="mb-3", id='show-schema', n_clicks=0),
                ], width=1)
            ]),
            dbc.Row([
                dbc.Col(html.Span("Query Graph"), width=1),
                dbc.Col(dcc.Dropdown(
                    id='query-graph',
                    options=list( {"label":i, "value":i} for i in graphs ),
                    value=graphs[0]
                )),
            ]),
            ],
            style={"margin-right" : "300px"},
            id="query-holder"
        ),
        html.Hr(),
        dcc.Store(id='schema-store'),
        html.Div([
            schemaGraph(),
            #html.Div(id="query-parsed"),
            html.Div(id="query-results",style={"margin-right":"300px"}),
        ])
    ])


def results_columns(results):
    c = set()
    for row in results:
        if 'vertex' in row:
            if 'data' in row['vertex']:
                c.update(list(row['vertex']['data'].keys()))
        elif 'render' in row:
            if isinstance(row['render'], dict):
                c.update(list(row['render'].keys()))
        else:
            print("Unknown type")
    return list( {"name":i, "id": i} for i in c )

def results_data(results):
    out = []
    for row in results:
        if 'vertex' in row:
            if 'data' in row['vertex']:
                r = {}
                for k, v in row['vertex']['data'].items():
                    r[k] = str(v)
                out.append(r)
    return out

def query_viewer(graph, query, num):
    conn = connect()
    q = query_parse(query)
    q.base_url = GRIP
    q.graph = graph
    q.credential_file = CRED
    q.url = GRIP + "/v1/graph/" + graph + "/query"
    results = q.limit(10).execute(raw=True)

    columns = results_columns(results)
    data = results_data(results)

    table = dash_table.DataTable(
        id='table',
        columns=columns,
        data=data,
        style_table={'overflowX': 'auto'},
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

# tried this one as a clientside_callback, but child elemnts like the cytoscape 
# didn't update
@app.callback(
    Output('schema-holder', 'style'),
    [Input('show-schema', 'n_clicks')])
def toggle_container(toggle_value):
    #print(toggle_value, flush=True)
    if toggle_value % 2 == 0:
        return schema_holder_style
    else:
        return {'display': 'none'}


app.clientside_callback(
    """
    function(n_clicks) {
        if (n_clicks % 2 == 0) {
            return {
                "margin-right" : "300px"
            }
        }
        return {
            "margin-right" : "0px"
        }
    }
    """,
    Output('query-results', 'style'),
    Input('show-schema', 'n_clicks')
)


app.clientside_callback(
    """
    function(n_clicks) {
        if (n_clicks % 2 == 0) {
            return {
                "margin-right" : "300px"
            }
        }
        return {
            "margin-right" : "0px"
        }
    }
    """,
    Output('query-holder', 'style'),
    Input('show-schema', 'n_clicks')
)


@app.callback(
    Output('schema-graph', 'elements'),
    [Input('schema-store', 'data')]
)
def schema_render(schema):
    o = []
    if 'vertices' in schema:
        for i in schema['vertices']:
            t = {"data": {"id":i['gid'], "label": i['gid']}}
            o.append(t)
    if 'edges' in schema:
        for i in schema['edges']:
            t = {"data":{"source":i['from'], "target":i['to']}}
            o.append(t)
    return o

@app.callback(
    Output('schema-graph', 'stylesheet'),
    [Input('query-text', 'value'), Input('schema-store', 'data')]
)
def schema_style(query, schema):
    q = parsePartialQuery(query)
    colored = schemaGraphColor(schema, q)
    o = []
    for i in base_cyto_stylesheet:
        o.append(i)
    for c in colored:
        o.append({
            'selector': "[id = '%s']" % (c),
            'style': {
                'content': 'data(label)',
                'background-color': 'blue',
            }
        })
    return o

@app.callback(
    Output('schema-store', 'data'),
    [Input('query-graph', 'value')]
)
def schema_load(graph):
    G = gripql.Graph(GRIP, credential_file=CRED, graph=graph)
    o = {'vertices' : [], 'edges' : []}
    try:
        schema = G.getSchema()
    except:
        schema = {}
    if 'vertices' in schema:
        for i in schema['vertices']:
            o['vertices'].append({"gid":i["gid"], "label":i["label"]})
    if 'edges' in schema:
        for i in schema['edges']:
            o['edges'].append({"from":i["from"], "to":i['to'], "label":i["label"]})
    return o


@app.callback(
    Output('query-results', 'children'),
    [Input('submit-val', 'n_clicks'), Input({'type': 'result-card-delete', 'index': ALL}, 'n_clicks')],
    [Input('query-graph', 'value'), State('query-text', 'value'), State('query-results', 'children') ])
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
            print("Invalid query")
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
                if i["props"]['id']['index'] != button_data['index']:
                    o.append(i)
            results = o
    return results
