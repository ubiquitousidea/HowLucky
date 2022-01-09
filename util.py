import time
import yaml
import psycopg2
import pandas as pd
import discogs_client
from yaml import Loader, Dumper
from secrets import token_urlsafe
from numpy.random import permutation, normal, exponential
from numpy import abs
from PIL import Image


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


def sleep_random():
    """
    sleep for a random time (exponential distributed)
    :return: None
    """
    n = exponential(2, 1)[0]
    print(f'sleeping {round(n, 2)} seconds')
    time.sleep(n)
    return None


# -----------------------------------------------------------------------------
# - General database functions ------------------------------------------------
# -----------------------------------------------------------------------------


SCHEMA_NAME = 'public'
MARKETPLACE_TABLE = 'marketplace'
RELEASE_TABLE = 'releases'
PRICES_VIEW = 'prices'


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
            cur.execute(query, row.values)
    return None


def make_condition_string(col_name, value):
    """
    construct sql condition string.
        if single value, result is of the form: 'col=value'.
        if list, use 'col in (values...)'
    :param col_name: name of the column where condition applies
    :param value: str or list of str, matching value(s)
    :return: sql string
    """
    if isinstance(value, (list, tuple)):
        quoted_values = [f"'{val}'" for val in value]
        value_list = '(' + ','.join(quoted_values) + ')'
        _output = f"{col_name} in {value_list}"
    else:
        _output = f"{col_name} = {value}"
    return _output


def read_rows(tbl, **conditions):
    """
    read data from the database table tbl where conditions are true
    :param tbl: name of the database table
    :param conditions: keyword arguments of the form <column_name> = <value>
    :return: pandas data frame
    """
    query = f"SELECT * FROM {SCHEMA_NAME}.{tbl} \n"
    if len(conditions) > 0:
        cond = [make_condition_string(col_name, value) for col_name, value in conditions.items()]
        cond = ' AND '.join(cond)
        query += f'WHERE {cond}'
    query = validate_query(query)
    with psycopg2.connect(**load_yaml('keys/database.yaml')) as conn:
        cur = conn.cursor()
        cur.execute(query)
        output = pd.DataFrame(
            cur.fetchall(),
            columns=[col[0] for col in cur.description])
    return output


# -----------------------------------------------------------------------------
# - Data frame preparation functions ------------------------------------------
# -----------------------------------------------------------------------------


def prepare_price_data(release, owned):
    """
    prepare data frame of price data from Release object
    :param release: Release object
    :param owned:
    :return: pandas data frame
    """
    stats = release.marketplace_stats
    output = {
        'release_id': release.id,
        'owned': owned
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
        'artist': release.artists[0].name,
        'artist_id': release.artists[0].id,
        'year': release.year,
        'country': release.country
    }
    try:
        output.update({
            'master_id': release.master.id
        })
    except AttributeError:
        pass
    return pd.DataFrame(output, index=[0])


# -----------------------------------------------------------------------------
# - Database write functions --------------------------------------------------
# -----------------------------------------------------------------------------


def store_release_data(release, owned=False):
    """
    store the marketplace stats and release info for a release
    :param release: Release object
    :param owned: boolean, whether or not the title is currently in the collection
    :return: None
    """
    assert isinstance(release, discogs_client.Release), f'release is {type(release)}'
    print(f'Storing marketplace data for: {release.title} by {release.artists[0].name}')
    write_rows(
        prepare_price_data(release, owned),
        tbl=MARKETPLACE_TABLE)
    write_rows(
        prepare_release_data(release),
        tbl=RELEASE_TABLE)
    return None


def get_release_data(**conditions):
    """
    get marketplace data from the local database for releases matching certain conditions
    :return: pandas data frame
    """
    df = read_rows(PRICES_VIEW, **conditions)
    df['country'].fillna('-', inplace=True)
    return df


def get_releases():
    """
    get all releases in local database
    :return: pandas data frame
    """
    return read_rows(RELEASE_TABLE)


# -----------------------------------------------------------------------------
# - visual things -------------------------------------------------------------
# -----------------------------------------------------------------------------


# class Colormaker(object):
#     def __init__(self, image):
#         assert isinstance(image, )
#         self.img = image
