import json
import plotly
import pandas as pd
import plotly.graph_objs as go
pd.options.plotting.backend = "plotly"


def get_plays_plot(df):
    index = df.index.to_pydatetime()

    trace1 = go.Scatter(x=index, y=list(df['plays']), mode='lines+markers', name='Plays')
    trace2 = go.Scatter(x=index, y=list(df['visitors']), mode='lines+markers', name='Visitors')
    trace3 = go.Scatter(x=index, y=list(df['finishes']), mode='lines+markers', name='Finishes')
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
        margin=dict(l=30, r=0, pad=0, b=40, t=40))

    fig = dict(data=data, layout=layout)
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


def get_segments_plot(tup):
    x, y = tup
    # Data and layout settings for heatmap plot
    title = dict(text="Segmente")
    colbar = dict(title=dict(text="Abspielrate", side="top"), x=1, y=0.515, ypad=0, len=1.03)
    xaxis = dict(title=title, nticks=7, tickmode="auto", tickangle=45, ticklen=5, tickwidth=1,
                 tickcolor="#444", ticks="outside")
    yaxis = dict(showticklabels=False)
    marg = dict(l=20, r=20, pad=0, b=20, t=50)
    htemp = "<b>Zeitpunkt:</b> %{x}<br><b>Abspielrate:</b> %{z}<extra></extra>"
    # Creation of heatmap plot
    fig = go.Figure(data=go.Heatmap(z=[y], x=x, colorscale="jet", zmin=0, zmax=max(y), zsmooth="fast",
                    hovertemplate=htemp, colorbar=colbar))
    fig.update_layout(xaxis=xaxis, yaxis=yaxis, showlegend=False, autosize=True, margin=marg)
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


def get_bar_plot(tup):
    x, y = tup
    trace1 = go.Bar(x=x, y=[x[0] for x in y], name='Plays')
    trace2 = go.Bar(x=x, y=[x[1] for x in y], name='Visitors')
    trace3 = go.Bar(x=x, y=[x[2] for x in y], name='Finishes')
    data = [trace1, trace2, trace3]
    layout = dict(
        barmode='group',
        bargap=0.15,
        bargroupgap=0.1,
        plot_bgcolor='white',
        margin=dict(l=35, r=250, pad=0, b=250, t=40)
    )
    fig = dict(data=data, layout=layout)
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


def get_heatmap_plot(comb, events):
    index = comb[0].to_pydatetime()
    fig = go.Figure(go.Heatmap(x=index, y=[x[1] for x in events], z=comb[1], colorscale='portland'))
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
