from sql.schema import *
from database.data_extractors import *
from database.database_util_postgres import DBPostgreSQL


# -----------------------------------------------------------------------------
# - Database storage functions ------------------------------------------------
# -----------------------------------------------------------------------------
def get_db_object(db, noisy=False):
    return


def store_release_metadata(db, release):
    """
    store release metadata in the chosen database
    :param db: database object (DBPostgreSQL or DBMySQL)
    :param release: discogs_client.Release object
    :return: None
    """
    print(f"Storing release metadata for: {release.title} by {release.artists[0].name}")

    release_info = prepare_release_data(release)
    db.insert_rows(release_info, RELEASE_TABLE)

    artist_release, artists = prepare_artist_data(release)
    db.insert_rows(artist_release, E_ARTIST_RELEASE)
    db.insert_rows(artists, ARTIST_TABLE)

    label_release, labels = prepare_label_data(release)
    db.insert_rows(label_release, E_LABEL_RELEASE)
    db.insert_rows(labels, LABEL_TABLE)
    return None


def store_release_data(db, release, store_metadata):
    """
    store the marketplace stats and release info for a release
    :param release: Release object
    :param store_metadata: if True, store release, artist, label data
    :param store_prices: if True, store prices in marketplace table
    :param db: str, which database to use (mysql or postgres)
    :return: None
    """
    assert isinstance(release, discogs_client.Release), f"release is {type(release)}"
    print(f"Storing marketplace data for: {release.title} by {release.artists[0].name}")
    marketplace_data = prepare_price_data(release)
    db.insert_rows(marketplace_data, MARKETPLACE_TABLE)
    if store_metadata:
        store_release_metadata(db, release)


# -----------------------------------------------------------------------------
# - Database retrieval functions ----------------------------------------------
# -----------------------------------------------------------------------------


def get_price_data(db, **conditions):
    """
    get marketplace data from the local database for releases matching certain conditions
    :param db: str, which database to use (mysql or postgres)
    :return: pandas data frame
    """
    df = db.read_rows(PRICES_VIEW, **conditions)
    df = df.sort_values(["release_id", "when"])
    df["country"].fillna("-", inplace=True)
    df["lowest_price"] = df["lowest_price"].astype(float)
    return df


def get_metadata(db, entity, **conditions):
    if entity == "label":
        output = db.read_rows(LABEL_TABLE, **conditions)
    elif entity == "artist":
        output = db.read_rows(ARTIST_TABLE, **conditions)
    elif entity == "album":
        output = db.read_rows(RELEASE_TABLE, **conditions)
    else:
        output = db.read_rows(entity, **conditions)
    return output
