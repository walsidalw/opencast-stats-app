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
        name='Plays')

    trace2 = go.Scatter(
        x=index,
        y=list(df['visitors']),
        mode='lines+markers',
        name='Visitors')

    trace3 = go.Scatter(
        x=index,
        y=list(df['finishes']),
        mode='lines+markers',
        name='Finishes')

    data = [trace1, trace2, trace3]

    layout = dict(
        xaxis=dict(
            showline=True,
            showticklabels=True,
            linecolor='rgb(204, 204, 204)',
            linewidth=2,
            ticks='outside',
            tickfont=dict(
                family='Arial',
                size=12,
                color='rgb(82, 82, 82)'),
            showgrid=True,
            gridcolor="#e6e6e6"),
        yaxis=dict(
            showgrid=True,
            gridcolor="#e6e6e6",
            zeroline=True,
            zerolinecolor="#e6e6e6",
            zerolinewidth=1),
        plot_bgcolor='white',
        margin=dict(
            l=30,
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
            x=1,
            y=0.515,
            ypad=0,
            len=1.03),
        hovertemplate="<b>Zeitpunkt:</b> %{x}<br>"
                      "<b>Abspielrate:</b> %{z}"
                      "<extra></extra>"))

    layout = dict(
        showlegend=False,
        autosize=True,
        xaxis=dict(
            title=dict(
                text="Segmente"),
            nticks=7,
            tickmode="auto",
            tickangle=45,
            ticklen=5,
            tickwidth=1,
            tickcolor="#444",
            ticks="outside"),
        yaxis=dict(
            showticklabels=False),
        margin=dict(
            l=20,
            r=20,
            pad=0,
            b=20,
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
        name='Plays')

    trace2 = go.Bar(
        x=x,
        y=[x[1] for x in y],
        name='Visitors')

    trace3 = go.Bar(
        x=x,
        y=[x[2] for x in y],
        name='Finishes')

    data = [trace1, trace2, trace3]

    layout = dict(
        barmode='group',
        bargap=0.12,
        bargroupgap=0.05,
        plot_bgcolor='white',
        xaxis=dict(
            nticks=len(x),
            tickmode="auto",
            tickangle=60,
            ticklen=5,
            tickwidth=1,
            tickcolor="#444",
            ticks="outside",
            automargin=True),
        margin=dict(
            l=35,
            r=0,
            pad=0,
            b=0,
            t=40))

    fig = dict(data=data, layout=layout)
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


def get_heatmap_plot(comb, events):
    """
    Build a heatmap plot for comparison of visitor amounts between episodes relative to time.

    :param comb: Contains date values for x axis and visitor values for each episode for y axis
    :param events: Episode information, in particular titles
    :return: JSON-encoded heatmap plot
    """
    index = comb[0].to_pydatetime()

    zmax = 0
    for elem in comb[1]:
        if zmax < max(elem):
            zmax = max(elem)

    data = go.Heatmap(dict(
        x=index,
        y=[x[1] for x in events],
        z=comb[1],
        zmin=0,
        zmax=math.floor(zmax * 0.75),
        colorscale='portland',
        colorbar=dict(
            title=dict(
                text="Anzahl Besucher",
                side="top"),
            x=1,
            y=0.515,
            ypad=0,
            len=1.03),
        hovertemplate="<b>Datum:</b> %{x}<br>"
                      "<b>Aufnahme:</b> %{y}<br>"
                      "<b>Anzahl:</b> %{z}"
                      "<extra></extra>"))

    layout = dict(
        autosize=False,
        height=len(events) * 20,
        width=1200,
        xaxis=dict(
            tickmode="auto",
            ticklen=5,
            tickwidth=1,
            tickcolor="#444",
            ticks="outside"),
        yaxis=dict(
            nticks=len(index),
            ticklen=5,
            tickwidth=1,
            tickcolor="#444",
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
