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

""" Initializing clients """
oc_client = occlient.OcClient(cfg['opencast'])
influx_clients = influxclient.get_clients(cfg['influxdb'])


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/org')
def org():
    plays_stats = influxclient.get_views(influx_clients['df_client'], rp, 'impressions_daily',
                                         'organizationId', orgaId, orgaId)
    graph = plots.get_plays_plot(plays_stats)
    return render_template('org.html', graph=graph)


@app.route('/series')
def series():
    series_all = oc_client.get_all_series()
    return render_template('series.html', all_series=series_all)


@app.route('/series/<series_id>')
def series_details(series_id):
    series_name = oc_client.get_series_name(series_id)
    episodes = oc_client.get_all_episodes(series_id)
    df = influxclient.get_views(influx_clients['df_client'], rp, 'impressions_daily', 'seriesId',
                                series_id, orgaId)
    totals = influxclient.get_totals(influx_clients['point_client'], rp, 'impressions_daily', series_id,
                                     orgaId, episodes)
    combined = influxclient.get_views_combined(influx_clients['df_client'], rp, 'impressions_daily', orgaId, episodes)
    graphs = plots.get_plays_plot(df), plots.get_bar_plot(totals), plots.get_heatmap_plot(combined, episodes)
    return render_template('series_details.html', series_id=series_id, series_name=series_name,
                           episodes=episodes, graphPlays=graphs[0], graphBar=graphs[1], graphHeat=graphs[2])


@app.route('/episodes/<episode_id>')
def episode_details(episode_id):
    episode_data = oc_client.get_episode_data(episode_id)
    plays_stats = influxclient.get_views(influx_clients['df_client'], rp, 'impressions_daily',
                                         'eventId', episode_id, orgaId)
    segments_stats = influxclient.get_segments(influx_clients['point_client'], rp, 'segments_daily',
                                               episode_id, orgaId)
    graphs = plots.get_plays_plot(plays_stats), plots.get_segments_plot(segments_stats)
    return render_template('episode_details.html', episode_name=episode_data[0], series_id=episode_data[1],
                           series_name=episode_data[2], graphs=graphs)


if __name__ == '__main__':
    app.run(debug=True)
