import plotly.express as px
from database.database_util import get_price_data


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
    yaxis_tickformat=',.2f'
)


def aggregate_prices(groupings, x_measure, y_measure, **conditions):
    """
    Utility function to collect and aggregate the prices by the groupings specified
    :param groupings: names of the grouping columns
    :param x_measure: measure to apply on number for sale
    :param y_measure: measure to apply on lowest price
    :param conditions:
    :return: grouped data frame with price summary
    """
    return (
        get_price_data(**conditions)
        .groupby(groupings)
        .agg({
            'lowest_price': y_measure,
            'num_for_sale': x_measure,
            'title': lambda x: x.nunique()
        }).rename(columns={'title': 'count'}))


def agg_plot(groupings, title, x_measure='median', y_measure='median', loglog=True, **conditions):
    """
    group the price data and aggregate price and supply
    :param groupings: list of names of categorical columns for grouping the marketplace data
    :param title: title for the plot figure
    :param x_measure: function to aggregate num_for_sale over groups
    :param y_measure: function to aggregate lowest_price over groups
    :return: Figure
    """
    df = aggregate_prices(groupings, x_measure, y_measure, **conditions)
    fig = px.scatter(
        df.reset_index(),
        x='num_for_sale',
        y='lowest_price',
        size='count',
        color='count',
        custom_data=groupings,
        log_x=loglog,
        log_y=loglog,
        labels={
            'num_for_sale': 'Number for Sale',
            'lowest_price': 'Lowest Price',
            'count': 'Unique Titles'
        },
        title=title
    )
    return fig


def gen_xy_hover_template(x_measure, y_measure):
    """
    create hover template markdown string with xmeasure and ymeasure
    """
    return (
        f'{x_measure.title()} Number for Sale: '
        '%{x}<br>'
        f'{y_measure.title()} Lowest Price: '
        '%{y:$.2f}'
    )


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
    fig.update_layout(**LAYOUT_STYLE)
    fig.update_layout(**YAXIS_MONEY_FORMAT)
    fig.update_traces(
        hovertemplate='Country: %{customdata[0]}<br>' + gen_xy_hover_template(x_measure, y_measure)
    )
    return fig, groupings, ['country']


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
    fig.update_layout(**LAYOUT_STYLE)
    fig.update_layout(**YAXIS_MONEY_FORMAT)
    fig.update_traces(
        hovertemplate='Label %{customdata[0]}<br>' + gen_xy_hover_template(x_measure, y_measure)
    )
    return fig, groupings, ['label']


def make_artist_plot(x_measure='median', y_measure='median', loglog=True):
    """
    produce a plot representing each artist in the data
    :return: Figure
    """
    groupings = ['artist', 'artist_id']
    fig = agg_plot(
        groupings=groupings,
        title='Artists: Price vs. Supply',
        x_measure=x_measure,
        y_measure=y_measure,
        loglog=loglog
    )
    fig.update_layout(**LAYOUT_STYLE)
    fig.update_layout(**YAXIS_MONEY_FORMAT)
    fig.update_traces(
        hovertemplate='Artist: %{customdata[0]}<br>' + gen_xy_hover_template(x_measure, y_measure)
    )
    return fig, groupings, ['artist']


def make_album_plot(x_measure='median', y_measure='median', **conditions):
    """
    produce a plot representing each album in the data
    :return: Figure
    """
    groupings = ['artist', 'title', 'release_id', 'artist_id', 'master_id']
    fig = agg_plot(
        groupings=groupings,
        title='Albums: Price vs Supply',
        x_measure=x_measure,
        y_measure=y_measure,
        **conditions
    )
    fig.update_layout(**LAYOUT_STYLE)
    fig.update_layout(**YAXIS_MONEY_FORMAT)
    fig.update_traces(
        hovertemplate=(
            '<b>Artist</b>: %{customdata[0]}<br>'
            '<b>Album</b>: %{customdata[1]}<br>'
            '<extra></extra>'
        ) + gen_xy_hover_template(x_measure, y_measure)
    )
    return fig, groupings, ['release']


# -----------------------------------------------------------------------------
# - Time Series Plots ---------------------------------------------------------
# -----------------------------------------------------------------------------


def make_timeseries_plot(color_var, y_var='lowest_price', **conditions):
    """
    Generate a time series plot of record values
    :param color_var: ui uses values from ENTITY_OPTIONS: (country, label, artist, album)
    :param y_var: 'lowest_price' or 'num_for_sale'
    :param conditions:
    :return:
    """
    df = get_price_data(**conditions)
    custom_data = [
        'catno', 'title', 'artist', 'num_for_sale', 'lowest_price', 'year',
        'artist_id', 'release_id', 'label', 'label_id', 'country']
    fig = px.line(
        df,
        x='when',
        y=y_var,
        line_group='release_id',
        color=color_var,
        markers=True,
        custom_data=custom_data,
        labels={
            'when': 'Date Time',
            'lowest_price': 'Lowest Price',
            'num_for_sale': 'Number For Sale',
            'country': 'Country',
            'label': 'Record Label',
            'title': 'Album Title',
            'artist': 'Artist',
            'catno': 'Catalog Number'
        },
        title="Album Prices over Time"
    )
    fig.update_traces(
        hovertemplate=(
            '<b>Title</b>: %{customdata[1]} (%{customdata[0]})<br>'
            '<b>Artist</b>: %{customdata[2]}<br>'
            '<b>Label</b>: %{customdata[8]} (%{customdata[10]} %{customdata[5]})<br>'
            'Date: %{x}<br>'
            'Lowest Price: %{customdata[4]:$.2f}<br>'
            'Number for Sale: %{customdata[3]}'
            '<extra></extra>'
        )
    )
    y_max = 1.05 * df[y_var].astype(float).max()
    fig.update_yaxes(range=[0, y_max])
    if y_var == 'lowest_price':
        fig.update_layout(**YAXIS_MONEY_FORMAT)
    fig.update_layout(**LAYOUT_STYLE)
    return fig, custom_data
