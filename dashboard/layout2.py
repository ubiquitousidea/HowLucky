import dash_bootstrap_components as dbc
from dash import html, dcc, get_asset_url


def make_button(text, btn_id):
    return dbc.Button(
        html.P(text, className='button_text'), 
        id=btn_id, color='secondary', style={'width':'20vw'})


main_layout = dbc.Container([
    dbc.Row([
        html.H1('Vinyl Collection Analyser')
    ]),
    dbc.Row([
        dbc.ButtonGroup([
            make_button('Label', 'labels_btn'),
            make_button('Artist', 'artists_btn'),
            make_button('Album', 'releases_btn')
        ], id='header_buttons')
    ], class_name='page_cell'),
    dbc.Row([
        dcc.Dropdown(id='main_dropdown'),
        dcc.Store(id='dropdown_entity')
    ], class_name='page_cell'),
    dbc.Row([
        dbc.Col(id="image_area", width=6, md=12),
        dbc.Col(id="info_area", width=6, md=12)
    ], class_name='page_cell')
], fluid=True, id='main_layout')
