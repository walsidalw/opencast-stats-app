from flask import Flask, render_template
from apscheduler.schedulers.background import BackgroundScheduler
import occlient
import atexit
import yaml

app = Flask(__name__)

""" Configuration file parsing """
with open("test_config.yaml", "r") as ymlfile:
    cfg = yaml.safe_load(ymlfile)

""" Initializing clients """
oc_client = occlient.OcClient(cfg["opencast"])

""" Global dict for all series in opencast instance """
SERIES = oc_client.get_all_series()


def series_update():
    global SERIES
    SERIES = oc_client.get_all_series()
    print("Scheduler ran")


""" Run an update task in the background every minute for series dict """
scheduler = BackgroundScheduler()
scheduler.add_job(func=series_update, trigger="interval", minutes=1)
scheduler.start()
atexit.register(lambda: scheduler.shutdown())


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/org')
def org():
    return render_template('org.html')


@app.route('/series')
def series():
    return render_template('series.html', data=SERIES.items())


@app.route('/series/<series_id>')
def series_datails(series_id):
    episodes = oc_client.get_all_episodes(series_id)
    return render_template('series_details.html', series_id=series_id, series_name=SERIES[series_id],
                           episodes=episodes.items())


@app.route('/episode/<series_id>/<episode_id>')
def episode_datails(series_id, episode_id):
    episode = (episode_id, oc_client.get_episode(episode_id))
    return render_template('episode_details.html', series_id=series_id, series_name=SERIES[series_id],
                           episode=episode)


if __name__ == '__main__':
    app.run(debug=True)
