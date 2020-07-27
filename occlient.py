import requests


class OcClient:

    def __init__(self, cfg):
        self.url = cfg['uri']
        self.user = cfg['user']
        self.password = cfg['password']

    def get_all_series(self):
        url = self.url + "/api/series"
        params = {"sort": "title:ASC", "offset": 0}
        offset = 0
        result = {}
        while True:
            params["offset"] = offset
            r = requests.get(url=url, params=params, auth=(self.user, self.password))
            if not r.json():
                break
            result += 100
            x = r.json()
            for elem in x:
                result[elem['identifier']] = elem['title']
        return result
