import dash_bootstrap_components as dbc
from dash import html, dcc, get_asset_url


main_layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(id="col1", class_name="col-lg-6 col-md-12"),
                dbc.Col(id="col2", class_name="col-lg-6 col-md-12"),
            ]
        )
    ],
    id="main_layout",
    fluid=True,
)
