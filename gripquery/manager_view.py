
import gripql
import json
from .app import app
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State, MATCH, ALL
import dash_table
import dash_bootstrap_components as dbc
import yaml

from .conn import connect

def setup(graphs):
    return html.Div([
        dcc.Tabs(id='manager-tabs', value='tab-info', children=[
            dcc.Tab(label='System Info', value='tab-info'),
            dcc.Tab(label='Start Driver', value='tab-start'),
            dcc.Tab(label='Mapping Wizard', value='tab-wizard'),
            dcc.Tab(label='Add Graph Mapping', value='tab-map'),
            dcc.Tab(label='Run Sifter Transform', value='tab-sifter'),
            dcc.Tab(label='Delete Graph', value='tab-delete'),
        ]),
        html.Div(id='manager-tabs-content'),
        html.Div(id="manager-delete-hidden"),
        html.Div(id="manager-mapping-hidden"),
        html.Div(id="manager-driver-hidden")
    ])

def genWizardEditor():
    conn = connect()
    tableOptions = []
    tableValues = {}
    for i, g in enumerate(sorted(conn.listTables(), key=lambda x:x['source']+x['name'])):
        tableOptions.append( {"label":"%s - %s" % (g['source'], g['name']), "value": str(i)} )
        tableValues[str(i)] = g

    return html.Div([
        dbc.Row([
            dbc.Col(dcc.Dropdown(id ='manager-wizard-dropdown',
                options = tableOptions,
                value = None,
                multi=True,
                style = {'font-size': '13px', 'color' : 'medium-blue-grey'}
            ), width="4"),
            dbc.Col(dbc.Card([
                dbc.CardBody("Create Vertex"),
                dcc.Input("manager-wizard-create-vertex-suffix", placeholder="Name Suffix"),
                dbc.Button("Create", id="manager-wizard-create-vertex", color="primary")
            ])),
            dbc.Col(dbc.Card([
                dbc.CardBody("Create Edge"),
                dbc.Button("Create", id="manager-wizard-create-edge", color="primary")
            ]))
        ]),
        dcc.Store(id="manager-wizard-vertex-store", data=[]),
        dcc.Store(id="manager-wizard-edge-store", data=[]),
        dcc.Store(id="manager-wizard-table-store", data=tableValues),
        html.Div(id="manager-wizard-preview")
    ])

@app.callback(Output("manager-wizard-preview", "children"),
[Input("manager-wizard-vertex-store", "data"),
Input("manager-wizard-edge-store", "data")])
def wizard_draw_preview(vertices, edges):
    o = []
    o.append(html.Div("""{"vertices" : ["""))
    for i in vertices:
        o.append(html.Div(json.dumps(i)))
    o.append(html.Div("""],"edges" : ["""))
    for i in edges:
        o.append(html.Div(json.dumps(i)))
    o.append("""]}""")
    return o

@app.callback(Output("manager-wizard-vertex-store", "data"),
    Input("manager-wizard-create-vertex", "n_clicks"),
    [State("manager-wizard-dropdown", "value"), State("manager-wizard-table-store", "data"), State("manager-wizard-create-vertex-suffix", "value"), State("manager-wizard-vertex-store", "data")]
)
def wizard_add_vertex(n_clicks, dropdown, values, suffix, data):
    if dropdown is not None and len(dropdown):
        print(values)
        for i in dropdown:
            v = values[i]
            data.append( { "gid" : v['name'] + suffix, "label": v['name'], "data" : { "collection" : v['name'], "source" : v['source'] } } )
        print("Adding Vertex")
    return data

@app.callback(Output('manager-tabs-content', 'children'),
              Input('manager-tabs', 'value'))
