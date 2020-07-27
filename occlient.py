import requests


class OcClient:

    def __init__(self, cfg):
        self.url = cfg['uri']
        self.user = cfg['user']
        self.password = cfg['password']
        self.series = {}
        self.episodes = {}

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
        json = r.json()
        for elem in json:
            result[elem['identifier']] = elem['title']
            self.episodes[elem['identifier']] = {"title": elem['title'], "created": elem['created'],
                                                 "is_part_of": elem['is_part_of']}
        return result

    def get_episode_data(self, episode_id):
        return self.episodes[episode_id]
