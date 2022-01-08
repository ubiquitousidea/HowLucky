from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from plotly.graph_objects import Layout, Figure
from plotter import LAYOUT_STYLE


page_layout = dbc.Container()


ENTITY_OPTIONS = [
    {'label': 'Country', 'value': 'country'},
    {'label': 'Label', 'value': 'label'},
    {'label': 'Artist', 'value': 'artist'},
    {'label': 'Album', 'value': 'album'}
]


MAIN_STYLE = {
    'font-family': 'helvetica',
    'background-color': '#222222',
    'min-height': '100vh',
    'min-width': '100vw',
}


layout_1 = dbc.Container([
    dbc.Row([
        html.H1('Record Collection Analyzer', style={'color': '#EEEEEE'})
    ]),
    dbc.Row([
        dbc.Col([
            dcc.RadioItems(
                id='entity_dropdown',
                options=ENTITY_OPTIONS,
                value='album',
                style={'margin': '10px'},
                labelStyle={'color': '#fff', 'margin': '5px'},
                inputStyle={'margin': '5px'}
            )
        ], width=4),
        dbc.Col(width=8)
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(
                id='graph1',
                style={'height': '70vh', 'width': '33vw'}),
            dcc.Store(id='graph1_custom_data')
        ]),
        dbc.Col([
            dcc.Graph(
                id='graph2',
                figure=Figure(layout=Layout(**LAYOUT_STYLE)),
                style={'height': '70vh', 'width': '63vw'}),
            dcc.Store(id='graph2_custom_data')
        ])
    ])
], fluid=True, id='main_container', style=MAIN_STYLE)
