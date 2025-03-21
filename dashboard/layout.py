from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from plotly.graph_objects import Layout, Figure
from .plotter import LAYOUT_STYLE
from database.database_util import get_metadata
from palet.color_palets import onemorning


ENTITY_OPTIONS = [
    {'label': 'Country', 'value': 'country'},
    {'label': 'Label', 'value': 'label'},
    {'label': 'Artist', 'value': 'artist'},
    {'label': 'Album', 'value': 'album'},
    {'label': 'Song', 'value': 'song'}
]


ENTITY_MAP = dict(
    album=['release_id', 'title'],
    artist=['artist_id', 'artist'],
    country=['country', 'country'],
    label=['label_id', 'label'],
    song=['song_id', 'title']  # TODO: make song a valid option
)


MAIN_STYLE = {
    'font-family': 'helvetica',
    'background-color': "#" + onemorning[1],
    'min-height': '100vh',
    'min-width': '80vw',
    'max-width': '80vw'
}


TITLE_STYLE = {
    'color': '#EEEEEE',
    'background-color': "#" + onemorning[3],
    'margin': '8px',
    'width': '100%'
}


MEASURE_OPTIONS = [
    {'label': 'Median', 'value': 'median'},
    {'label': 'Mean', 'value': 'mean'},
    {'label': 'Min', 'value': 'min'},
    {'label': 'Max', 'value': 'max'},
]

LOG_LINEAR_OPTIONS = [
    {'label': 'Log', 'value': 'log'},
    {'label': 'Linear', 'value': 'linear'}
]

GRAPH_TYPES = [
    {'label': 'Time Series', 'value': 'timeseries'},
    {'label': 'Scatter Plot', 'value': 'scatter'}
]

ARTIST_CARD_STYLE = {
    'min-width': '14vw',
    'max-width': '14vw',
    'max-height': '10vh',
    'min-height': '10vh',
    'padding': '10px',
    'margin': '5px',
    'background-color': "#" + onemorning[1],
    'border-radius': '10px'
}

ALBUM_CARD_STYLE = {
    'min-width': '30vw',
    'max-width': '30vw',
    'min-height': '30vh',
    'max-height': '30vh',
    'padding': '10px',
    'margin': '5px',
    'background-color': "#" + onemorning[1],
    'border-radius': '10px'
}

CARD_GROUP_STYLE = {
    'overflow': 'scroll',
    'min-height': '50vh',
    'max-height': '50vh',
    'max-width': '45vw',
    'min-width': '45vw'
}


YAXIS_OPTIONS = [
    {'label': 'Lowest Price', 'value': 'lowest_price'},
    {'label': 'Number for Sale', 'value': 'num_for_sale'}
]


RADIO_STYLE_ARGS = dict(
    style={'margin': '2px', 'text-align': 'left'},
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
                    html.H4(title, style={'color': '#fff', 'text-align': 'left'})
                ],width=3),
                dbc.Col([
                    dcc.RadioItems(
                        id=id,
                        options=options,
                        value=options[default_option]['value'],
                        **RADIO_STYLE_ARGS
                    )
                ])
            ], justify='center')
        ]


# --------------------------------------------------------------------------------------------
# - Graph with entity and custom data name storage -------------------------------------------
# --------------------------------------------------------------------------------------------


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
                style={
                    'height': f'{self._vh} vh',
                    'min-height': f'{self._vh} vh',
                    'max-height': f'{self._vh} vh',
                    'width': f'{self._vw} vw',
                    'min-width': f'{self._vw} vw',
                    'max-width': f'{self._vw} vw'
                },
                figure=Figure(layout=Layout(**LAYOUT_STYLE))
            ),
            dcc.Store(id=f'{self.base_id}_custom_data'),
            dcc.Store(id=f'{self.base_id}_entity')
        ]
        if self._show_selection:
            self.children.append(html.Pre(id=f'{self.base_id}_selection', style={'color': '#fff'}))


