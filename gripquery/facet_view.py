
import gripql
from .app import app
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State, MATCH, ALL
import dash_table

from .conn import connect

def setup(graphs):
    return html.Div([
        html.Div(
            dcc.Dropdown(
            id='facet-graph',
            options=list( {"label":i, "value":i} for i in graphs ),
            value=graphs[0]
        )),
        html.Div(
            dcc.Dropdown(
                id="facet-label",
                options=[]
            )
        ),
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
                    page_size= 50,
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
        )
        ], style={
        "height" : "100%"
    })


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
    [Input("facet-graph", "value"), Input("facet-label", "value")]
)
def update_facets(graph, label):
    print("Updating %s %s" % (graph, label))
    if label is None or graph is None:
        return {}, []

    c = connect()
    G = c.graph(graph)
    schema = G.getSchema()

    columns = []
    fields = None
    for v in schema.get("vertices", []):
        if v["gid"] == label:
            fields = list(v["data"].keys())
            for f in fields:
                columns.append({"name":f, "id":f})
    facets = {}
    if fields is not None:
        for row in G.query().V().hasLabel(label).aggregate( list(gripql.term(f, f) for f in fields)  ):
            if row['name'] not in facets:
                facets[row['name']] = {"index":len(facets), "options":[]}
            facets[row['name']]['options'].append({"value":row['key'],"label":row['key']})
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

@app.callback(
    Output("facet-table", "data"),
    [
        Input("facet-graph", "value"),
        Input("facet-label", "value"),
        Input({"type": "facet-selector", "index":ALL}, "value")
    ],
    [State("facet-store", "data"),]
)
def update_table(graph, label, facet_inputs, facets):
    if graph is not None and label is not None:
        conn = connect()
        G = conn.graph(graph)
        q = G.query().V().hasLabel(label)
        if len(facet_inputs):
            for k, f in facets.items():
                fi = facet_inputs[f['index']]
                if len(fi):
                    q = q.has(gripql.within(k, fi))
        data = results_data(q)
        return data
    return []

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
