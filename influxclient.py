from influxdb import DataFrameClient, InfluxDBClient
import pandas as pd
import numpy as np
import json
import time


def get_dataset_client(cfg):
    return InfluxDBClient(cfg['host'], cfg['port'], cfg['user'], cfg['password'], cfg['database'])


def get_dataframe_client(cfg):
    return DataFrameClient(cfg['host'], cfg['port'], cfg['user'], cfg['password'], cfg['database'])


def get_views(client: DataFrameClient, rp, measurement, resource, res_id, orga_id):
    """
    For a given resource type and Id, request number of plays, visitors and finishes grouped
    by day.

    :param client: InfluxDB DataFrame client for the query request
    :param rp: Retention Policy
    :param measurement: Name of the measurement under which the data is stored
    :param resource: Type of resource. Can be "organizationId", "seriesId" or "eventId"
    :param res_id: Unique identifier of resource
    :param orga_id: OrganizationId of the requested resource
    :return: DataFrame containing indexes for dates and columns for plays, visitors and finishes
    """
    params = {'val1': orga_id,
              'val2': res_id}
    q = 'SELECT sum("finishes") AS "finishes", sum("plays") AS "plays", sum("visitors") AS "visitors" ' \
        'FROM "{}"."{}" WHERE "organizationId"=$val1 AND "{}"=$val2 GROUP BY time(1d) FILL(0)'\
        .format(rp, measurement, resource)
    r = client.query(q, bind_params=params)
    if r:
        return r[measurement]
    return pd.DataFrame()


def get_views_combined(client: DataFrameClient, rp, measurement, orga_id, events):
    """
    For given list of episodes, request daily number of visitors. Join the resulting DataFrames
    and fill NaNs with 0s.

    :param client: InfluxDB DataFrame client for the query request
    :param rp: Retention Policy
    :param measurement: Name of the measurement under which the data is stored
    :param orga_id: OrganizationId of the requested episodes
    :param events: List of episodes, containing episodeIds and titles
    :return: Combined DataFrame for all episodes in list, where indexes are dates and columns represent
             visitors of each episode on given date
    """
    df = pd.DataFrame()
    val = []
    col = []
    for idx, name in events:
        temp = get_views(client, rp, measurement, 'eventId', idx, orga_id)
        if not temp.empty:
            temp = temp.drop(columns=['plays', 'finishes'])
            temp = temp.rename(columns={'visitors': idx})
            df = df.join(temp, how='outer')
            col.append(name)

    df = df.fillna(0)
    for column in df.columns:
        val.append(list(df[column]))
    return df.index, col, val


def get_totals(client: InfluxDBClient, rp, measurement, series_id, orga_id, events):
    """
    For given seriesId, request all points from InfluxDB summed up and grouped by eventId.
    Filter the result set by eventIds and build indexes and data tuples for each episode in given list.

    :param client: Simple InfluxDB client for the query request
    :param rp: Retention Policy
    :param measurement: Name of the measurement under which the data is stored
    :param series_id: Unique identifier for series
    :param orga_id: OrganizationId of the requested series
    :param events: List of episodes, containing episodeIds and titles
    :return: Tuple of episode titles as indexes and data list containing aggregated numbers of plays, visitors
             and finishes of corresponding episode
    """
    params = {'val1': orga_id,
              'val2': series_id}
    q = 'SELECT sum("finishes") AS "finishes", sum("plays") AS "plays", sum("visitors") AS "visitors" ' \
        'FROM "{}"."{}" WHERE "organizationId"=$val1 AND "seriesId"=$val2 GROUP BY "eventId"'\
        .format(rp, measurement)
    r = client.query(q, bind_params=params)
    index = []
    data = []
    for idx, name in events:
        points = list(r.get_points(measurement=measurement, tags={"eventId": idx}))
        if points:
            for point in points:
                index.append(name)
                data.append((point['plays'], point['visitors'], point['finishes']))
    return index, data


def get_segments(client: InfluxDBClient, rp, measurement, event_id, orga_id):
    """
    For given episode, request segment data from InfluxDB. Parse the returned JSON into human
    readable form and build lists of indexes (time strings) and play rates for each segment.
    
    :param client: Simple InfluxDB client for the query request
    :param rp: Retention Policy
    :param measurement: Name of the measurement under which the data is stored
    :param event_id: Unique identifier for episode
    :param orga_id: OrganizationId of the requested episode
    :return: Pair of indexes (time segments) and play rates
    """""
    params = {'val1': orga_id,
              'val2': event_id}
    q = 'SELECT "segments" FROM "{}"."{}" WHERE "organizationId"=$val1 AND "eventId"=$val2'.format(rp, measurement)
    r = client.query(q, bind_params=params)
    points = list(r.get_points())
    if points:
        index = []
        data = []
        r_json = json.loads((points[0])['segments'])
        if "15" in (r_json[0])['label']:
            seconds = 15
        else:
            seconds = 30
        for i, elem in enumerate(r_json):
            sec = (i + 1) * seconds
            index.append((time.strftime("%H:%M:%S", time.gmtime(sec))))
            data.append(elem['play_rate'])
        return index, data
    return []
