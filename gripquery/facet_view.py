
import gripql
from .app import app
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State, MATCH, ALL
import dash_table
import dash_bootstrap_components as dbc

from .conn import connect

def setup(graphs):
    return html.Div([
        dbc.Row([
            dbc.Col(
                dcc.Dropdown(
                id='facet-graph',
                options=list( {"label":i, "value":i} for i in graphs ),
                value=graphs[0]
            )),
            dbc.Col(
                dcc.Dropdown(
                    id="facet-label",
                    options=[]
                )
            ),
            
            dbc.Col(
                dbc.Button(
                    html.Span("copy_all", className="material-icons"),
                    id="query-toast-toggle",
                    color="primary",
                    className="mb-3",
                ),
            )            
        ]),
        dcc.Store(id="facet-store"),
        dcc.Store(id="facet-filters"),
        html.Div([
            html.Div(id="facet-div", style={"height":"100%", "width":"20%", "float":"left"}),
            html.Div(
                dash_table.DataTable(
                    id='facet-table',
                    columns=[],
                    data=[],
                    style_cell={
                        'whiteSpace': 'normal',
                        'height': 'auto',
                        'overflowX': 'auto'
                    },
                    page_action="native",
                    page_current= 0,
                    page_size= 25,
                ),
                id="facet-table-div",
                style={
                    #"position": "relative",
                    "width": "80%",
                    #"left": "20rem",
                    "float": "right"
            })
            ],
            style={
                "height" : "100%"
            }
        ),
        dbc.Toast(
            [html.Span("V()", id="query-copy-text")],
            id="query-toast",
            is_open=False,
            header="GRIP Query",
            dismissable=True,
            style={"position": "fixed", "top": 20, "right": 10, "width": "50%"},
        )
        ], style={
        "height" : "100%"
    })


@app.callback(
    Output("query-toast", "is_open"),
    [Input("query-toast-toggle", "n_clicks")],
)
def open_toast(n):
    if n is not None:
        return True

@app.callback(
    Output('facet-label', "options"),
    Input("facet-graph", "value")
)
def update_labels(graph):
    if graph is None:
        return []
    c = connect()
    G = c.graph(graph)
    o = G.listLabels()
    if "vertexLabels" in o:
        return list( {"label":i, "value":i} for i in o["vertexLabels"] )
    return []


@app.callback(
    [Output("facet-store", "data"), Output("facet-table", "columns")],
    Input("facet-label", "value"), State("facet-graph", "value")
)
def update_facets(label, graph):
    if label is None or graph is None:
        return {}, []

    c = connect()
    G = c.graph(graph)
    schema = G.getSchema()

    columns = []
    fieldType = {}
    fields = None
    for v in schema.get("vertices", []):
        if v["gid"] == label:
            fields = list(v["data"].keys())
            for f in fields:
                t = v["data"][f]
                if t in ["STRING", "BOOL"]:
                    columns.append({"name":f, "id":f})
                    fieldType[f] = t
    if fields is not None:
        facetAgg = {}
        for row in G.query().V().hasLabel(label).aggregate( list(gripql.term(f, f) for f in fieldType.keys())  ):
            if row['name'] not in facetAgg:
                facetAgg[row['name']] = {}
            facetAgg[row['name']][row['key']] = row['value']

        facets = {}
        index = 0
        for name, valueSet in facetAgg.items():
            if len(valueSet) < 50:
                values = []
                options = []
                for i, value in enumerate(valueSet):
                    values.append(value)
                    options.append({"value":i,"label":str(value)})
                facets[name] = {"index":index, "options":options, "values":values}
                index += 1
    return facets, columns

# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "relative",
    "float": "left",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "20rem",
    "height" : "100%",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}


@app.callback(
    Output("facet-div", "children"),
    Input("facet-store", "data")
)
def update_view(data):
    if data is None:
        return []

    elements = []

    for k, v in data.items():
        a = html.Div([
            html.P("%s:" % (k)),
            dcc.Dropdown(id = {"type":'facet-selector', "index":v["index"]},
                options = v["options"],
                value = [],
                multi = True,
                style = {'font-size': '13px', 'color' : 'medium-blue-grey', 'white-space': 'nowrap', 'text-overflow': 'ellipsis'}
            )],
            style={"margin":"5px"}
        )
        elements.append(a)

    return [html.Div(elements, style=SIDEBAR_STYLE)]

# Not yet done, but covers use cases within this viewer
def query_string(q):
    d = q.to_dict()
    elements = []
    for q in d['query']:
        #print(q)
        if 'v' in q:
            elements.append("V()")
        elif 'hasLabel' in q:
            elements.append("hasLabel(%s)" % (",".join( '"%s"' % i for i in q['hasLabel'])))
        elif 'has' in q:
            if q['has']['condition']['condition'] == "WITHIN":
                values = ",".join( '"%s"' % i for i in q['has']['condition']['value'] )
                elements.append( 'has( gripql.within("%s", [%s]) )' % (q['has']['condition']['key'],values ) )
        else:
            elements.append(str(q))
    return ".".join(elements)

@app.callback(
    [ Output("facet-table", "data"), Output("query-copy-text", "children") ],
    [
        Input({"type": "facet-selector", "index":ALL}, "value")
    ],
    [
        State("facet-store", "data"),
        State("facet-graph", "value"),
        State("facet-label", "value")
    ]
)
def update_table(facet_inputs, facets, graph, label):
    if graph is not None and label is not None:
        conn = connect()
        G = conn.graph(graph)
        q = G.query().V().hasLabel(label)
        if len(facet_inputs):
            for k, f in facets.items():
                fi = facet_inputs[f['index']]
                if len(fi):
                    fset = []
                    # turn the dropdown selection numbers back into the original values
                    for j in fi:
                        fset.append(f['values'][j])
                    q = q.has(gripql.within(k, fset))
        data = results_data(q)
        return data, query_string(q)
    return [], "V()"

def results_data(results):
    out = []
    for row in results:
        r = {}
        for k, v in row['data'].items():
            r[k] = str(v)
        out.append(r)
    return out


#@app.callback(
#    Output("facet-filters", "data"),
#    Input({"type": "facet-selector", "index":ALL}, "value"),
#    State("facet-store", "data")
#)
#def update_filters(facets, facet_data):
#    print("Selected filters: %s %s" % (facets, facet_data))
#    return {}
