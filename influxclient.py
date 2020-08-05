from influxdb import DataFrameClient, InfluxDBClient
import pandas as pd
import json
import time


def get_clients(cfg):
    point_client = InfluxDBClient(cfg['host'], cfg['port'], cfg['user'], cfg['password'], cfg['database'])
    df_client = DataFrameClient(cfg['host'], cfg['port'], cfg['user'], cfg['password'], cfg['database'])
    return {'point_client': point_client,
            'df_client': df_client}


def get_views(client: DataFrameClient, rp, measurement, resource, res_id, orga_id):
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
    df = pd.DataFrame()
    z = []
    for idx, name in events:
        temp = get_views(client, rp, measurement, 'eventId', idx, orga_id)
        if not temp.empty:
            temp = temp.drop(columns=['plays', 'finishes'])
            temp = temp.rename(columns={'visitors': idx})
            df = df.join(temp, how='outer')
            df = df.fillna(0)
            z.append(list(df[idx]))
    return df.index, z


def get_totals(client: InfluxDBClient, rp, measurement, series_id, orga_id, events):
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
