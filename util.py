import psycopg2
import discogs_client
import time
import yaml
import pandas as pd
import numpy as np
from numpy import array, where
from numpy.random import permutation, exponential
from psycopg2.extensions import register_adapter, AsIs
from yaml import Loader, Dumper
from json import dumps
from secrets import token_urlsafe


SCHEMA_NAME = 'public'

# historial price data table
MARKETPLACE_TABLE = 'marketplace'

# node tables
RELEASE_TABLE = 'releases'
ARTIST_TABLE = 'artists'
LABEL_TABLE = 'labels'

# edge tables
E_ARTIST_RELEASE = 'artist_release'
E_LABEL_RELEASE = 'label_release'

# views
PRICES_VIEW = 'prices'


def addapt_numpy_float64(numpy_float64):
    return AsIs(numpy_float64)


def addapt_numpy_int64(numpy_int64):
    return AsIs(numpy_int64)


register_adapter(np.float64, addapt_numpy_float64)
register_adapter(np.int64, addapt_numpy_int64)


# -----------------------------------------------------------------------------
# - basic i/o functions -------------------------------------------------------
# -----------------------------------------------------------------------------


def load_yaml(f):
    """
    load a yaml file into a dictionary
    :param f: yaml input file name
    :return: dictionary
    """
    with open(f) as stream:
        d = yaml.load(stream, Loader=Loader)
    return d


def write_yaml(data, fname):
    """
    output a dictionary as a yaml file
    :param data: dictionary
    :param fname: yaml output file name
    :return: None
    """
    if not fname.lower().endswith('yaml'):
        fname = fname.split('.')[0] + '.yaml'
    with open(fname, 'w') as stream:
        yaml.dump(data, stream, Dumper=Dumper)
    return None


def dump_json(d):
    """
    output dictionary as a json string
    :param d: dictionary
    :return: string
    """
    return dumps(d, indent=4, sort_keys=True)


def get_factor(attribute, traces, custom_data_labels):
    """
    extract custom data from selected points by name
    :param attribute: name of the variable to extract
    :param custom_data_labels: list of the column names in the points' customdata
    :param traces: selectedData attribute of a dcc.Graph
    :return: list of unique values of colname among the selected points in traces
    """
    var_index = where(array(custom_data_labels) == attribute)[0][0]
    values = [point['customdata'][var_index] for point in traces['points']]
    values = list(set(values))
    condition = {attribute: values}
    return condition


# -----------------------------------------------------------------------------
# - randomizing functions -----------------------------------------------------
# -----------------------------------------------------------------------------


def make_random_password(_bytes=16):
    """
    create a random password
    :param _bytes: password size in bytes
    :return: password string
    """
    return token_urlsafe(_bytes)


class Randomize(object):
    """
    a class for iterating in a random order
    """
    def __init__(self, iterable):
        self.iterable = iterable
        self.n = len(self.iterable)

    def __iter__(self):
        for i in permutation(self.n):
            yield self.iterable[i]


def sleep_random(quiet=False):
    """
    sleep for a random time (exponential distributed)
    :param quiet: if False, print the sleep time before sleeping
    :return: None
    """
    n = exponential(2, 1)[0]
    if not quiet:
        print(f'sleeping {round(n, 2)} seconds')
    time.sleep(n)
    return None


# -----------------------------------------------------------------------------
# - General database functions ------------------------------------------------
# -----------------------------------------------------------------------------


def validate_query(query):
    """
    validate SQL query and return a potentially modified query
    :param query: sql query string
    :return: sql query string
    """
    return query if query.endswith(';') else query + ';'


def write_rows(df, tbl):
    """
    Write rows of dataframe 'df' to the database table 'tbl'
    :param df: pandas data frame
    :param tbl: table name
    :return: None
    """
    col_names = ','.join(df.columns)
    n_col = df.shape[1]
    fmt = ','.join(['%s'] * n_col)
    with psycopg2.connect(**load_yaml('keys/database.yaml')) as conn:
        cur = conn.cursor()
        for idx, row in df.iterrows():
            query = (
                f"INSERT INTO {SCHEMA_NAME}.{tbl}({col_names})\n"
                f"VALUES ({fmt})\n"
                f"ON CONFLICT DO NOTHING")
            query = validate_query(query)
            try:
                cur.execute(query, row.values)
            except psycopg2.ProgrammingError as e:
                print({'query': query})
                print({'values': row})
                raise e
    return None


def make_condition_string(colname, n):
    """
    generate string of formatting text for use in SQL query
    :param n: number of values
        if n == 1: col = val
        if n > 1: col in (val, ...)
    :return:
    """
    if n == 1:
        _output = f"%s = %s"
    elif n > 1:
        fmt_list = ','.join(['%s'] * n)
        _output = f"{colname} in ({fmt_list})"
    else:
        raise ValueError('n must be greater than zero')
    return _output


