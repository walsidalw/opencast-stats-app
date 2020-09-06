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

import requests


def get_all_series(cfg):
    """
    Request and return all series in given Opencast organization.

    :param cfg: Opencast configuration
    :return: List of seriesId and title pairs
    """
    url = cfg['uri'] + "/api/series"
    params = {"sort": "title:ASC", "offset": 0, "limit": 10000}
    offset = 0
    result = []
    while True:
        params["offset"] = offset
        r = requests.get(url=url, params=params, auth=(cfg['user'], cfg['password']))
        if not r.json():
            break
        offset += 10000
        x = r.json()
        for elem in x:
            result.append((elem['identifier'], elem['title']))
    return result


def get_series_name(cfg, series_id):
    """
    Request series information from Opencast.

    :param series_id: Unique identifier for series
    :param cfg: Opencast configuration
    :return: Title of the series
    """
    url = cfg['uri'] + "/api/series/" + series_id
    r = requests.get(url=url, auth=(cfg['user'], cfg['password']))
    x = r.json()
    return x['title']


def get_all_episodes(cfg, series_id):
    """
    Request all episodes within a series.

    :param series_id: Unique identifier for series
    :param cfg: Opencast configuration
    :return: List of pair of eventIds and titles for episodes
    """
    url = cfg['uri'] + "/api/events"
    params = {"filter": "is_part_of:" + series_id,
              "sort": "start_date:ASC"}
    result = []
    r = requests.get(url=url, params=params, auth=(cfg['user'], cfg['password']))
    json_data = r.json()
    for elem in json_data:
        result.append([elem['identifier'], elem['title']])
    return result


def get_episode_data(cfg, episode_id):
    """
    Requests episode information from Opencast.

    :param episode_id: Unique identifier for episode
    :param cfg: Opencast configuration
    :return: Tuple of episode title, parent seriesId and parent series title
    """
    url = cfg['uri'] + "/api/events/" + episode_id
    r = requests.get(url=url, auth=(cfg['user'], cfg['password']))
    x = r.json()
    return x['title'], x['is_part_of'], x['series']
