"""
create a dashboard to view and analyze the collected data
"""

import dash
from dash.dependencies import Input, Output, State, ALL
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import webbrowser
from plotter_util import get_factor, get_buttons_clicked
from database_util import get_metadata
from layout import main_layout, ENTITY_MAP, ArtistCard, AlbumCard
from plotter import (
    make_artist_plot,
    make_timeseries_plot
)


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = 'Collection Analyzer'
app.layout = main_layout  # page_layout


@app.callback(
    Output('graph1', 'figure'),
    Output('graph1_custom_data', 'data'),
    Output('graph1_entity', 'data'),
    Input('analyze_button', 'n_clicks'),
    Input('axis_type', 'value'),
    Input('measure', 'value'))
def update_graph1(n, at, measure):
    if not n:
        raise PreventUpdate
    return make_artist_plot(
        x_measure=measure,
        y_measure=measure,
        loglog=('log' in at))


@app.callback(Output('graph2', 'figure'),
              Output('graph2_custom_data', 'data'),
              Input({'object': 'card_button', 'field': ALL, 'value': ALL}, 'n_clicks'),
              Input('graph2_options', 'value'),
              State({'object': 'card_store', 'field': ALL, 'value': ALL}, 'data'))
def update_graph2(card_clicks, y_var, card_data):
    conditions = get_buttons_clicked(card_data, card_clicks)
    if not conditions:
        raise PreventUpdate
    return make_timeseries_plot(color_var='title', y_var=y_var, **conditions)


@app.callback(Output('card_container', 'children'),
              Input('graph1', 'selectedData'),
              State('graph1_custom_data', 'data'),
              State('graph1_entity', 'data'))
def add_cards(traces, custom_data_columns, entity):
    """
    generate dash bootstrap cards to represent a selection of point
    :param traces: selected points
    :param custom_data_columns: list of col names stored in each points' customdata
    :param entity: name of the entity plotted on scatter plot
    :return: list of Cards
    """
    if traces is None or len(traces) == 0:
        return []
    entity = entity[0]
    col_name, color_var = ENTITY_MAP.get(entity)
    conditions = get_factor(col_name, traces, custom_data_columns)
    card_data = get_metadata(entity, **conditions)
    cards = []
    for idx, row in card_data.iterrows():
        cards.append(ArtistCard.from_row(row))
    return cards


@app.callback(Output('release_card_col', 'children'),
              Input('graph2', 'clickData'),
              State('graph2_custom_data', 'data'))
def show_release_card(clickdata, customdata):
    """
    Create album card when user clicks a point on graph2
    :param clickdata: clickData property of graph 2
    :param customdata: list of column names stored in custom data of graph 2 points
    :return: list of 1 album card
    """
    if not clickdata:
        raise PreventUpdate
    conditions = get_factor('release_id', clickdata, customdata)
    cards = []
    for idx, row in get_metadata('last_price', **conditions).iterrows():
        cards.append(AlbumCard.from_row(row))
    return cards


if __name__ == '__main__':
    port = 8052
    webbrowser.open(f'http://127.0.0.1:{port}')
    app.run_server(port=port, debug=False)
