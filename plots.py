import json
import plotly
import pandas as pd
import numpy as np
pd.options.plotting.backend = "plotly"


def get_plays_plot(df):
    plot = df.plot()
    return json.dumps(plot, cls=plotly.utils.PlotlyJSONEncoder)
