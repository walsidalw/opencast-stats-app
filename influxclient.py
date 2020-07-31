from influxdb import DataFrameClient, InfluxDBClient
import json


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
    return r[measurement]


def get_segments(client: InfluxDBClient, rp, measurement, event_id, orga_id):
    params = {'val1': orga_id,
              'val2': event_id}
    q = 'SELECT "segments" FROM "{}"."{}" WHERE "organizationId"=$val1 AND "eventId"=$val2'.format(rp, measurement)
    r = client.query(q, bind_params=params)
    point = list(r.get_points())[0]
    j = json.loads(point['segments'])
    result = []
    for i in j:
        result.append((i['nb_plays'], i['play_rate']))
    return result


c = DataFrameClient(database='opencast1')
resul = get_views(c, 'autogen', 'impressions_daily', 'eventId', 'c667ea18-3239-479b-a940-3300607503eb', 'mh_default_org')
print('Check data frame')
print(resul)
f = InfluxDBClient(database='opencast1')
df = get_segments(f, 'autogen', 'segments_daily', 'c667ea18-3239-479b-a940-3300607503eb', 'mh_default_org')
print("JSON")
print(df)

