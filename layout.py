from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from plotly.graph_objects import Layout, Figure
from plotter import LAYOUT_STYLE


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


MEASURE_OPTIONS = [
    {'label': 'Median', 'value': 'median'},
    {'label': 'Mean', 'value': 'mean'},
    {'label': 'Min', 'value': 'min'},
    {'label': 'Max', 'value': 'max'},
]


RADIO_STYLE_ARGS = dict(
    style={'margin': '10px'},
    labelStyle={'color': '#fff', 'margin': '5px'},
    inputStyle={'margin': '5px'}
)


class Options(dbc.Container):
    def __init__(self, id, title, options, default_option=0, *args, **kwargs):
        self._title = title
        dbc.Container.__init__(self, id=f'{id}_container', *args, **kwargs)
        self.children = [
            dbc.Container([
                dbc.Row([
                    dbc.Col([
                        html.H4(title, style={'color': '#fff'})
                    ], width=4),
                    dbc.Col([
                        dcc.RadioItems(
                            id=id,
                            options=options,
                            value=options[default_option]['value'],
                            **RADIO_STYLE_ARGS
                        )
                    ])
                ], justify='start')
            ])
        ]


layout_1 = dbc.Container([
    dbc.Row([
        html.H1('Record Collection Analyzer', style={'color': '#EEEEEE'})
    ]),
    dbc.Row([
        dbc.Col([
            Options(
                id='entity_dropdown',
                title='Entity',
                options=ENTITY_OPTIONS,
                default_option=2
            ),
            Options(
                id='x_measure',
                title='Count Measure',
                options=MEASURE_OPTIONS,

            ),
            Options(
                id='y_measure',
                title='Price Measure',
                options=MEASURE_OPTIONS,
            )
        ], width=4),
        dbc.Col(width=8)
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(
                id='graph1',
                style={'height': '70vh', 'width': '48vw'}),
            dcc.Store(id='graph1_custom_data')
        ]),
        dbc.Col([
            dcc.Graph(
                id='graph2',
                figure=Figure(layout=Layout(**LAYOUT_STYLE)),
                style={'height': '70vh', 'width': '48vw'}),
            dcc.Store(id='graph2_custom_data')
        ])
    ])
], fluid=True, id='main_container', style=MAIN_STYLE)


page_layout = dbc.Container()
