import json
import plotly
import math
import pandas as pd
import plotly.graph_objs as go
pd.options.plotting.backend = "plotly"


def get_views_plot(df):
    """
    Build a plot for plays, visitors and finishes.

    :param df: DataFrame, where the indexes dates and which contains columns for visitors, plays and finishes
    :return: JSON-encoded lines plot
    """
    index = df.index.to_pydatetime()

    trace1 = go.Scatter(
        x=index,
        y=list(df['plays']),
        mode='lines+markers',
        name='Wiedergegeben')

    trace2 = go.Scatter(
        x=index,
        y=list(df['visitors']),
        mode='lines+markers',
        name='Besucher')

    trace3 = go.Scatter(
        x=index,
        y=list(df['finishes']),
        mode='lines+markers',
        name='Beendet')

    data = [trace1, trace2, trace3]

    layout = dict(
        xaxis=dict(
            ticks='outside'),
        yaxis=dict(
            rangemode='nonnegative',
            automargin=True),
        margin=dict(
            l=0,
            r=0,
            pad=0,
            b=40,
            t=40))

    fig = dict(data=data, layout=layout)
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


def get_segments_plot(tup):
    """
    Build a heatmap plot for video segments.

    :param tup: Tuple of x for time values on the x axis and y for play rates corresponding to segments
    :return: JSON-encoded heatmap plot
    """
    x, y = tup

    data = go.Heatmap(dict(
        z=[y],
        x=x,
        colorscale="jet",
        zmin=0,
        zmax=max(y),
        zsmooth="fast",
        colorbar=dict(
            title=dict(
                text="Abspielrate",
                side="top"),
            tickformat=".0%",
            x=1,
            y=0.515,
            ypad=0,
            len=1.03),
        hovertemplate="<b>Zeitpunkt:</b> %{x}<br>"
                      "<b>Abspielrate:</b> %{z:,.0%}"
                      "<extra></extra>"))

    layout = dict(
        showlegend=False,
        autosize=True,
        xaxis=dict(
            title=dict(
                text='Segmente'),
            nticks=7,
            tickangle=45,
            ticks='outside',
            automargin=True),
        yaxis=dict(
            showticklabels=False,
            tickformat=',.0%'),
        margin=dict(
            l=0,
            r=0,
            pad=0,
            b=0,
            t=50))

    fig = go.Figure(dict(data=data, layout=layout))
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


def get_bar_plot(tup):
    """
    Build a bar plot containing combined data of all episodes within a series.

    :param tup: Tuple of values for x and y axis
    :return: JSON-encoded bar plot
    """
    x, y = tup

    trace1 = go.Bar(
        x=x,
        y=[x[0] for x in y],
        name='Wiedergegeben')

    trace2 = go.Bar(
        x=x,
        y=[x[1] for x in y],
        name='Besucher')

    trace3 = go.Bar(
        x=x,
        y=[x[2] for x in y],
        name='Beendet')

    data = [trace1, trace2, trace3]

    layout = dict(
        barmode='group',
        bargap=0.08,
        bargroupgap=0.05,
        xaxis=dict(
            nticks=len(x),
            tickangle=60,
            ticks="outside",
            automargin=True),
        yaxis=dict(
            automargin=True),
        margin=dict(
            l=0,
            r=0,
            pad=0,
            b=0,
            t=40))

    fig = dict(data=data, layout=layout)
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


def get_heatmap_plot(comb):
    """
    Build a heatmap plot for comparison of visitor amounts between episodes relative to time.

    :param comb: Contains date values for x axis and visitor values for each episode for y axis
    :param events: Episode information, in particular titles
    :return: JSON-encoded heatmap plot
    """
    index = comb[0].to_pydatetime()

    zmax = 0
    for elem in comb[2]:
        if zmax < max(elem):
            zmax = max(elem)

    data = go.Heatmap(dict(
        x=index,
        y=comb[1],
        z=comb[2],
        zmin=0,
        zmax=math.floor(zmax * 0.75),
        colorscale='portland',
        colorbar=dict(
            title=dict(
                text="Anzahl Besucher",
                side="top"),
            x=1,
            y=0.512,
            ypad=0,
            len=1),
        hovertemplate="<b>Datum:</b> %{x}<br>"
                      "<b>Aufnahme:</b> %{y}<br>"
                      "<b>Anzahl:</b> %{z}"
                      "<extra></extra>"))

    layout = dict(
        autosize=False,
        height=len(comb[1]) * 27,
        width=1200,
        xaxis=dict(
            ticks="outside"),
        yaxis=dict(
            nticks=len(comb[1]),
            ticks="outside",
            automargin=True),
        margin=dict(
            l=0,
            r=0,
            pad=0,
            b=0,
            t=50))

    fig = go.Figure(dict(data=data, layout=layout))
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
