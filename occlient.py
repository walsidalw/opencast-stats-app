import requests
import json
from datetime import datetime, timedelta


class OcClient:

    def __init__(self, cfg):
        self.url = cfg['uri']
        self.user = cfg['user']
        self.password = cfg['password']
        self.series = {}
        self.episodes = {}
        self.providers = {"plays": ".plays.sum.influx", "finishes": ".finishes.sum.influx",
                          "visits": ".visits.sum.influx"}

    """ Updates the list(dict) of all available series. Runs in a scheduled background task. """
    def update_all_series(self):
        url = self.url + "/api/series"
        params = {"sort": "title:ASC", "offset": 0}
        offset = 0
        while True:
            params["offset"] = offset
            r = requests.get(url=url, params=params, auth=(self.user, self.password))
            if not r.json():
                break
            offset += 100
            x = r.json()
            for elem in x:
                self.series[elem['identifier']] = {"title": elem['title'], "created": elem['created']}
        print("scheduler ran")

    """ Returns the dict of all series """
    def get_all_series(self):
        return self.series

    """ Returns stored data (creation date and title) of a specific series."""
    def get_series_data(self, series_id):
        return self.series[series_id]

    """ Returns all episodes within a specified series. Stores each episode inside class. """
    def get_all_episodes(self, series_id):
        url = self.url + "/api/events"
        params = {"filter": "is_part_of:" + series_id,
                  "sort": "start_date:ASC"}
        result = {}
        r = requests.get(url=url, params=params, auth=(self.user, self.password))
        json_data = r.json()
        for elem in json_data:
            result[elem['identifier']] = elem['title']
            self.store_episode(elem)
        return result

    """ Helper method for episode data storage. """
    def store_episode(self, epi):
        self.episodes[epi['identifier']] = {"title": epi['title'], "created": epi['created'],
                                            "is_part_of": epi['is_part_of']}

    """ Returns stored data for a specified episode. If no data is stored yet, requests information from Opencast"""
    def get_episode_data(self, episode_id):
        if episode_id in self.episodes:
            return self.episodes[episode_id]
        url = self.url + "/api/events/" + episode_id
        r = requests.get(url=url, auth=(self.user, self.password))
        self.store_episode(r.json())
        return self.episodes[episode_id]

    """ Returns statistical data. Works for each representation layer (organization, series, episode) and each 
        available statics provider (defined in self.providers). """
    def get_stats(self, level, stat, resource):
        url = self.url + "/api/statistics/data/query"
        provider = level + self.providers[stat]

        if level != "organization":
            start = (self.series[resource])['created'] if level == "series" else (self.episodes[resource])['created']
        else:
            start = (datetime.today() - timedelta(183)).replace(microsecond=0).isoformat() + "Z"
        end = (datetime.now()).replace(microsecond=0).isoformat() + "Z"

        query = {"provider": {"identifier": provider},
                 "parameters": {"resourceId": resource,
                                "from": start,
                                "to": end,
                                "dataResolution": "daily"}}
        data = "data=" + json.dumps([query])

        r = requests.post(url, data=data, auth=(self.user, self.password))
        json_data = r.json()
        return (json_data[0])['data']
