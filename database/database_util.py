from sql.schema import *
from database.data_extractors import *
from database.database_util_mysql import DBMySQL
from database.database_util_postgres import DBPostgreSQL


# -----------------------------------------------------------------------------
# - Database storage functions ------------------------------------------------
# -----------------------------------------------------------------------------
def get_db_object(db, noisy=False):
    """
    :param db: str, postgres or mysql
    :param noisy: if True, print database being used
    :return: BaseDB object
    """
    if db == 'postgres':
        if noisy:
            print(f"USING POSTGRES {DB_KEYS_POSTGRES['dbname']}")
        _db = DBPostgreSQL(DB_KEYS_POSTGRES)
    elif db == 'mysql':
        if noisy:
            print(f"USING MYSQL DATABASE {DB_KEYS_MYSQL['database']}")
        _db = DBMySQL(DB_KEYS_MYSQL)
    else:
        raise ValueError(f'unknown database {db}')
    return _db


def store_release_metadata(db, release):
    """
    store release metadata in the chosen database
    :param db: database object (DBPostgreSQL or DBMySQL)
    :param release: discogs_client.Release object
    :return: None
    """
    print(f'Storing release metadata for: {release.title} by {release.artists[0].name}')

    release_info = prepare_release_data(release)
    db.insert_rows(release_info, RELEASE_TABLE)

    artist_release, artists = prepare_artist_data(release)
    db.insert_rows(artist_release, E_ARTIST_RELEASE)
    db.insert_rows(artists, ARTIST_TABLE)

    label_release, labels = prepare_label_data(release)
    db.insert_rows(label_release, E_LABEL_RELEASE)
    db.insert_rows(labels, LABEL_TABLE)
    return None


def store_release_data(release, store_metadata=True, store_prices=True, db=DB_CHOICE):
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
    _db = get_db_object(db)
    if store_prices:
        marketplace_data = prepare_price_data(release)
        _db.insert_rows(marketplace_data, MARKETPLACE_TABLE)
    if store_metadata:
        try:
            store_release_metadata(_db, release)
        except:
            pass
    return None


# -----------------------------------------------------------------------------
# - Database retrieval functions ----------------------------------------------
# -----------------------------------------------------------------------------


def get_price_data(db=DB_CHOICE, **conditions):
    """
    get marketplace data from the local database for releases matching certain conditions
    :param db: str, which database to use (mysql or postgres)
    :return: pandas data frame
    """
    _db = get_db_object(db)
    df = _db.read_rows(PRICES_VIEW, **conditions)
    df = df.sort_values(['release_id', 'when'])
    # print(df.columns)
    df['country'].fillna('-', inplace=True)
    df['lowest_price'] = df['lowest_price'].astype(float)
    return df


def get_metadata(entity, db=DB_CHOICE, **conditions):
    _db = get_db_object(db)
    if entity == 'label':
        output = _db.read_rows(LABEL_TABLE, **conditions)
    elif entity == 'artist':
        output = _db.read_rows(ARTIST_TABLE, **conditions)
    elif entity == 'album':
        output = _db.read_rows(RELEASE_TABLE, **conditions)
    else:
        output = _db.read_rows(entity, **conditions)
    return output
