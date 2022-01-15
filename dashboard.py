"""
create a dashboard to view and analyze the collected data
"""

import dash
from dash.dependencies import Input, Output, State, ALL
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import webbrowser
from util import dump_json
from plotter_util import get_factor
from database_util import get_metadata
from layout import layout_1, BaseCard, ENTITY_MAP
from plotter import (
    make_country_plot,
    make_label_plot,
    make_artist_plot,
    make_album_plot,
    make_timeseries_plot
)


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = 'Collection Analyzer'
app.layout = layout_1  # page_layout


@app.callback(
    Output('graph1', 'figure'),
    Output('graph1_custom_data', 'data'),
    Input('entity_dropdown', 'value'),
    Input('x_measure', 'value'),
    Input('y_measure', 'value')
)
def update_graph1(entity, x_measure, y_measure):

    if entity == 'country':
        plot_func = make_country_plot
    elif entity == 'label':
        plot_func = make_label_plot
    elif entity == 'artist':
        plot_func = make_artist_plot
    elif entity == 'album':
        plot_func = make_album_plot
    else:
        raise PreventUpdate

    return plot_func(x_measure=x_measure, y_measure=y_measure)


@app.callback(Output('card_container', 'children'),
              Input('graph1', 'selectedData'),
              State('entity_dropdown', 'value'),
              State('graph1_custom_data', 'data'))
def add_cards(traces, entity, custom_data_labels):
    """
    generate dash bootstrap cards to represent a selection of point
    :param traces: selected points
    :param entity: what entity those points represent (country, label, artist, release)
    :param custom_data_labels: list of col names stored in each points' customdata
    :return: list of Cards
    """
    if not custom_data_labels:
        raise PreventUpdate
    if traces is None or len(traces) == 0:
        return []
    col_name, color_var = ENTITY_MAP.get(entity)
    conditions = get_factor(col_name, traces, custom_data_labels)
    card_data = get_metadata(entity, **conditions)
    cards = []
    for idx, row in card_data.iterrows():
        card = BaseCard(row)
        cards.append(card)
    return cards


# @app.callback(Output('graph1_selection', 'children'),
#               Input('graph1', 'selectedData'))
# def report_graph1_selection(selected):
#     return dump_json(selected)


@app.callback(Output('textplace', 'children'),
              Input({'object': 'card_button', 'field': ALL, 'value': ALL}, 'n_clicks'),
              State({'object': 'card_store', 'field': ALL, 'value': ALL}, 'data'))
def get_button_clicks(n, d):

    return dump_json({'n': n, 'd': d})


if __name__ == '__main__':
    port = 8058
    webbrowser.open(f'http://127.0.0.1:{port}')
    app.run_server(port=port, debug=False)