def render_content(tab):

    if tab == 'tab-info':
        conn = connect()
        return html.Div([
            html.H1("Graphs"),
            dash_table.DataTable(
                data=list( {"name" : g} for g in conn.listGraphs() ),
                columns=[{'id': "name", 'name': "Graph Name"}],
                page_size=10,
                style_cell={'textAlign': 'left'},
            ),
            html.Hr(),
            html.H1("Tables"),
            dash_table.DataTable(
                data=list( {"name" : g['name'], "source":g['source'], "fields":",".join(g['fields'])} for g in conn.listTables() ),
                columns=[{'id': "name", 'name': "Table Name"}, {'id': "source", 'name': "Table Source"}, {'id': "fields", 'name': "Table Fields"}],
                page_size=10,
                style_cell={'textAlign': 'left'},
            ),
            html.Hr(),
            html.H1("Drivers"),
            dash_table.DataTable(
                data=list( {"name" : g} for g in conn.listDrivers() ),
                columns=[{'id': "name", 'name': "Driver Name"}],
                page_size=10,
                style_cell={'textAlign': 'left'},
            ),
            html.Hr(),
            html.H1("Active Plugins"),
            dash_table.DataTable(
                data=list( {"name" : g} for g in conn.listPlugins() ),
                columns=[{'id': "name", 'name': "Plugin Name"}],
                page_size=10,
                style_cell={'textAlign': 'left'},
            ),
            html.Hr(),
        ])
    elif tab == 'tab-start':
        conn = connect()
        drivers = conn.listDrivers()
        initDriverSelect = dcc.Dropdown(id ='manager-driver-init-dropdown',
            options = list( {"label":g, "value": g } for g in drivers ),
            value = None,
            style = {'font-size': '13px', 'color' : 'medium-blue-grey', 'white-space': 'nowrap', 'text-overflow': 'ellipsis'}
        )
        initConfigText = dcc.Textarea(
            id='manager-driver-init-config',
            value='',
            style={'width': '100%', 'height': 300},
        )
        return html.Div([
            initDriverSelect,
            dcc.Input(id="manager-driver-init-name", placeholder="Plugin Name", type="text"),
            initConfigText,
            html.Button("Start Plugin", id="manager-driver-init")
        ])
    elif tab == 'tab-wizard':
        return html.Div([
            genWizardEditor(),
            html.Div(id="manager-wizard-preview")
        ])

    elif tab == 'tab-map':
        return html.Div([
            dcc.Input(id="manager-add-mapping-name", placeholder="Graph Name", type="text"),
            dcc.Textarea(
                id='manager-add-mapping-config',
                value='',
                style={'width': '100%', 'height': 300},
            ),
            html.Button("Add Mapping", id="manager-add-mapping")
        ])
    elif tab == 'tab-delete':
        conn = connect()
        graphs = conn.listGraphs()
        deleteGraphSelect = dcc.Dropdown(id ='manager-graph-delete-dropdown',
            options = list( {"label":g, "value": g } for g in graphs ),
            value = None,
            style = {'font-size': '13px', 'color' : 'medium-blue-grey', 'white-space': 'nowrap', 'text-overflow': 'ellipsis'}
        )
        graphDeleteCard = dbc.Card(
            dbc.CardBody(
                [
                    html.H4("Delete Graph", className="card-title"),
                    deleteGraphSelect,
                    dcc.ConfirmDialogProvider(
                        children=html.Button("Delete"),
                        id='manager-delete-graph',
                        message='Are you sure that you want to delete this graph?'
                    )
                ]
            ),
            style={"width": "30rem"},
        )
        return graphDeleteCard
    return html.Div()

@app.callback(Output("manager-delete-hidden", "children"),
    [Input('manager-delete-graph', 'submit_n_clicks')],
    State('manager-graph-delete-dropdown', 'value'))
def display_confirm(submit_click, graph):
    if submit_click:
        print("Deleting %s" % (graph))
        conn = connect()
        conn.deleteGraph(graph)
        return [
            html.Meta(httpEquiv="refresh",content="0")
        ]
    return []

@app.callback(Output("manager-driver-hidden", "children"),
    [Input('manager-driver-init', 'n_clicks')],
    [State('manager-driver-init-dropdown', 'value'), State("manager-driver-init-name", "value"), State('manager-driver-init-config', 'value')])
def plugin_start(submit_click, plugin, name, config):
    if plugin is not None:
        try:
            config = yaml.load(config, yaml.SafeLoader)
            conn = connect()
            res = conn.startPlugin(name, plugin, config)
            print(res)
        except:
            pass
    return []


@app.callback(Output("manager-mapping-hidden", "children"),
    [Input('manager-add-mapping', 'n_clicks')],
    [State('manager-add-mapping-name', 'value'), State('manager-add-mapping-config', 'value')])
def plugin_start(submit_click, graph, mapping):
    if graph != "":
        data = yaml.load(mapping, yaml.SafeLoader)
        if data is not None and 'vertices' in data and 'edges' in data:
            conn = connect()
            res = conn.postMapping(graph, data['vertices'], data['edges'])
            print(res)
    return []
