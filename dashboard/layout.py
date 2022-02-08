from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from plotly.graph_objects import Layout, Figure
from plotter import LAYOUT_STYLE
from data_extractors import *
from database_util import get_metadata


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
    'margin': '4px',
    'width': '100%'
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
    'min-width': '14vw',
    'max-width': '14vw',
    'max-height': '10vh',
    'min-height': '10vh',
    'padding': '10px',
    'margin': '5px',
    'background-color': '#333340',
    'border-radius': '10px'
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
            dcc.Store(id=f'{self.base_id}_custom_data'),
            dcc.Store(id=f'{self.base_id}_entity')
        ]
        if self._show_selection:
            self.children.append(html.Pre(id=f'{self.base_id}_selection', style={'color': '#fff'}))


class BaseCard(dbc.Card):
    """
    Class for artist/label/album cards
    """
    def __init__(self, title, image, text, id_field, id_value):
        self._title = title
        self._image = image
        self._text = text
        self._id_field = id_field
        self._id_value = id_value
        self._object_id = {'field': self._id_field, 'value': self._id_value}
        dbc.Card.__init__(self, id=self.generate_id('card'), style=CARD_STYLE)
        self.children = []
        self.generate_components()

    @classmethod
    def from_row(cls, row):
        try:
            title = row['name']
        except:
            title = row['title']
        return cls(
            title=title,
            image=row['image'],
            text='',
            id_field=row.index[0],
            id_value=row.values[0],
        )

    @classmethod
    def from_discogs_item(cls, item):
        if isinstance(item, discogs_client.Artist):
            id_field = 'artist_id'
            title = item.name
        elif isinstance(item, discogs_client.Label):
            id_field = 'label_id'
            title = item.name
        elif isinstance(item, discogs_client.Release):
            id_field = 'release_id'
            title = item.title
        else:
            raise ValueError(f'unknown type of {item}: {type(item)}')
        return cls(
            title=title,
            image=get_image_url(item),
            text='',
            id_field=id_field,
            id_value=item.id
        )

    def generate_id(self, object_type):
        _output = {'object': object_type}
        _output.update(self._object_id)
        return _output

    def generate_components(self):
        """
        Generate components of the card
        """
        self.children = [
            dbc.Row([
                dbc.Col([
                    dbc.CardImg(src=self._image, id=self.generate_id('image')),
                    dcc.Store(id=self.generate_id('card_store'), data=self._object_id),
                ], width=4),
                dbc.Col([
                    dbc.CardBody([
                        html.H4(
                            self._title,
                            style={'color': '#FFF', 'margin': '5px'}),
                        dbc.Button('View Albums', id=self.generate_id('card_button'))
                    ])
                ])
            ]),

        ]

# -----------------------------------------------------------------------------
# - Main Layout ---------------------------------------------------------------
# -----------------------------------------------------------------------------


def artist_options():
    artists = get_metadata('artist')
    return [html.Option(value=a) for a in artists['name'].tolist()]


layout_1 = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1('Record Collection Analyzer', style=TITLE_STYLE),
        ], width='auto'),
        dbc.Col([
            dbc.Button('Analyze', id='analyze_button', style={'margin-top': '10px'})
        ], width='auto'),
        dbc.Col([
            dbc.Input(
                id='search-box',
                list='artists',
                type='text',
                style={'margin': '10px', 'width': '500px'}),
            html.Datalist(artist_options(), id='artists')
        ])
    ]),
    dbc.Row([
        dbc.Col([
            Options(
                id='axis_type',
                title='Axis Type',
                options=[
                    {'label': 'Log', 'value': 'log'},
                    {'label': 'Linear', 'value': 'linear'}
                ]
            ),
            GraphPlus(id='graph1', vh=45, vw=45, show_selection=False)
        ]),
        dbc.Col([
            dbc.Spinner([
                dbc.CardGroup(
                    id='card_container',
                    style={
                        'overflow': 'scroll',
                        'min-height': '50vh',
                        'max-height': '50vh',
                        'max-width': '45vw',
                        'min-width': '45vw'
                    }
                )
            ], color='info', type='grow', spinner_style={'height': '5rem', 'width': '5rem'})
        ])
    ]),
    dbc.Row([
        dbc.Col([
            Options(id='graph2_options', title='Measure', options=YAXIS_OPTIONS),
        ], width=4)
    ]),
    dbc.Row([
        dbc.Col([
            GraphPlus(id='graph2', vh=45, vw=90, show_selection=False, fluid=True)
        ])
    ])
], fluid=True, id='main_container', style=MAIN_STYLE)
