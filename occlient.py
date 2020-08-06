import requests


class OcClient:

    def __init__(self, cfg):
        self.url = cfg['uri']
        self.user = cfg['user']
        self.password = cfg['password']

    def get_all_series(self):
        """
        Request and return all series in given Opencast organization.

        :return: List of seriesId and title pairs
        """
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

    def get_series_name(self, series_id):
        """
        Request series information from Opencast.

        :param series_id: Unique identifier for series
        :return: Title of the series
        """
        url = self.url + "/api/series/" + series_id
        r = requests.get(url=url, auth=(self.user, self.password))
        x = r.json()
        return x['title']

    def get_all_episodes(self, series_id):
        """
        Request all episodes within a series.

        :param series_id: Unique identifier for series
        :return: List of pair of eventIds and titles for episodes
        """
        url = self.url + "/api/events"
        params = {"filter": "is_part_of:" + series_id,
                  "sort": "start_date:ASC"}
        result = []
        r = requests.get(url=url, params=params, auth=(self.user, self.password))
        json_data = r.json()
        for elem in json_data:
            result.append([elem['identifier'], elem['title']])
        return result

    def get_episode_data(self, episode_id):
        """
        Requests episode information from Opencast.

        :param episode_id: Unique identifier for episode
        :return: Tuple of episode title, parent seriesId and parent series title
        """
        url = self.url + "/api/events/" + episode_id
        r = requests.get(url=url, auth=(self.user, self.password))
        x = r.json()
        return x['title'], x['is_part_of'], x['series']
