from dash import (
    Dash, Input, Output, State, dcc, html, 
    get_asset_url, callback, callback_context)
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from dashboard.layout2 import main_layout
import plotly.graph_objects as go
import plotly.express as px
from discogs_identity import dclient
from database.database_util import get_metadata
from database.database_util_postgres import DBPostgreSQL
from sql.schema import DB_KEYS_POSTGRES, LABEL_TABLE, ARTIST_TABLE, RELEASE_TABLE
import re
import time
from dashboard.image_cache import ImageCache
from flask import Flask

server = Flask()
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], server=server)
app.title = " Vinyl Collection Analyser"
app.layout = main_layout


DB = DBPostgreSQL(DB_KEYS_POSTGRES)


@callback(
    Output('main_dropdown', 'options'),
    Output('main_dropdown', 'placeholder'),
    Output('dropdown_entity', 'data'),
    Input('labels_btn', 'n_clicks'),
    Input('artists_btn', 'n_clicks'),
    Input('releases_btn', 'n_clicks')
)
def update_dropdown_options(n1, n2, n3):
    btn = callback_context.triggered_id
    if btn is None:
        raise PreventUpdate
    tbl_name = re.search(r'(\w+)_btn', btn).group(1)
    entity = re.sub(r'(\w+)s', r'\1', tbl_name)
    name_col = 'title' if tbl_name == 'releases' else 'name'
    id_col = f'{entity}_id'
    tbl = DB.read_rows(tbl_name)
    tbl = tbl.sort_values(name_col).reset_index(drop=True)
    options = [
        {'label': row[name_col], 'value': {'id': row[id_col], 'name': row[name_col]}} 
        for idx, row in 
        tbl.iterrows()]
    return (
        options, 
        f'Select a {entity.title()}',
        {'entity': entity})


@app.callback(
    Output('main_dropdown', 'value'),
    Input('labels_btn', 'n_clicks'),
    Input('artists_btn', 'n_clicks'),
    Input('releases_btn', 'n_clicks')
)
def afffffff(_, __, ___):
    pass


@callback(
    Output('image_area', 'children'),
    Input('main_dropdown', 'value'),
    State('dropdown_entity', 'data')
)
def show_card(v, d):
    if not v:
        raise PreventUpdate
    entity = d['entity']
    image_url = ImageCache().get_image(entity, v['id'])
    
    if entity == 'artist':
        artist = dclient.artist(v['id'])
        main_text = artist.profile
    elif entity == 'label':
        label = dclient.label(v['id'])
        main_text = label.profile
    elif entity == 'release':
        release = dclient.release(v['id'])
        main_text = release.notes
    else:
        raise ValueError(f'Unknown entity {entity}')
    
    sub_entity = {
        'artist': 'release', 
        'label': 'artist', 
        'release': 'release'}.get(entity)
    button_id = {
        'entity': entity, 
        'id': v['id'], 
        'desired_entity': sub_entity}
    output = dbc.Card([
        dbc.CardHeader(html.H2(v['name'])),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Img(
                        src=image_url,
                        alt=f"Picture of {v['name']}",
                        className='img-fluid'
                    )
                ], width=5),
                dbc.Col([
                    html.P(main_text, style={'max-height': '500px', 'overflowY': 'auto'})
                ], width=7)
            ]),
        ]),
        dbc.CardFooter([
            dbc.Button([f'See {sub_entity}s'], id=button_id, color='info')
        ], class_name='text-center')
    ], class_name='entity_card')
    return output

if __name__ == "__main__":
    app.run(port=8099, debug=False)
