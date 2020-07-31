from flask import Flask, render_template
from apscheduler.schedulers.background import BackgroundScheduler
import occlient
import atexit
import yaml

app = Flask(__name__)

""" Configuration file parsing """
with open("test_config.yaml", "r") as ymlfile:
    cfg = yaml.safe_load(ymlfile)

orgaId = (cfg["opencast"])["organizationId"]

""" Initializing clients """
oc_client = occlient.OcClient(cfg["opencast"])


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/org')
def org():
    return render_template('org.html')


@app.route('/series')
def series():
    series_all = oc_client.get_all_series()
    return render_template('series.html', all_series=series_all)


@app.route('/series/<series_id>')
def series_details(series_id):
    series_name = oc_client.get_series_name(series_id)
    episodes = oc_client.get_all_episodes(series_id)
    return render_template('series_details.html', series_id=series_id, series_name=series_name,
                           episodes=episodes)


@app.route('/episodes/<episode_id>')
def episode_details(episode_id):
    episode_data = oc_client.get_episode_data(episode_id)
    return render_template('episode_details.html', episode_name=episode_data[0], series_id=episode_data[1],
                           series_name=episode_data[2])


if __name__ == '__main__':
    app.run(debug=True)
