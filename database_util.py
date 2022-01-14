import numpy as np
import psycopg2
from psycopg2.extensions import register_adapter, AsIs
from data_extractors import *
from sql.schema import *


def adapt_numpy_float64(numpy_float64):
    return AsIs(numpy_float64)


def adapt_numpy_int64(numpy_int64):
    return AsIs(numpy_int64)


register_adapter(np.float64, adapt_numpy_float64)
register_adapter(np.int64, adapt_numpy_int64)


# -----------------------------------------------------------------------------
# - General database functions ------------------------------------------------
# -----------------------------------------------------------------------------


def punctuate_query(query):
    """
    punctuate SQL query and return a potentially modified query
    :param query: sql query string
    :return: sql query string
    """
    return query if query.endswith(';') else query + ';'


def write_rows(df, tbl, returning=None):
    """
    Write rows of dataframe 'df' to the database table 'tbl'
    :param df: pandas data frame
    :param tbl: table name
    :param returning:
    :return: None
    """
    col_names = ','.join(df.columns)
    n_col = df.shape[1]
    fmt = ','.join(['%s'] * n_col)
    with psycopg2.connect(**DATABASE_KEYS) as conn:
        cur = conn.cursor()
        for idx, row in df.iterrows():
            query = f"INSERT INTO {SCHEMA_NAME}.{tbl}({col_names})\nVALUES ({fmt})\n"
            query += f'RETURNING {returning}' if returning is not None else ''
            query += f"ON CONFLICT DO NOTHING"
            query = punctuate_query(query)
            try:
                cur.execute(query, row.values)
            except psycopg2.ProgrammingError as e:
                print({'query': query})
                print({'values': row})
                raise e
    return None


def read_rows(tbl, **conditions):
    """
    read data from the database table tbl where conditions are true
    :param tbl: name of the database table
    :param conditions: keyword arguments of the form <column_name> = <value>
    :return: pandas data frame
    """
    query = f"SELECT * FROM {SCHEMA_NAME}.{tbl} \n"
    cond_values = None  # this name needs to be defined for cur.execute to run
    if len(conditions) > 0:
        cond_values = []
        format_st = []
        for colname, values in conditions.items():
            n = len(values)
            _ = ','.join(['%s'] * n)
            fmt = f'{colname} in ({_})'
            format_st.append(fmt)
            cond_values.extend(values)
        condition_string = ' AND '.join(format_st)
        query += f'WHERE {condition_string}'
    query = punctuate_query(query)
    with psycopg2.connect(**DATABASE_KEYS) as conn:
        cur = conn.cursor()
        cur.execute(query, cond_values)
        output = pd.DataFrame(
            cur.fetchall(),
            columns=[col[0] for col in cur.description])
    return output

# -----------------------------------------------------------------------------
# - Database storage functions ------------------------------------------------
# -----------------------------------------------------------------------------


def store_release_data(release, store_metadata=True, store_prices=True):
    """
    store the marketplace stats and release info for a release
    :param release: Release object
    :param store_metadata: if True, store release, artist, label data
    :param store_prices: if True, store prices in marketplace table
    :return: None
    """
    assert isinstance(release, discogs_client.Release), f'release is {type(release)}'
    print(f'Storing marketplace data for: {release.title} by {release.artists[0].name}')
    if store_prices:
        marketplace_data = prepare_price_data(release)
        write_rows(marketplace_data, MARKETPLACE_TABLE)
    if store_metadata:
        try:
            release_info = prepare_release_data(release)
            write_rows(release_info, RELEASE_TABLE)
            artist_release, artists = prepare_artist_data(release)
            write_rows(artist_release, E_ARTIST_RELEASE)
            write_rows(artists, ARTIST_TABLE)
            label_release, labels = prepare_label_data(release)
            write_rows(label_release, E_LABEL_RELEASE)
            write_rows(labels, LABEL_TABLE)
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
