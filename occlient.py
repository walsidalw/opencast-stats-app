import requests


class OcClient:

    def __init__(self, cfg):
        self.url = cfg['uri']
        self.user = cfg['user']
        self.password = cfg['password']

    """ Requests and returns all series in organization. Returned data contains seriesId, title and creation date """
    def get_all_series(self):
        url = self.url + "/api/series"
        params = {"sort": "title:ASC", "offset": 0, "limit": 10000}
        offset = 0
        result = []
        while True:
            params["offset"] = offset
            r = requests.get(url=url, params=params, auth=(self.user, self.password))
            if not r.json():
                break
            offset += 10000
            x = r.json()
            for elem in x:
                result.append((elem['identifier'], elem['title']))
        return result

    """ Requests series data from Opencast and returns series title """
    def get_series_name(self, series_id):
        url = self.url + "/api/series/" + series_id
        r = requests.get(url=url, auth=(self.user, self.password))
        x = r.json()
        return x['title']

    """ Returns all episodes within a specified series. Stores each episode inside class. """
    def get_all_episodes(self, series_id):
        url = self.url + "/api/events"
        params = {"filter": "is_part_of:" + series_id,
                  "sort": "start_date:ASC"}
        result = []
        r = requests.get(url=url, params=params, auth=(self.user, self.password))
        json_data = r.json()
        for elem in json_data:
            result.append([elem['identifier'], elem['title']])
        return result

    """ Returns stored data for a specified episode. If no data is stored yet, requests information from Opencast"""
    def get_episode_data(self, episode_id):
        url = self.url + "/api/events/" + episode_id
        r = requests.get(url=url, auth=(self.user, self.password))
        x = r.json()
        return x['title'], x['is_part_of'], x['series']
