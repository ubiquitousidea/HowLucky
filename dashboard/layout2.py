import dash_bootstrap_components as dbc
from dash import html, dcc, get_asset_url


main_layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(id="col1", width=6, lg=6, md=12, sm=12),
                dbc.Col(id="col2", width=6, lg=6, md=12, sm=12),
            ]
        )
    ],
    id="main_layout",
    fluid=True,
    class_name="text-center",
)
