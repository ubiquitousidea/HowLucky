from numpy import log, where, array
import plotly.graph_objects as go
import plotly.express as px
from util import get_release_data


LAYOUT_STYLE = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font_color='#CCCCCC',
    font_size=18,
    xaxis_tickfont_size=12,
    yaxis_tickfont_size=12,
    xaxis_tickfont_color='#CCCCCC',
    yaxis_tickfont_color='#CCCCCC',
    xaxis_zeroline=False,
    yaxis_zeroline=False,
    yaxis_gridcolor='#444444',
    xaxis_gridcolor='#444444',
    clickmode='event+select',
    dragmode='select'
)


YAXIS_MONEY_FORMAT = dict(
    yaxis_tickprefix='$',
    yaxis_tickformat=',.2f',

)


def figure_style(func):
    """
    Decorator to make plot generating functions produce consistent style
    :return: Figure, list of col names
    """
    def wrapper(*args, **kwargs):
        fig, custom_data_labels = func(*args, **kwargs)
        fig.update_layout(**LAYOUT_STYLE)
        return fig, custom_data_labels
    return wrapper


def aggregate_prices(groupings, x_measure, y_measure):
    return (
        get_release_data()
        .groupby(groupings)
        .agg({
            'lowest_price': y_measure,
            'num_for_sale': x_measure,
            'title': 'count'
        }).rename(columns={'title': 'count'}))


def agg_plot(groupings, title, x_measure='median', y_measure='median'):
    """
    group the price data and aggregate price and supply
    :param groupings: list of names of categorical columns for grouping the marketplace data
    :param title: title for the plot figure
    :param x_measure: function to aggregate num_for_sale over groups
    :param y_measure: function to aggregate lowest_price over groups
    :return: Figure
    """
    df = aggregate_prices(groupings, x_measure, y_measure)
    fig = px.scatter(
        df.reset_index(),
        x='num_for_sale',
        y='lowest_price',
        size='count',
        color='count',
        custom_data=groupings,
        log_x=True,
        log_y=True,
        labels={
            'num_for_sale': 'Number for Sale',
            'lowest_price': 'Lowest Price',
            'count': 'Record Count'
        },
        title=title
    )
    return fig


def xy_hovertemplate(x_measure, y_measure):
    """
    create hover template markdown string with xmeasure and ymeasure
    """
    return (
        f'{x_measure.title()} Number for Sale: '
        '%{x}<br>'
        f'{y_measure.title()} Lowest Price: '
        '%{y:$.2f}'
    )


@figure_style
def make_country_plot(x_measure='median', y_measure='median'):
    """
    produce a plot representing each country in the data
    :return: Figure
    """
    groupings = ['country']
    fig = agg_plot(
        groupings=groupings,
        title='Release Country',
        x_measure=x_measure,
        y_measure=y_measure)
    fig.update_layout(**YAXIS_MONEY_FORMAT)
    fig.update_traces(
        hovertemplate='Country: %{customdata[0]}<br>' + xy_hovertemplate(x_measure, y_measure)
    )
    return fig, groupings


@figure_style
def make_label_plot(x_measure='median', y_measure='median'):
    """
    produce a plot representing each record label in the data
    :return:
    """
    groupings = ['label', 'label_id']
    fig = agg_plot(
        groupings=groupings,
        title='Record Label',
        x_measure=x_measure,
        y_measure=y_measure
    )
    fig.update_layout(**YAXIS_MONEY_FORMAT)
    fig.update_traces(
        hovertemplate='Label %{customdata[0]}<br>' + xy_hovertemplate(x_measure, y_measure)
    )
    return fig, groupings


@figure_style
def make_artist_plot(x_measure='median', y_measure='median'):
    """
    produce a plot representing each artist in the data
    :return: Figure
    """
    groupings = ['artist', 'artist_id']
    fig = agg_plot(
        groupings=groupings,
        title='Artists: Price vs. Supply',
        x_measure=x_measure,
        y_measure=y_measure)
    fig.update_layout(**YAXIS_MONEY_FORMAT)
    fig.update_traces(
        hovertemplate='Artist: %{customdata[0]}<br>' + xy_hovertemplate(x_measure, y_measure)
    )
    return fig, groupings


@figure_style
def make_album_plot(x_measure='median', y_measure='median'):
    """
    produce a plot representing each album in the data
    :return: Figure
    """
    groupings = ['artist', 'title', 'release_id', 'artist_id', 'master_id']
    fig = agg_plot(
        groupings=groupings,
        title='Albums: Price vs Supply',
        x_measure=x_measure,
        y_measure=y_measure)
    fig.update_layout(**YAXIS_MONEY_FORMAT)
    fig.update_traces(
        hovertemplate=(
            '<b>Artist</b>: %{customdata[0]}<br>'
            '<b>Album</b>: %{customdata[1]}<br>'
        ) + xy_hovertemplate(x_measure, y_measure)
    )
    return fig, groupings


@figure_style
def make_timeseries_plot(color_var, y_var='lowest_price', **conditions):
    df = get_release_data(**conditions)
    custom_data = ['artist', 'title', 'num_for_sale', 'lowest_price', 'year']
    fig = px.line(
        df,
        x='when',
        y=y_var,
        line_group='release_id',
        color=color_var,
        custom_data=custom_data,
        labels={
            'when': 'Date Time',
            'lowest_price': 'Lowest Price',
            'num_for_sale': 'Number For Sale',
            'country': 'Country'
        },
        title="Album Prices over Time"
    )
    fig.update_traces(
        hovertemplate=(
            '<b>Artist</b>: %{customdata[0]}<br>'
            '<b>Album</b>: %{customdata[1]}<br>'
            '<b>Year</b>: %{customdata[4]}<br>'
            'Date: %{x}<br>'
            'Lowest Price: %{customdata[3]:$.2f}<br>'
            'Number for Sale: %{customdata[2]}'

        )
    )
    y_max = 1.05 * df[y_var].astype(float).max()
    fig.update_yaxes(range=[0, y_max])
    if y_var == 'lowest_price':
        fig.update_layout(**YAXIS_MONEY_FORMAT)
    return fig, custom_data
