
import gripql
from .app import app
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State, MATCH, ALL
import dash_table
import dash_bootstrap_components as dbc

from .conn import connect

def setup(graphs):

    graphSelect = dcc.Dropdown(id ='manager-graph-dropdown',
        options = list( {"label":g, "value": g } for g in graphs ),
        value = None,
        style = {'font-size': '13px', 'color' : 'medium-blue-grey', 'white-space': 'nowrap', 'text-overflow': 'ellipsis'}
    )

    graphDeleteCard = dbc.Card(
        dbc.CardBody(
            [
                html.H4("Delete Graph", className="card-title"),
                graphSelect,
                dcc.ConfirmDialogProvider(
                    children=html.Button("Delete"),
                    id='manager-delete-graph',
                    message='Are you sure that you want to delete this graph?'
                )
            ]
        ),
        style={"width": "18rem"},
    )

    return html.Div([
        graphDeleteCard,
        html.Div(id="manager-hidden")
    ])


@app.callback(Output("manager-hidden", "children"),
    [Input('manager-delete-graph', 'submit_n_clicks')],
    State('manager-graph-dropdown', 'value'))
def display_confirm(submit_click, graph):
    if submit_click:
        print("Deleting %s" % (graph))
        return [
            html.Meta(httpEquiv="refresh",content="0")
        ]
    return []
