import json
import plotly
import pandas as pd
import plotly.graph_objs as go
pd.options.plotting.backend = "plotly"


def get_plays_plot(df):
    plot = df.plot()
    return json.dumps(plot, cls=plotly.utils.PlotlyJSONEncoder)


def get_segments_plot(tup):
    x, y = tup
    htemp = "<b>Zeitpunkt:</b> %{x}<br><b>Abspielrate:</b> %{z}<extra></extra>"
    xaxis = {'nticks': 7, 'tickmode': 'auto', 'tickangle': 45, 'ticklen': 5, 'tickwidth': 1, 'tickcolor': '#444',
             'ticks': 'outside'}
    yaxis = {'showticklabels': False}
    marg = dict(l=20, r=20, pad=0, b=20, t=50)
    fig = go.Figure(data=go.Heatmap(z=[y], x=x, colorscale='jet', zmin=0, zmax=max(y), zsmooth='fast',
                    hovertemplate=htemp))
    fig.update_layout(xaxis=xaxis, yaxis=yaxis, showlegend=False, autosize=True, margin=marg)
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
