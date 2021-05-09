
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
#from . import query_view
from . import facet_view
from .app import app

PORT="8050"
HOST="0.0.0.0"

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
    c = gripql.Connection(conn.GRIP, credential_file=conn.CRED)
    graphs = []
    for i in c.listGraphs():
        if not i.endswith("__schema__"):
            graphs.append(i)

    #app.layout = html.Div([navbar(),query_view.setup(graphs)])
    app.layout = html.Div([navbar(),facet_view.setup(graphs)], style={
        "position": "fixed",
        "height" : "100%",
        "width" : "100%"
    })



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
