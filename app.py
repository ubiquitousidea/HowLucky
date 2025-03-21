import re
import time
from flask import Flask
from box import Box
from dash import (
    Dash, Input, Output, State, ALL,
    callback, callback_context)
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px

# ---------------------------
from dashboard.layout2 import (
    MAIN_LAYOUT, make_release_card, 
    make_artist_card, make_graph_card)
from database.database_util_postgres import DBPostgreSQL
from sql.schema import DB_KEYS_POSTGRES


server = Flask(__name__)
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], server=server)
app.title = " Vinyl Collection Analyser"
app.layout = MAIN_LAYOUT
DB = DBPostgreSQL(DB_KEYS_POSTGRES)


@callback(
    Output('column_1', 'children'),
    Input('main_dropdown', 'value'))
def show_artist(v):
    if not v:
        raise PreventUpdate
    return make_artist_card(v)


@callback(
    Output('column_2', 'children'),
    Input({
        'entity': ALL,
        'id': ALL,
        'desired_entity': ALL,
        'widget_type': 'button'
        }, 'n_clicks'))
def add_release_cards(_):
    if all([item is None for item in _]):
        raise PreventUpdate
    caller = Box(callback_context.triggered_id)
    artist_by_release = DB.read_rows('artist_by_release', artist_id=[caller.id])
    release_ids = artist_by_release.release_id.values.tolist()
    releases = DB.read_rows('last_price', release_id=release_ids)
    return [make_release_card(rel) for idx, rel in releases.iterrows()]


@callback(
    Output('column_3','children'),
    Input({
        'widget_type': 'graphit',
        'entity': 'release',
        'id': ALL,
        'graph_type': 'timeseries'
    }, 'n_clicks'))
def create_graphs(_):
    if all([item is None for item in _]):
        raise PreventUpdate
    caller = Box(callback_context.triggered_id)
    return make_graph_card([caller.id])


if __name__ == "__main__":
    app.run(port=8069, debug=False)
