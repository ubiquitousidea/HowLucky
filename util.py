import time
import yaml
import psycopg2
from psycopg2.extensions import register_adapter, AsIs
import pandas as pd
import discogs_client
from yaml import Loader, Dumper
from secrets import token_urlsafe
import numpy as np
from numpy import array, where
from numpy.random import permutation, exponential


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


def get_factor(attribute, traces, custom_data_labels):
    """
    extract custom data from selected points by name
    :param attribute: name of the variable to extract
    :param custom_data_labels: a list of the column names represented in the points'
        customdata attribute
    :param traces: plotly/dash traces, selectedData attribute of a dcc.Graph for example
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
        value = list(set(value))  # use only unique values
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
        'country': release.country,
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


def store_release_data(release):
    """
    store the marketplace stats and release info for a release
    :param release: Release object
    :return: None
    """
    assert isinstance(release, discogs_client.Release), f'release is {type(release)}'
    print(f'Storing marketplace data for: {release.title} by {release.artists[0].name}')
    try:
        marketplace_data = prepare_price_data(release)
        release_info = prepare_release_data(release)
        label_release, labels = prepare_label_data(release)
        artist_release, artists = prepare_artist_data(release)
        write_rows(marketplace_data, MARKETPLACE_TABLE)
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


# -----------------------------------------------------------------------------
# - visual things -------------------------------------------------------------
# -----------------------------------------------------------------------------


# class Colormaker(object):
#     def __init__(self, image):
#         assert isinstance(image, )
#         self.img = image
