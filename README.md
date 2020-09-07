# opencast-stats-app #

Flask Web-App presenting episode statistics for episodes in [Opencast](https://opencast.org) with raw data stored in [InfluxDB](https://www.influxdata.com). It is intended for use in conjunction with the [opencast-matomo-adapter](https://github.com/walsidalw/opencast-matomo-adapter), which collects and aggregates statistics from [Matomo](https://matomo.org/). Not safe for production yet!

## How it works ##

This application contains multiple views for data representation. For each view, HTTP requests are used to fetch meta data for the current resource(s). Then the statistics are queries from a specified InfluxDB database and in a third step those statistics are fed into Plot.ly plots.

## Configuration file ##

Before start, the configuration file located in `config-yaml` needs to be set up. All properties are mandatory.

### InfluxDB configuration ###

    host: http://localhost
    
URI of the InfluxDB database
    
    port: 8086
    
Port of the InfluxDB database
    
    user: root
    
User name for logging into the InfluxDB database
    
    password: root
    
Password for the InfluxDB database
    
    database: opencast
    
Name of the InfluxDB database
    
    retention-policy: autogen
    
The retention policy to use
    
### Opencast configuration ###

    uri: https://organization.api.opencast.com
    
The (External API) URI the Web-App connects to to find out an resource’s metadata
    
    user: admin
    
Opencast External API login credentials, user name

    password: password
    
Opencast External API login credentials, password

    organizationId: mh_default_org
    
Opencast organizationId, for which statistics shall be retrieved

## Opencast ##

The adapter will try to retrieve metadata for every viewed resource using the Opencast External API. Specifically, it will use the =/api/events/{episodeId}= endpoint, passing the episode ID, the =/api/events= endpoint, for a list of all episodes within a series, and the =/api/series= endpoint for a list of all series within an organisation.

## InfluxDB ##

Raw data for statistics is retrieved from InfluxDB. The Web-App will query InfluxDB via HTTP requests and always specify at least one resource (organizatioId, seriesId, eventId). It expects the general episode metrics (visitors, plays, views) within a `impressions_daily` measurement and data for video segments within the `segments_daily` measurement.

## Installation ##

### Setup ###

First, create a virtual environment for the application and activate it from the project root:

```shell
$ pip install virtualenv
$ virtualenv venv
$ source venv/bin/activate
```

Then you can install the system requirements in the isolated environment:

```shell
$ pip install -t lib -r requirements.txt
```

### Run ###

Within the virtual environment simply run from the project root:

```shell
$ python app.py
```

Note that under this setup the application runs in development mode. If you want to deploy the Web-App in production, some changes have to be made. See [here](https://flask.palletsprojects.com/en/1.1.x/tutorial/deploy/) for some guidelines.
