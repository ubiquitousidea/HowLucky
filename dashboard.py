"""
create a dashboard to view and analyze the collected data
"""

import dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import webbrowser
from numpy import where, array
from layout import page_layout, layout_1
from plotter import (
    make_country_plot,
    make_label_plot,
    make_artist_plot,
    make_album_plot,
    make_timeseries_plot,

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


@app.callback(
    Output('graph2', 'figure'),
    Output('graph2_custom_data', 'data'),
    Input('graph1', 'selectedData'),
    State('entity_dropdown', 'value'),
    State('graph1_custom_data', 'data'))
def update_graph2(traces, entity, custom_data_labels):
    if traces is None:
        raise PreventUpdate
    if entity == 'album':
        release_index = where(array(custom_data_labels) == 'release_id')[0][0]
        release_ids = [point['customdata'][release_index] for point in traces['points']]
        conditions = {'release_id': release_ids}
        color_var = 'title'
    elif entity == 'artist':
        artist_index = where(array(custom_data_labels) == 'artist_id')[0][0]
        artist_ids = [point['customdata'][artist_index] for point in traces['points']]
        conditions = {'artist_id': artist_ids}
        color_var = 'artist'
    elif entity == 'country':
        country_index = where(array(custom_data_labels) == 'country')[0][0]
        country_names = [point['customdata'][country_index] for point in traces['points']]
        conditions = {'country': country_names}
        color_var = 'country'
    else:
        conditions = {}
        color_var = 'year'

    return make_timeseries_plot(color_var, **conditions)


if __name__ == '__main__':
    port = 8052
    webbrowser.open(f'http://127.0.0.1:{port}')
    app.run_server(port=port, debug=False)
