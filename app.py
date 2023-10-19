from dash import Dash, Input, Output, State, dcc, html, get_asset_url, callback
import webbrowser
import dash_bootstrap_components as dbc
from dashboard.layout2 import main_layout

# from dash.dependencies import ALL
# from dash.exceptions import PreventUpdate
# from discogs_identity import dclient
# from dashboard.plotter import *


app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Collection Analyser 2.0.0"
app.layout = main_layout  # page_layout


@callback(
    Output("col1", "children"),
    Output("col2", "children"),
    Input("main_layout", "children"),
)
def add_pictures(_):
    return (
        html.Img(
            src=get_asset_url("giantsteps.jpg"),
            className="img-fluid",
            style={"padding": "12px"},
        ),
        html.Img(
            src=get_asset_url("sunshine.jpg"),
            className="img-fluid",
            style={"padding": "12px"},
        ),
    )


if __name__ == "__main__":
    port = 8053
    webbrowser.open(f"http://127.0.0.1:{port}")
    app.run_server(port=port, debug=True)