def read_rows(tbl, **conditions):
    """
    read data from the database table tbl where conditions are true
    :param tbl: name of the database table
    :param conditions: keyword arguments of the form <column_name> = <value>
    :return: pandas data frame
    """
    query = f"SELECT * FROM {SCHEMA_NAME}.{tbl} \n"
    condition_values = None
    if len(conditions) > 0:
        condition_values = []
        condition_strings = []
        for colname, values in conditions.items():
            n = len(values)
            fmt = make_condition_string(colname, n)
            condition_strings.append(fmt)
            condition_values.extend(values)
        condition_string = ' AND '.join(condition_strings)
        query += f'WHERE {condition_string}'
    query = validate_query(query)
    with psycopg2.connect(**load_yaml('keys/database.yaml')) as conn:
        cur = conn.cursor()
        cur.execute(query, condition_values)
        output = pd.DataFrame(
            cur.fetchall(),
            columns=[col[0] for col in cur.description])
    return output


# -----------------------------------------------------------------------------
# - Data frame preparation functions ------------------------------------------
# -----------------------------------------------------------------------------


def get_image_url(item):
    try:
        output = item.images[0]['uri']
    except:
        output = ''
    return output


def get_profile(item):
    try:
        output = item.profile
    except:
        output = ''
    return output


def get_country(item):
    try:
        output = item.country
    except:
        output = ''
    return output


def prepare_price_data(release):
    """
    prepare data frame of price data from Release object
    :param release: Release object
    :return: pandas data frame
    """
    stats = release.marketplace_stats
    output = {
        'release_id': release.id
    }
    try:
        output.update({
            'lowest_price': stats.lowest_price.value,
            'currency': stats.lowest_price.currency,
            'num_for_sale': stats.num_for_sale
        })
    except AttributeError:
        pass
    return pd.DataFrame(output, index=[0])


def prepare_release_data(release):
    """
    produce data frame of release data from Release object
    :param release: Release object
    :return: pandas data frame
    """
    output = {
        'release_id': release.id,
        'title': release.title,
        'year': release.year,
        'country': get_country(release),
        'format': release.formats[0]['name']
    }
    try:
        output.update({
            'master_id': release.master.id
        })
    except AttributeError:
        pass
    return pd.DataFrame(output, index=[0])


def prepare_label_data(release):
    """
    prepare the label information and release-label links
    :param release: Release object
    :return: dict of release_id/label_id pairs, dict of labels
    """
    rid = release.id
    labels = release.labels
    n_labels = len(labels)
    labels = [{
        'label_id': label.id,
        'name': label.name,
        'profile': get_profile(label),
        'image': get_image_url(label)
    } for label in labels]
    label_release = [{
        'release_id': rid, 'label_id': label['label_id']
    } for label in labels]
    return (
        pd.DataFrame(label_release, index=range(n_labels)),
        pd.DataFrame(labels, index=range(n_labels))
    )


def prepare_artist_data(release):
    rid = release.id
    artists = release.artists
    n_artists = len(artists)
    artists = [{
        'artist_id': artist.id,
        'name': artist.name,
        'profile': get_profile(artist),
        'image': get_image_url(artist)
    } for artist in artists]
    artist_release = [{
        'artist_id': artist['artist_id'], 'release_id': rid
    } for artist in artists]
    return (
        pd.DataFrame(artist_release, index=range(n_artists)),
        pd.DataFrame(artists, index=range(n_artists))
    )


# -----------------------------------------------------------------------------
# - Database write functions --------------------------------------------------
# -----------------------------------------------------------------------------


def store_release_data(release, store_metadata=True):
    """
    store the marketplace stats and release info for a release
    :param release: Release object
    :param store_metadata: if False, store only the marketplace data
    :return: None
    """
    assert isinstance(release, discogs_client.Release), f'release is {type(release)}'
    print(f'Storing marketplace data for: {release.title} by {release.artists[0].name}')
    try:
        marketplace_data = prepare_price_data(release)
        write_rows(marketplace_data, MARKETPLACE_TABLE)
        if store_metadata:
            release_info = prepare_release_data(release)
            label_release, labels = prepare_label_data(release)
            artist_release, artists = prepare_artist_data(release)
            write_rows(release_info, RELEASE_TABLE)
            write_rows(label_release, E_LABEL_RELEASE)
            write_rows(labels, LABEL_TABLE)
            write_rows(artist_release, E_ARTIST_RELEASE)
            write_rows(artists, ARTIST_TABLE)
    except Exception as e:
        raise e
    return None


def get_release_data(**conditions):
    """
    get marketplace data from the local database for releases matching certain conditions
    :return: pandas data frame
    """
    df = read_rows(PRICES_VIEW, **conditions)
    df['country'].fillna('-', inplace=True)
    df['lowest_price'] = df['lowest_price'].astype(float)
    return df


def get_releases():
    """
    get all releases in local database
    :return: pandas data frame
    """
    return read_rows(RELEASE_TABLE)