# --------------------------------------------------------------------------------------------
# - Base Card --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------


class BaseCard(dbc.Card):
    """
    Class for artist/label/album cards

    When instances of this card class are present in a layout
    callback functions can be triggered by changes to any of
    the cards in the layout. This allows for counting of button
    clicks with a special processing function get_buttons_clicked
    in plotter_util.py

    """
    def __init__(self, title, image, id_field, id_value, style, *args, **kwargs):
        """
        Instantiate a Card that is a subclass of a dash-bootstrap-components Card
        :param title: card title
        :param image: card image url
        :param id_field: name of the id field such as release_id, artist_id, label_id
        :param id_value: id value of the artist/label/release that this card represents
        :param style: dict of css styles
        """
        self._title = title
        self._image = image
        self._id_field = id_field
        self._id_value = str(id_value)
        self._object_id = {'field': self._id_field, 'value': self._id_value}
        dbc.Card.__init__(self, id=self.generate_id('card'), style=style)

    def generate_id(self, object_type):
        """
        generate a component id for a child component of this card
        :param object_type: type of child component (button, image, etc...)
        :return: dict
        """
        _output = {'object': object_type}
        _output.update(self._object_id)
        return _output


# --------------------------------------------------------------------------------------------
# - Artist Card ------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------


class ArtistCard(BaseCard):
    def __init__(self, title, image, id_field, id_value, style):
        """
        Instantiate a Card that is a subclass of a dash-bootstrap-components Card
        :param title: card title
        :param image: card image url
        :param id_field: name of the id field such as release_id, artist_id, label_id
        :param id_value: id value of the artist/label/release that this card represents
        :param style: dict of css styles
        """
        BaseCard.__init__(self, title, image, id_field, id_value, style)
        self.children = []
        self.generate_components()

    @classmethod
    def from_row(cls, row):
        """
        Instantiate this class using a row from a database table
        :param row: Series, row of a db table representing an artist, release, or label
        """
        return cls(
            title=row['name'],
            image=row['image'],
            id_field=row.index[0],
            id_value=row.values[0],
            style=ARTIST_CARD_STYLE
        )

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
                        html.H5(
                            self._title,
                            style={'color': '#FFF', 'margin': '5px'}),
                        dbc.Button('View Albums', id=self.generate_id('card_button'))
                    ])
                ])
            ]),
        ]


# --------------------------------------------------------------------------------------------
# - Album Card -------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------


