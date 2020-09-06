"""
The Apereo Foundation licenses this file to you under the Educational
Community License, Version 2.0 (the "License"); you may not use this file
except in compliance with the License. You may obtain a copy of the License
at:

  http://opensource.org/licenses/ecl2.txt

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the
License for the specific language governing permissions and limitations under
the License.
"""

from flask import Flask, render_template
import occlient
import influxclient
import plots
import yaml

app = Flask(__name__)

""" Configuration file parsing """
with open("test_config.yaml", "r") as ymlfile:
    cfg = yaml.safe_load(ymlfile)

orgaId = (cfg['opencast'])['organizationId']
rp = (cfg['influxdb'])['retention-policy']


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/org')
def org():
    influx_client = influxclient.get_dataframe_client(cfg['influxdb'])
    view_stats = influxclient.get_views(influx_client, rp, 'impressions_daily',
                                        'organizationId', orgaId, orgaId)
    graph = plots.get_views_plot(view_stats)
    return render_template('org.html', graphViews=graph)


@app.route('/series')
def series():
    series_all = occlient.get_all_series(cfg['opencast'])
    return render_template('series.html', all_series=series_all)


@app.route('/series/<series_id>')
def series_details(series_id):
    data = series_details_data(series_id)
    return render_template('series_details.html', series_id=series_id, series_name=data[0],
                           episodes=data[1], graphViews=data[2], graphBar=data[3], graphHeat=data[4])


@app.route('/episodes/<episode_id>')
def episode_details(episode_id):
    data = episode_details_data(episode_id)
    return render_template('episode_details.html', episode_name=data[0], series_id=data[1],
                           series_name=data[2], graphViews=data[3], graphHeat=data[4])


def series_details_data(series_id):
    """
    Try to fetch statistics. If unsuccessful, do not invoke plotting functions and avoid exceptions.

    :param series_id: Unique identifier for series
    :return: List of all relevant data for rendering: series title, list of episodes and graphs
             for the lines, bar and heatmap plots
    """
    influx_client_df = influxclient.get_dataframe_client(cfg['influxdb'])
    influx_client_ds = influxclient.get_dataset_client(cfg['influxdb'])
    series_name = occlient.get_series_name(cfg['opencast'], series_id)
    episodes = occlient.get_all_episodes(cfg['opencast'], series_id)

    view_stats = influxclient.get_views(influx_client_df, rp, 'impressions_daily', 'seriesId',
                                        series_id, orgaId)
    if view_stats.empty:
        graph_views = ''
    else:
        graph_views = plots.get_views_plot(view_stats)

    totals = influxclient.get_totals(influx_client_ds, rp, 'impressions_daily', series_id,
                                     orgaId, episodes)
    if not totals[0]:
        graph_totals = ''
    else:
        graph_totals = plots.get_bar_plot(totals)

    combined = influxclient.get_views_combined(influx_client_df, rp, 'impressions_daily',
                                               orgaId, episodes)
    if combined[0].empty:
        graph_combined = ''
    else:
        graph_combined = plots.get_heatmap_plot(combined)

    return [series_name, episodes, graph_views, graph_totals, graph_combined]


def episode_details_data(episode_id):
    """
    Try to fetch statistics. If unsuccessful, do not invoke plotting functions and avoid exceptions.

    :param episode_id: Unique identifier for episode
    :return: List of all relevant data for rendering: episode title, seriesId and title, and graphs
             for the lines and segments heatmap plots
    """
    influx_client_df = influxclient.get_dataframe_client(cfg['influxdb'])
    influx_client_ds = influxclient.get_dataset_client(cfg['influxdb'])
    episode_data = occlient.get_episode_data(cfg['opencast'], episode_id)

    view_stats = influxclient.get_views(influx_client_df, rp, 'impressions_daily',
                                        'eventId', episode_id, orgaId)
    if view_stats.empty:
        graph_views = ""
    else:
        graph_views = plots.get_views_plot(view_stats)

    segments_stats = influxclient.get_segments(influx_client_ds, rp, 'segments_daily',
                                               episode_id, orgaId)
    if not segments_stats:
        graph_heat = ""
    else:
        graph_heat = plots.get_segments_plot(segments_stats)

    return [episode_data[0], episode_data[1], episode_data[2], graph_views, graph_heat]


if __name__ == '__main__':
    app.run(debug=True)
