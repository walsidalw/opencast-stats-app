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
        self.providers ={"plays": ".plays.sum.influx", "finishes": ".finishes.sum.influx",
                         "visits": ".visits.sum.influx"}

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

    def get_series(self):
        return self.series

    def get_all_episodes(self, series_id):
        url = self.url + "/api/events"
        params = {"filter": "is_part_of:" + series_id,
                  "sort": "start_date:ASC"}
        result = {}
        r = requests.get(url=url, params=params, auth=(self.user, self.password))
        json_data = r.json()
        for elem in json_data:
            result[elem['identifier']] = elem['title']
            self.episodes[elem['identifier']] = {"title": elem['title'], "created": elem['created'],
                                                 "is_part_of": elem['is_part_of']}
        return result

    def get_episode_data(self, episode_id):
        return self.episodes[episode_id]

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
        json_q = json.dumps([query])
        data = "data=" + json_q
        r = requests.post(url, data=data, auth=(self.user, self.password))
        json_data = r.json()
        print(json_data)
        return (json_data[0])['data']

