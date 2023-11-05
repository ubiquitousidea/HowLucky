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


app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = " Vinyl Collection Analyser"
app.layout = main_layout


DB = DBPostgreSQL(DB_KEYS_POSTGRES)


@callback(
    Output('main_dropdown', 'options'),
    Output('main_dropdown', 'value'),
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
    name_col = 'title' if tbl_name == 'releases' else 'name'
    id_col = f'{tbl_name[:-1]}_id'
    tbl = DB.read_rows(tbl_name)
    tbl = tbl.sort_values(name_col).reset_index(drop=True)
    options = [
        {'label': row[name_col], 'value': row[id_col]} 
        for idx, row in 
        tbl.iterrows()]
    return (
        options, 
        None, 
        f'Select a {tbl_name[:-1].title()}',
        {'table': tbl_name, 'key': name_col, 'id_col': id_col})


@callback(
    Output('image_area', 'children'),
    Input('main_dropdown', 'value'),
    State('dropdown_entity', 'data')
)
def show_image(v, d):
    if not v:
        raise PreventUpdate
    table_name = d['table']
    name_col = d['key']
    id_col = d['id_col']
    output = DB._query(
        f"select image, {name_col} "
        f"from public.{table_name} "
        f"where {id_col} = {v};")
    image_url = output[0][0]
    name = output[0][1]
    return html.Img(
        src=image_url, 
        alt=f'Picture of {name}', 
        className='img-fluid')






if __name__ == "__main__":
    app.run(port=8069, debug=False)
