import re
import time
from flask import Flask
from box import Box
from dash import (
    Dash, Input, Output, State, dcc, html, ALL,
    callback, callback_context)
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px

# ---------------------------
from dashboard.plotter import make_timeseries_plot
from dashboard.layout2 import main_layout
from discogs_identity import dclient
from database.database_util import get_metadata
from database.database_util_postgres import DBPostgreSQL
from sql.schema import DB_KEYS_POSTGRES, LABEL_TABLE, ARTIST_TABLE, RELEASE_TABLE
from dashboard.image_cache import ImageCache


server = Flask(__name__)
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
    # TODO: exclude artist 1389784 and 3016481
    options = [
        {'label': row[name_col], 'value': {'id': row[id_col], 'name': row[name_col]}} 
        for idx, row in 
        tbl.iterrows()]
    return (
        options, 
        f'Select a {entity.title()}',
        {'entity': entity})


@callback(
    Output('column_1', 'children'),
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
        'widget_type': 'button',
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
                        className='img-fluid', style={'height': '150px'}
                    )
                ]),
                dbc.Col([
                    html.P(main_text, className='bio_text')
                ])
            ]),
        ]),
        dbc.CardFooter([
            dbc.Button([f'See {sub_entity}s'], id=button_id, color='secondary')
        ], class_name='entity_card_footer')
    ], class_name='entity_card')
    return output





@callback(
    Output('column_2', 'children'),
    Input({
        'entity': ALL,
        'id': ALL,
        'desired_entity': ALL,
        'widget_type': 'button'
        }, 'n_clicks')
)
def add_sub_cards(_):
    if all([item is None for item in _]):
        raise PreventUpdate
    caller = Box(callback_context.triggered_id)
    if caller.desired_entity == 'release' and caller.entity == 'artist':
        x = DB.read_rows('artist_by_release', artist_id=[caller.id])
        releases = DB.read_rows('last_price', release_id=x.release_id.values.tolist())
        im = ImageCache()
        return [
            dbc.Card([
                dbc.CardHeader(html.H2(f'{rel.title} ({rel.catno})')),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Img(
                                src=im.get_release_image(rel.release_id), 
                                className='img-fluid', alt=f'Picture of {rel.title}',
                                style={'height':'150px'}
                            )
                        ]),
                        dbc.Col([
                            html.P(f'by {rel.artist}'),
                            html.P(f"{rel.label} ({rel.country} {rel.year if rel.year else ''})"),
                            html.P(f"{rel.num_for_sale} for sale from {rel.lowest_price}")
                        ])
                    ])
                ]),
                dbc.CardFooter([
                    dbc.Button('Show Trends', id={
                        'widget_type': 'graphit',
                        'entity': 'release',
                        'id': rel.release_id,
                        'graph_type': 'prices_over_time'
                    }, color='secondary')
                ], class_name='entity_card_footer')
            ], class_name='entity_card')
            for idx, rel in releases.iterrows()]


@callback(
    Output('column_3','children'),
    Input({
        'widget_type': 'graphit',
        'entity': 'release',
        'id': ALL,
        'graph_type': 'prices_over_time'
    }, 'n_clicks')
)
def create_graphs(_):
    if all([item is None for item in _]):
        raise PreventUpdate
    caller = Box(callback_context.triggered_id)
    if caller.graph_type == 'prices_over_time':
        fig, cdata = make_timeseries_plot(
            color_var='artist',
            release_id=[caller.id])
        
        graph_element = dcc.Graph(
            id={'entity': 'release', 'id': caller.id, 'widget_type': 'graph'},
            figure=fig, className='graph1', config=dict(displaylogo= False)
        )
        return dbc.Card([
            dbc.CardHeader(html.H2('Prices over Time')),
            dbc.CardBody(graph_element),
        ], class_name='graph-card')


if __name__ == "__main__":
    app.run(port=8069, debug=False)
