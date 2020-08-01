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
    df = influxclient.get_views(influx_clients['df_client'], rp, 'impressions_daily', 'organizationId', orgaId, orgaId)
    graph = plots.get_plays_plot(df)
    return render_template('org.html', tables=[df.to_html(classes='data')], titles=df.columns.values, graphJSON=graph)


@app.route('/series')
def series():
    series_all = oc_client.get_all_series()
    return render_template('series.html', all_series=series_all)


@app.route('/series/<series_id>')
def series_details(series_id):
    series_name = oc_client.get_series_name(series_id)
    episodes = oc_client.get_all_episodes(series_id)
    df = influxclient.get_views(influx_clients['df_client'], rp, 'impressions_daily', 'seriesId', series_id, orgaId)
    graph = plots.get_plays_plot(df)
    return render_template('series_details.html', series_id=series_id, series_name=series_name,
                           episodes=episodes, tables=[df.to_html(classes='data')], titles=df.columns.values,
                           graphJSON=graph)


@app.route('/episodes/<episode_id>')
def episode_details(episode_id):
    episode_data = oc_client.get_episode_data(episode_id)
    df = influxclient.get_views(influx_clients['df_client'], rp, 'impressions_daily', 'eventId', episode_id, orgaId)
    seg = influxclient.get_segments(influx_clients['point_client'], rp, 'segments_daily', episode_id, orgaId)
    graphs = plots.get_plays_plot(df), plots.get_plays_plot(seg)
    return render_template('episode_details.html', episode_name=episode_data[0], series_id=episode_data[1],
                           series_name=episode_data[2], tables=[df.to_html(classes='data')], titles=df.columns.values,
                           seg=[seg.to_html(classes='data')], times=seg.columns.values, graphJSON=graphs)


if __name__ == '__main__':
    app.run(debug=True)
