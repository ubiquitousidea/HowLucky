import discogs_client
import pandas as pd
from util import just_try

# -----------------------------------------------------------------------------
# - Data frame preparation functions ------------------------------------------
# -----------------------------------------------------------------------------


@just_try
def get_image_url(item):
    return item.images[0]['uri']


@just_try
def get_catno(release):
    return release.labels[0].data['catno']


@just_try
def get_thumb_url(item):
    return item.thumb


@just_try
def get_title(release):
    return release.title


@just_try
def get_profile(item):
    assert isinstance(item, (
        discogs_client.Label,
        discogs_client.Artist
    ))
    return item.profile


@just_try
def get_country(release):
    return release.country


@just_try
def get_year(release):
    return release.year


@just_try
def get_format(release):
    return release.formats[0]['name']


@just_try
def get_release_text(release):
    return release.formats[0]['text']


@just_try
def get_master_id(release):
    return release.master.id


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
        'release_id': release.id,
        'lowest_price': get_lowest_price(stats),
        'currency': get_lowest_price_currency(stats),
        'num_for_sale': get_num_for_sale(stats)
    }
    return pd.DataFrame(output, index=[0])


def prepare_release_data(release):
    """
    produce data frame of release data from Release object
    :param release: Release object
    :return: pandas data frame
    """
    output = {
        'release_id': release.id,
        'title': get_title(release),
        'year': get_year(release),
        'country': get_country(release),
        'format': get_format(release),
        'catno': get_catno(release),
        'master_id': get_master_id(release),
        'image': get_image_url(release)
    }
    return pd.DataFrame(output, index=[0])


def prepare_label_data(release):
    """
    prepare the label information and release-label links
    :param release: Release object
    :return: dataframe, dataframe
    """
    rid = release.id
    n_labels = len(release.labels)
    labels = [{
        'label_id': label.id,
        'name': label.name,
        'image': get_image_url(label)
    } for label in release.labels]
    label_release = [{
        'release_id': rid,
        'label_id': label['label_id'],
        'label_rank': idx
    } for idx, label in enumerate(labels)]
    return (
        pd.DataFrame(label_release, index=range(n_labels)),
        pd.DataFrame(labels, index=range(n_labels))
    )


def prepare_artist_data(release):
    """
    prepare the artist data and release/artist link data
    :param release: Release object
    :return: dataframe, dataframe
    """
    rid = release.id
    artists = release.artists
    n_artists = len(artists)
    artists = [{
        'artist_id': artist.id,
        'name': artist.name,
        'image': get_image_url(artist)
    } for artist in artists]
    artist_release = [{
        'release_id': rid,
        'artist_id': artist['artist_id'],
        'artist_rank': idx
    } for idx, artist in enumerate(artists)]
    return (
        pd.DataFrame(artist_release, index=range(n_artists)),
        pd.DataFrame(artists, index=range(n_artists))
    )

