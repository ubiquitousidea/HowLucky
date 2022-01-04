"""
create a dashboard to view and analyze the collected data
"""

import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import webbrowser
from plotly.graph_objects import Layout, Figure
from plotter import (
    make_country_plot,
    make_label_plot,
    make_artist_plot,
    make_album_plot,
    make_timeseries_plot,
    ARTIST_INDEX, RELEASE_INDEX, LAYOUT_STYLE
)


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = 'Collection Analyzer'


ENTITY_OPTIONS = [
    {'label': 'Country', 'value': 'country'},
    {'label': 'Label', 'value': 'label'},
    {'label': 'Artist', 'value': 'artist'},
    {'label': 'Album', 'value': 'album'}
]


MAIN_STYLE = {
    'font-family': 'helvetica',
    'background-color': '#555555',
    'min-height': '100vh',
    'min-width': '100vw',
}


app.layout = dbc.Container([
    dbc.Row([
        html.H1('Record Collection Analyzer')
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(
                id='entity_dropdown',
                options=ENTITY_OPTIONS,
                value='album',
                multi=False,
                clearable=False
            )
        ], width=4),
        dbc.Col(width=8)
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(
                id='graph1',
                style={'height': '70vh', 'width': '33vw'})
        ]),
        dbc.Col([
            dcc.Graph(
                id='graph2',
                figure=Figure(layout=Layout(**LAYOUT_STYLE)),
                style={'height': '70vh', 'width': '63vw'})
        ])
    ])
], fluid=True, id='main_container', style=MAIN_STYLE)


@app.callback(
    Output('graph1', 'figure'),
    Input('entity_dropdown', 'value'))
def update_graph1(entity):
    if entity == 'country':
        fig = make_country_plot()
    elif entity == 'label':
        fig = make_label_plot()
    elif entity == 'artist':
        fig = make_artist_plot()
    elif entity == 'album':
        fig = make_album_plot()
    else:
        raise PreventUpdate
    return fig


@app.callback(
    Output('graph2', 'figure'),
    Input('graph1', 'selectedData'),
    State('entity_dropdown', 'value'))
def update_graph2(traces, entity):
    if traces is None:
        raise PreventUpdate
    if entity == 'album':
        release_ids = [point['customdata'][RELEASE_INDEX] for point in traces['points']]
        conditions = {'release_id': release_ids}
    elif entity == 'artist':
        artist_ids = [point['customdata'][ARTIST_INDEX] for point in traces['points']]
        conditions = {'artist_id': artist_ids}
    else:
        conditions = {}
    fig = make_timeseries_plot(**conditions)
    return fig


if __name__ == '__main__':
    port = 8052
    webbrowser.open(f'http://127.0.0.1:{port}')
    app.run_server(port=port, debug=False)
