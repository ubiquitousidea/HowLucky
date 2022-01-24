import discogs_client
from sql.schema import *
from data_extractors import *
from database_util_mysql import DBMySQL
from database_util_postgres import DBPostgreSQL


# -----------------------------------------------------------------------------
# - Database storage functions ------------------------------------------------
# -----------------------------------------------------------------------------

def store_release_data(release, store_metadata=True, store_prices=True, db='mysql'):
    """
    store the marketplace stats and release info for a release
    :param release: Release object
    :param store_metadata: if True, store release, artist, label data
    :param store_prices: if True, store prices in marketplace table
    :param db: str, which database to use (mysql or postgres)
    :return: None
    """
    assert isinstance(release, discogs_client.Release), f'release is {type(release)}'
    print(f'Storing marketplace data for: {release.title} by {release.artists[0].name}')

    if db == 'postgres':
        _db = DBPostgreSQL(DB_KEYS_POSTGRES)
    elif db == 'mysql':
        _db = DBMySQL(DB_KEYS_MYSQL)
    else:
        raise ValueError(f'unknown database {db}')
    if store_prices:
        marketplace_data = prepare_price_data(release)
        _db.insert_rows(marketplace_data, MARKETPLACE_TABLE)
    if store_metadata:
        try:
            release_info = prepare_release_data(release)
            _db.insert_rows(release_info, RELEASE_TABLE)

            artist_release, artists = prepare_artist_data(release)
            _db.insert_rows(artist_release, E_ARTIST_RELEASE)
            _db.insert_rows(artists, ARTIST_TABLE)

            label_release, labels = prepare_label_data(release)
            _db.insert_rows(label_release, E_LABEL_RELEASE)
            _db.insert_rows(labels, LABEL_TABLE)
        except:
            pass
    return None


# -----------------------------------------------------------------------------
# - Database retrieval functions ----------------------------------------------
# -----------------------------------------------------------------------------


def get_price_data(**conditions):
    """
    get marketplace data from the local database for releases matching certain conditions
    :return: pandas data frame
    """

    df = read_rows(PRICES_VIEW, **conditions)
    df = df.sort_values(['release_id', 'when'])
    df['country'].fillna('-', inplace=True)
    df['lowest_price'] = df['lowest_price'].astype(float)
    return df


def get_metadata(entity, **conditions):
    """
    get metadata on
    :param entity:
    :param conditions:
    :return:
    """
    if entity == 'label':
        output = read_rows(LABEL_TABLE, **conditions)
    elif entity == 'artist':
        output = read_rows(ARTIST_TABLE, **conditions)
    elif entity == 'album':
        output = read_rows(RELEASE_TABLE, **conditions)
    else:
        raise TypeError(f'bad entity {entity}')
    return output
