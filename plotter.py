import plotly.graph_objects as go
import plotly.express as px
from util import get_release_data


LAYOUT_STYLE = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font_color='#CCCCCC',
    yaxis_tickprefix='$',
    yaxis_tickformat=',.2f',
    xaxis_tickfont_color='#CCCCCC',
    yaxis_tickfont_color='#CCCCCC',
    xaxis_zeroline=False,
    yaxis_zeroline=False,
    yaxis_gridcolor='#666666',
    xaxis_gridcolor='#666666',
    clickmode='event+select',
    dragmode='select'
)


def figure_style(func):
    """
    Decorator to make plot generating functions produce consistent style
    :return: Figure, list of col names
    """
    def wrapper(*args, **kwargs):
        fig, custom_data_labels = func(*args, **kwargs)
        assert isinstance(fig, go.Figure), '@figure_style can only decorate functions that return Figures'
        fig.update_layout(**LAYOUT_STYLE)
        return fig, custom_data_labels
    return wrapper


@figure_style
def make_country_plot():
    """
    produce a plot representing each country in the data
    :return: Figure
    """
    return go.Figure(), []


@figure_style
def make_label_plot():
    """
    produce a plot representing each record label in the data
    :return:
    """
    return go.Figure(), []


@figure_style
def make_artist_plot():
    """
    produce a plot representing each artist in the data
    :return: Figure
    """
    groupings = ['artist', 'artist_id']
    df = (
        get_release_data()
        .groupby(groupings)
        .agg({
            'lowest_price': 'max',
            'num_for_sale': 'median',
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
        custom_data=groupings,
        log_x=True,
        log_y=True,
        labels={
            'num_for_sale': 'Number for Sale',
            'lowest_price': 'Lowest Price'
        }
    )
    fig.update_traces(
        hovertemplate=(
            'Artist: %{customdata[0]}<br>'
            'Median # for sale: %{x}<br>'
            'Highest Min Price: %{y:$.2f}'
        )
    )
    return fig, groupings


@figure_style
def make_album_plot():
    """
    produce a plot representing each album in the data
    :return: Figure
    """
    groupings = ['artist', 'title', 'release_id', 'artist_id', 'master_id']
    df = (
        get_release_data()
        .groupby(groupings)
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
        custom_data=groupings,
        log_x=True,
        log_y=True,
        labels={
            'num_for_sale': 'Number for Sale',
            'lowest_price': 'Lowest Price'
        }
    )
    fig.update_traces(
        hovertemplate=(
            '<b>Artist</b>: %{customdata[0]}<br>'
            '<b>Album</b>: %{customdata[1]}<br>'
            'Median # for sale: %{x}<br>'
            'Lowest Price: %{y:$.2f}'
        )
    )
    return fig, groupings


@figure_style
def make_timeseries_plot(**conditions):
    df = get_release_data(**conditions)
    df['country'].fillna('-', inplace=True)
    custom_data_labels =['artist', 'title', 'num_for_sale']
    fig = px.line(
        df,
        x='when',
        y='lowest_price',
        color='country',
        line_group='release_id',
        custom_data=custom_data_labels,
        markers=True,
        labels={
            'when': 'Date Time',
            'lowest_price': 'Lowest Price',
            'country': 'Country'
        }
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
    y_max = 1.05 * df['lowest_price'].astype(float).max()
    fig.update_yaxes(range=[0, y_max])
    return fig, custom_data_labels
