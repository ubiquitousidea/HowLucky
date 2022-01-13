import discogs_client
import pandas as pd


# -----------------------------------------------------------------------------
# - Data frame preparation functions ------------------------------------------
# -----------------------------------------------------------------------------


def just_try(func):
    """
    decorator to default object lookup failure to return an empty string
    :param func: function to be decorated
    :return: function that returns blank string if call fails
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except:
            return None
    return wrapper


@just_try
def get_image_url(item):
    assert isinstance(item, discogs_client.Release)
    return item.images[0]['uri']


@just_try
def get_catno_url(label):
    assert isinstance(label, discogs_client.Label)
    return label.data['catno']


@just_try
def get_thumb_url(item):
    assert isinstance(item, (
        discogs_client.Label,
        discogs_client.Artist,
        discogs_client.Release,
        discogs_client.Master
    ))
    return item.thumb


@just_try
def get_profile(item):
    assert isinstance(item, (
        discogs_client.Label,
        discogs_client.Artist
    ))
    return item.profile


@just_try
def get_country(item):
    assert isinstance(item, discogs_client.Release)
    return item.country


@just_try
def get_lowest_price(stats):
    return stats.lowest_price.value


@just_try
def get_lowest_price_currency(stats):
    return stats.lowest_price.currency


@just_try
def get_num_for_sale(stats):
    return stats.num_for_sale


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
            'lowest_price': get_lowest_price(stats),
            'currency': get_lowest_price_currency(stats),
            'num_for_sale': get_num_for_sale(stats)
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
        'image': get_image_url(label),
        'thumb': get_thumb_url(label)
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

