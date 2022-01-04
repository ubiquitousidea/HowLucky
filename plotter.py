import plotly.graph_objects as go
import plotly.express as px
from util import get_release_data
from numpy import where, array


LAYOUT_STYLE = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    clickmode='event+select'
)


RELEASE_GROUPINGS = ['artist', 'title', 'release_id', 'artist_id', 'master_id']

ARTIST_INDEX = where(array(RELEASE_GROUPINGS) == 'artist_id')[0][0]
RELEASE_INDEX = where(array(RELEASE_GROUPINGS) == 'release_id')[0][0]


def figure_style(func):
    """
    Decorator to make plot generating functions produce consistent style
    :return: Figure
    """
    def wrapper(*args, **kwargs):
        fig = func(*args, **kwargs)
        assert isinstance(fig, go.Figure), '@figure_style can only decorate functions that return Figures'
        fig.update_layout(**LAYOUT_STYLE)
        return fig
    return wrapper


@figure_style
def make_country_plot():
    """
    produce a plot representing each country in the data
    :return: Figure
    """
    return go.Figure()


@figure_style
def make_label_plot():
    """
    produce a plot representing each record label in the data
    :return:
    """
    return go.Figure()


@figure_style
def make_artist_plot():
    """
    produce a plot representing each artist in the data
    :return: Figure
    """
    return go.Figure()


@figure_style
def make_album_plot():
    """
    produce a plot representing each album in the data
    :return: Figure
    """
    df = (
        get_release_data()
        .groupby(RELEASE_GROUPINGS)
        .agg({
            'num_for_sale': 'median',
            'lowest_price': 'max',
            'title': 'count'
        })
        .rename(columns={'title': 'count'})
        .reset_index()
    )
    fig = px.scatter(
        df,
        x='num_for_sale',
        y='lowest_price',
        size='count',
        color='count',
        custom_data=RELEASE_GROUPINGS,
        log_x=True,
        log_y=True
    )
    fig.update_traces(
        hovertemplate=(
            '<b>Artist</b>: %{customdata[0]}<br>'
            '<b>Album</b>: %{customdata[1]}<br>'
            'Median # for sale: %{x}<br>'
            'Lowest Price: %{y:$.2f}'
        )
    )
    return fig


@figure_style
def make_timeseries_plot(**conditions):
    df = get_release_data(**conditions)
    df['country'].fillna('-', inplace=True)
    fig = px.line(
        df,
        x='when',
        y='lowest_price',
        color='country',
        line_group='release_id',
        custom_data=['artist', 'title', 'num_for_sale'],
        markers=True
    )
    fig.update_traces(
        hovertemplate=(
            '<b>Artist</b>: %{customdata[0]}<br>'
            '<b>Album</b>: %{customdata[1]}<br>'
            'Date: %{x}<br>'
            'Lowest Price: %{y:$.2f}<br>'
            '# for Sale: %{customdata[2]}'
        )
    )
    return fig
