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


YAXIS_OPTIONS = [
    {'label': 'Lowest Price', 'value': 'lowest_price'},
    {'label': 'Number for Sale', 'value': 'num_for_sale'}
]


RADIO_STYLE_ARGS = dict(
    style={'margin': '2px'},
    labelStyle={'color': '#fff', 'margin': '5px'},
    inputStyle={'margin': '5px'}
)


class Options(dbc.Container):
    def __init__(self, id, title, options, default_option=0, *args, **kwargs):
        self._title = title
        dbc.Container.__init__(self, id=f'{id}_container', *args, **kwargs)
        self.children = [
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
        ]


class GraphPlus(dbc.Container):
    """
    Class to unify a graph and its associated customdata columns
    and a window to show selected data
    """
    def __init__(self, id, *args, **kwargs):
        self.base_id = id
        dbc.Container.__init__(self, id=f'{self.base_id}_container', *args, **kwargs)
        self.generate_components()

    def generate_components(self):
        self.children = [
            dcc.Graph(
                id=self.base_id,
                style={'height': '70vh', 'width': '45vw'},
                figure=Figure(layout=Layout(**LAYOUT_STYLE))
            ),
            dcc.Store(id=f'{self.base_id}_custom_data'),
            html.Pre(id=f'{self.base_id}_selection', style={'color': '#fff'})
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
        ], width=6),
        dbc.Col([
            Options(
                id='timeseries_y_var',
                title='Y-Variable',
                options=YAXIS_OPTIONS
            )
        ], width='auto')
    ]),
    dbc.Row([
        dbc.Col([
            GraphPlus(id='graph1')
        ]),
        dbc.Col([
            GraphPlus(id='graph2')
        ])
    ])
], fluid=True, id='main_container', style=MAIN_STYLE)


page_layout = dbc.Container()
