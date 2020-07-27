from flask import Flask, render_template
from apscheduler.schedulers.background import BackgroundScheduler
import occlient
import atexit
import yaml

app = Flask(__name__)

""" Configuration file parsing """
with open("test_config2.yaml", "r") as ymlfile:
    cfg = yaml.safe_load(ymlfile)

""" Initializing clients """
oc_client = occlient.OcClient(cfg["opencast"])
oc_client.update_all_series()


""" Run an update task in the background every minute for series dict """
scheduler = BackgroundScheduler()
scheduler.add_job(func=oc_client.update_all_series, trigger="interval", minutes=1)
scheduler.start()
atexit.register(lambda: scheduler.shutdown())


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/org')
def org():
    data = oc_client.get_stats("organization", "plays", "mh_default_org")
    return render_template('org.html')


@app.route('/series')
def series():
    series_data = oc_client.get_series()
    return render_template('series.html', all_series=series_data.items())


@app.route('/series/<series_id>')
def series_details(series_id):
    series_data = oc_client.get_series()
    episodes = oc_client.get_all_episodes(series_id)
    series_name = (series_data[series_id])['title']
    return render_template('series_details.html', series_id=series_id, series_name=series_name,
                           episodes=episodes.items())


@app.route('/episodes/<episode_id>')
def episode_details(episode_id):
    series_data = oc_client.get_series()
    episode = (episode_id, oc_client.get_episode_data(episode_id))
    series_id = (episode[1])['is_part_of']
    series_name = (series_data[series_id])['title']
    return render_template('episode_details.html', series_id=series_id, series_name=series_name,
                           episode=episode)


if __name__ == '__main__':
    app.run(debug=True)
