
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

from . import conn
from . import query_view
from . import facet_view
from .style import format_style
from .app import app

PORT="8050"
HOST="0.0.0.0"


sidebar_header = dbc.Row(
    [
        dbc.Col(
            [html.Div(
                "GRIP",
            className="display-4"),
            html.Div(
                "GRaph Itegration Platform",
            className="display-8")]
        ),
        dbc.Col(
            [
                html.Button(
                    html.Span(className="navbar-toggler-icon"),
                    className="navbar-toggler",
                    style={
                        "color": "rgba(0,0,0,.5)",
                        "border-color": "rgba(0,0,0,.1)",
                    },
                    id="navbar-toggle",
                ),
                html.Button(
                    html.Span(className="navbar-toggler-icon"),
                    className="navbar-toggler",
                    style={
                        "color": "rgba(0,0,0,.5)",
                        "border-color": "rgba(0,0,0,.1)",
                    },
                    id="sidebar-toggle",
                ),
            ],
            width="auto",
            align="center",
        ),
    ]
)

def genNavBarList():
    out = []
    for k, v in [ ("query","Query"), ("facet","Facet View") ]:
        e = dbc.NavLink(
            v,
            href="/%s" % (k),
            id="page-%s-link" % (k),
            style={
                'font-size': format_style('font_size_lg'),
                'fontFamily': format_style('font')
            }
        )
        out.append(e)
    return out



sidebar = html.Div(
    [
        sidebar_header,
        html.Div(
            [
                html.Hr(),
                html.P(
                    "Tools",
                    className="lead",
                    style={
                        'font-size': format_style('font_size_lg'),
                        'fontFamily': format_style('font'),
                        'margin-top' : "20px"
                    },
                ),
            ],
            id="blurb",
        ),
        dbc.Collapse(
            dbc.Nav(
                genNavBarList(),
                vertical=True,
                pills=True,
            ),
            id="collapse",
        ),
    ],
    id="sidebar",
)



def app_setup():
    content = html.Div(id="page-content")
    app.layout = html.Div([dcc.Location(id="url"), sidebar, content])


    #app.layout = html.Div([dcc.Location(id="url"),navbar(),content]) #,query_view.setup(graphs)])
    #app.layout = html.Div([navbar(),sidebar(),facet_view.setup(graphs)], style={
    #    "position": "fixed",
    #    "height" : "100%",
    #    "width" : "100%"
    #})

@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    c = gripql.Connection(conn.GRIP, credential_file=conn.CRED)
    graphs = []
    for i in c.listGraphs():
        if not i.endswith("__schema__"):
            graphs.append(i)

    if pathname == "/" or pathname == "/query":
        return query_view.setup(graphs)
    elif pathname == "/facet":
        return facet_view.setup(graphs)

    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )



@app.callback(
    Output("sidebar", "className"),
    [Input("sidebar-toggle", "n_clicks")],
    [State("sidebar", "className")]
)
def toggle_classname(n, classname):
    '''Side menu state'''
    if n and classname == "":
        return "collapsed"
    return ""


@app.callback(
    Output("collapse", "is_open"),
    [Input("navbar-toggle", "n_clicks")],
    [State("collapse", "is_open")]
)
def toggle_collapse(n, is_open):
    '''Side menu'''
    if n:
        return not is_open
    return is_open

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default=HOST)
    parser.add_argument("-p", "--port", default=PORT)
    parser.add_argument("-g", "--grip", default=conn.GRIP)
    parser.add_argument("-c", "--cred", default=conn.CRED)

    args = parser.parse_args()
    HOST = args.host
    PORT = args.port
    conn.GRIP = args.grip
    conn.CRED = args.cred

    app_setup()

    app.run_server(debug=True,
        port=PORT,
        host=HOST)
