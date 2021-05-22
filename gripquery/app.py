
import dash_bootstrap_components as dbc
from flask import Flask, send_from_directory
import dash

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css', dbc.themes.BOOTSTRAP]
#external_stylesheets = [dbc.themes.BOOTSTRAP]

server = Flask(__name__)
app = dash.Dash(__name__, server=server,
    external_stylesheets=external_stylesheets,
     meta_tags=[
        {
            "name": "viewport",
            "content": "width=device-width, initial-scale=1"
        }
    ]
)
app.config.suppress_callback_exceptions = True
