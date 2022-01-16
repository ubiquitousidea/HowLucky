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


TITLE_STYLE = {
    'color': '#EEEEEE',
    'background-color': '#252525',
    'margin': '4px'
}


MEASURE_OPTIONS = [
    {'label': 'Median', 'value': 'median'},
    {'label': 'Mean', 'value': 'mean'},
    {'label': 'Min', 'value': 'min'},
    {'label': 'Max', 'value': 'max'},
]


GRAPH_TYPES = [
    {'label': 'Time Series', 'value': 'timeseries'},
    {'label': 'Scatter Plot', 'value': 'scatter'}
]


CARD_STYLE = {
    'width': '35vw',
    'max-height': '33vh',
    'min-height': '10vh',
    'padding': '10px',
    'margin': '15px',
    'background-color': '#333340'
}


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
    def __init__(self, id, vh=45, vw=45, show_selection=False, *args, **kwargs):
        self.base_id = id
        self._vh = vh
        self._vw = vw
        self._show_selection = show_selection
        dbc.Container.__init__(self, id=f'{self.base_id}_container', *args, **kwargs)
        self.children = []
        self.generate_components()

    def generate_components(self):
        self.children = [
            dcc.Graph(
                id=self.base_id,
                style={'height': f'{self._vh}vh', 'width': f'{self._vw}vw'},
                figure=Figure(layout=Layout(**LAYOUT_STYLE))
            ),
            dcc.Store(id=f'{self.base_id}_custom_data')
        ]
        if self._show_selection:
            self.children.append(html.Pre(id=f'{self.base_id}_selection', style={'color': '#fff'}))


class BaseCard(dbc.Card):
    """
    Class for artist/label/album cards
    """
    def __init__(self, row):
        self._entity = None
        self._id_field = None
        self._id_value = None
        self._object_id = None
        self._image_url = None
        self._profile = None
        self._title = None
        self.set_entity(row)
        dbc.Card.__init__(
            self,
            id=self.generate_id('card'),
            style=CARD_STYLE)
        self.children = []
        self.generate_components()

    def set_entity(self, row, j=0):
        """
        set the identity of this object
        :param row: database row
        :param j: column index of the id row (default 0)
        """
        self._entity, _ = row.index[j].split('_')
        self._id_field = row.index[j]
        self._id_value = row.values[j]
        self._object_id = {'field': self._id_field, 'value': self._id_value}
        self._image_url = row['image']
        self._profile = row['profile']
        self._title = row['name']

    def generate_id(self, object_type):
        _output = {'object': object_type}
        _output.update(self._object_id)
        return _output

    @property
    def profile(self):
        try:
            return self._profile[:1000]  # truncate to 1000 char
        except TypeError:
            return ''

    def generate_components(self):
        """
        Generate components of the card
        """
        self.children = [
            dbc.Row([
                dbc.Col([
                    dbc.CardImg(src=self._image_url),
                    dbc.CardImgOverlay(
                        dbc.Button('View Albums', id=self.generate_id('card_button'))
                    )
                ], width=4),
                dbc.Col([
                    html.H4(
                        self._title,
                        style={'color': '#fff', 'margin': '1rem'}),
                    html.P(self.profile, style={'color': '#fff'}),
                    dcc.Store(id=self.generate_id('card_store'), data=self._object_id)
                ], width=8)
            ]),
        ]

# -----------------------------------------------------------------------------
# - Main Layout ---------------------------------------------------------------
# -----------------------------------------------------------------------------


layout_1 = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1('Record Collection Analyzer', style=TITLE_STYLE),
        ]),
        dbc.Col([
            dbc.Button('Analyze', id='analyze_button')
        ])

    ]),
    dbc.Row([
        dbc.Col([
            GraphPlus(id='graph1', vh=50, vw=45, show_selection=False),
            GraphPlus(id='graph2', vh=50, vw=45, show_selection=False)
        ]),
        dbc.Col([
            dbc.Container(id='card_container', style={'overflow-y': 'scroll'}, fluid=True)
        ])
    ])
], fluid=True, id='main_container', style=MAIN_STYLE)