class AlbumCard(BaseCard):
    def __init__(self, title, image, catno, artist, label, year, country, format, format_details, id_field, id_value, style):
        """
        Instantiate a Card that is a subclass of a dash-bootstrap-components Card
        :param title: card title
        :param image: card image url
        :param id_field: name of the id field such as release_id, artist_id, label_id
        :param id_value: id value of the artist/label/release that this card represents
        :param style: dict of css styles
        """
        BaseCard.__init__(self, title, image, id_field, id_value, style)
        self._catno = catno
        self._artist = artist
        self._label = label
        self._year = year
        self._country = country
        self._format = format
        self._format_details = format_details
        self.children = []
        self.generate_components()

    @classmethod
    def from_row(cls, row):
        """
        Instantiate this class using a row from a database table
        :param row: Series, row of a db table representing an artist, release, or label
        """
        # print(row)
        return cls(
            title=row['title'],
            image=row['image'],
            catno=row['catno'],
            year=row['year'],
            artist=row['artist'],
            label=row['label'],
            country=row['country'],
            format=row['format'],
            format_details=row['format_details'],
            id_field=row.index[0],
            id_value=row.values[0],
            style=ALBUM_CARD_STYLE
        )

    @property
    def title(self):
        output = html.Div([
            html.H5(
                f'{self._title} ({self._catno})',
                style={'color': '#FFF', 'margin': '5px'}),
            html.P(
                f'{self._format}, {self._format_details}',
                style={'color':'#FFF', 'margin': '5px'}
            ),
            html.P(
                f'by {self._artist}',
                style={'color': '#FFF', 'margin': '5px'}
            ),
            html.P(
                f'{self._label} ({self._country} {self._year})',
                style={'color': '#FFF', 'margin': '5px'}
            ),
        ], style={'margin': '0px', 'padding': '0px'})
        return output

    def generate_components(self):
        self.children = [
            dbc.Row([
                dbc.Col([
                    dbc.CardImg(src=self._image, id=self.generate_id('image'))
                ], width=5),
                dbc.Col([
                    dbc.CardBody([
                        self.title,
                        dcc.Link(
                            'View Discogs Marketplace',
                            href=f'https://www.discogs.com/sell/release/{self._id_value}',
                            target='_blank'
                        )
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



class SearchResult(dbc.Card):
    def __init__(self, item):
        """
        represent a search result
        :param item: discogs client object (
        """
    pass



# main_layout = dbc.Container([
#     dbc.Row([
#         dbc.Col([
#             html.H1('Record Collection Analyzer', style=TITLE_STYLE),
#         ], width='auto'),
#         dbc.Col([
#             dbc.Button('Analyze', id='analyze_button', style={'margin-top': '10px'})
#         ], width='auto'),
#         dbc.Col([
#             dbc.Input(
#                 id='search_box',
#                 list='artists',
#                 type='text',
#                 debounce=True,
#                 style={'margin': '10px', 'width': '500px'}),
#             html.Datalist(artist_options(), id='artists')
#         ])
#     ]),
#     dbc.Row([
#         dbc.Col([
#             Options(
#                 id='axis_type',
#                 title='Axis Type',
#                 options=LOG_LINEAR_OPTIONS
#             ),
#             Options(
#                 id='measure',
#                 title='Measure Function',
#                 options=MEASURE_OPTIONS,
#                 default_option=1
#             ),
#             dbc.Spinner([
#                 GraphPlus(id='graph1', vh=45, vw=45, show_selection=False)
#             ], type='grow', color='warning', spinner_style={'width': '10rem', 'height': '10rem'})
#         ], width='auto'),
#         dbc.Col([
#             dbc.Spinner([
#                 dbc.CardGroup(
#                     id='card_container',
#                     style=CARD_GROUP_STYLE
#                 )
#             ], color='warning', type='grow', spinner_style={'height': '5rem', 'width': '5rem'})
#         ])
#     ]),
#     dbc.Row([
#         dbc.Col([
#             Options(id='graph2_options', title='Measure', options=YAXIS_OPTIONS),
#             GraphPlus(id='graph2', vh=45, vw=60, show_selection=False, fluid=True)
#         ]),
#         dbc.Col(id='release_card_col')
#     ])
# ], fluid=True, id='main_container', style=MAIN_STYLE)


main_layout = dbc.Container([
    html.H1('Collection Analyser 2.0.0', style={'color': 'white'}),
    dbc.Row([
        dbc.Col([
            Options(
                id='entity_options',
                title='Entity',
                default_option=2,
                options=ENTITY_OPTIONS
            )
        ])
    ], justify='center'),
    dbc.Row([
        dbc.Col([], width=3),
        dbc.Col([
            dbc.Input(
                id='search_text',
                type='text',
                debounce=True,
                style={
                    'margin': '10px',
                    'width': '300px'
                }
            )
        ]),
        dbc.Col([
            dbc.Button([
                html.H5('Search')
            ], color='secondary', id='search_button')
        ]),
        dbc.Col([], width=3)
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Collapse([
                dbc.CardGroup(id='search_results')
            ], id='collapse1')
        ])
    ]),
    dbc.Row([
        dbc.Col([
            GraphPlus(
                id='music_relationship_plot',
                vh=95, vw=95,
                show_selection=True,
                fluid=True
            )
        ])
    ])

], fluid=True, id='main_container', style=MAIN_STYLE)







