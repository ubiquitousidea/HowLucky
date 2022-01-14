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


ENTITY_MAP = dict(
    album=['release_id', 'title'],
    artist=['artist_id', 'artist'],
    country=['country', 'country'],
    label=['label_id', 'label']
)


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
    def __init__(self, id, show_selection=False, *args, **kwargs):
        self.base_id = id
        self._show_selection = show_selection
        dbc.Container.__init__(self, id=f'{self.base_id}_container', *args, **kwargs)
        self.children = []
        self.generate_components()

    def generate_components(self):
        self.children = [
            dcc.Graph(
                id=self.base_id,
                style={'height': '70vh', 'width': '45vw'},
                figure=Figure(layout=Layout(**LAYOUT_STYLE))
            ),
            dcc.Store(id=f'{self.base_id}_custom_data')
        ]
        if self._show_selection:
            self.children.append(html.Pre(id=f'{self.base_id}_selection', style={'color': '#fff'}))


CARD_STYLE = {
    'width': '45vw',
    'max-height': 500,
    'padding': '10px',
    'margin': '10px',
    'background-color': '#444455'
}


class BaseCard(dbc.Card):
    """
    Class for artist/label/album cards
    """
    def __init__(self, row):
        entity, _ = row.index[0].split('_')
        _id = row.values[0]
        dbc.Card.__init__(self, id=f'{entity}_{_id}_card', style=CARD_STYLE, className='p-3')
        self.children = []
        if entity == 'release':
            title = row['title']
        else:
            title = row['name']
        self._title = title
        self._image_url = row['image']
        self._profile = row['profile']
        self.generate_components()

    def generate_components(self):
        self.children = [
            dbc.Row([
                dbc.Col([
                    dbc.CardImg(src=self._image_url),
                    dbc.CardImgOverlay(
                        html.H4(
                            self._title,
                            style={'color': '#fff', 'margin': '1rem'})
                    )
                ], width=4),
                dbc.Col([
                    html.P(self._profile, style={'color': '#fff'})
                ], width=8)
            ]),
        ]


layout_1 = dbc.Container([
    dbc.Row([
        html.H1('Record Collection Analyzer', style={'color': '#EEEEEE', 'margin': '10px'})
    ]),
    dbc.Row([
        dbc.Col([
            Options(
                id='entity_dropdown', title='Entity',
                options=ENTITY_OPTIONS, default_option=2
            ),
            Options(
                id='x_measure', title='Count Measure',
                options=MEASURE_OPTIONS,

            ),
            Options(
                id='y_measure', title='Price Measure',
                options=MEASURE_OPTIONS,
            )
        ], width=6),
        dbc.Col([
            Options(
                id='timeseries_y_var', title='Y-Variable',
                options=YAXIS_OPTIONS
            )
        ], width='auto')
    ]),
    dbc.Row([
        dbc.Col([
            GraphPlus(id='graph1')
        ]),
        dbc.Col([
            dbc.Collapse(GraphPlus(id='graph2'), id='graph2_collapse', is_open=False),
            dbc.Container(id='card_container', fluid=True)

        ])
    ])
], fluid=True, id='main_container', style=MAIN_STYLE)
