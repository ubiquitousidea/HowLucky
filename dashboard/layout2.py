from dashboard.image_cache import ImageCache
import dash_bootstrap_components as dbc
from dash import html, dcc, get_asset_url
from discogs_identity import dclient
from database.database_util_postgres import DBPostgreSQL
from sql.schema import DB_KEYS_POSTGRES


DB = DBPostgreSQL(DB_KEYS_POSTGRES)


def make_button(text, btn_id):
    return dbc.Button(
        html.P(text, className='button_text'), 
        id=btn_id, color='secondary', style={'width':'20vw'})


def get_artist_options():
    tbl = DB.read_rows('artists')
    return [
        {'label': row['name'], 'value': {'id': row.artist_id, 'name': row['name']}}
        for idx, row in tbl.iterrows()
    ]


MAIN_LAYOUT = dbc.Container([
    dbc.Row([
        html.H1('Vinyl Collection Analyser', className='text-center page-cell')
    ]),
    dbc.Row([
        dcc.Dropdown(
            id='main_dropdown', 
            options=get_artist_options(), 
            placeholder='Select Artist'),
        dcc.Store(id='dropdown_entity')
    ], class_name='page_cell'),
    dbc.Row([
        dbc.Col(id="column_1", width=12, lg=6),
        dbc.Col(id="column_2", width=12, lg=6),
        dbc.Col(id='column_3', width=12)
    ], class_name='page_cell')
], fluid=True, id='main_layout')



def make_artist_card(v):
    # create artist card using information from the discogs API
    # v: dict, a dropdown value
    image_url = ImageCache().get_artist_image(v['id'])
    artist = dclient.artist(v['id'])
    main_text = artist.profile
    button_id = {
        'widget_type': 'button',
        'entity': 'artist', 
        'id': v['id'], 
        'desired_entity': 'release'}
    return dbc.Card([
        dbc.CardHeader(html.H2(v['name'])),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Img(
                        src=image_url,
                        alt=f"Picture of {v['name']}",
                        className='img-fluid'
                    )
                ], width=4),
                dbc.Col([
                    html.P(main_text, className='bio_text')
                ], width=8)
            ]),
        ]),
        dbc.CardFooter([
            dbc.Button('See Releases', id=button_id, color='secondary')
        ], class_name='entity_card_footer')
    ], class_name='entity_card')


def make_release_card(rel):
    # create a release card using information from the local database
    # rel: row from the prices view of the vinyl database
    im = ImageCache()
    return dbc.Card([
        dbc.CardHeader(html.H2(f'{rel.title} ({rel.catno})')),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Img(
                        src=im.get_release_image(rel.release_id), 
                        className='img-fluid', alt=f'Picture of {rel.title}'
                    )
                ], width=4),
                dbc.Col([
                    html.P(f'by {rel.artist}'),
                    html.P(f"{rel.label} ({rel.country} {rel.year if rel.year else ''})"),
                    html.P(f"{rel.num_for_sale} for sale from {rel.lowest_price}")
                ], width=8)
            ])
        ]),
        dbc.CardFooter([
            dbc.ButtonGroup([
                dbc.Button('Show Trends', id={
                    'widget_type': 'graphit',
                    'entity': 'release',
                    'id': rel.release_id,
                    'graph_type': 'timeseries'
                }, color='secondary'),
                dbc.Button([
                    dcc.Link(
                        'Buy on Discogs',
                        href=f'https://www.discogs.com/sell/release/{rel.release_id}',
                        target='_blank'
                    )
                ], style={'background-color':'white'})
            ])
        ], class_name='entity_card_footer')
    ], class_name='entity_card')
