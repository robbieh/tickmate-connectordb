import os
import sys
import yaml
import sqlite3
import datetime
import connectordb
import requests.exceptions
from configloader import ConfigLoader

CONFFILE = os.getenv("HOME") + '/.tickmate-connectordb.yaml'
TESTCONFFILE = './test-resources/tickmate-connectordb.yaml'

MAIN_CONF = CONFFILE

config = ConfigLoader()
if os.path.isfile(CONFFILE):
    config.update_from_yaml_file(os.path.normpath(CONFFILE))
if os.path.isfile(TESTCONFFILE):
    MAIN_CONF = TESTCONFFILE
    config.update_from_yaml_file(os.path.normpath(TESTCONFFILE))
config.update_from_env_namespace(namespace='TKCDB')

def trackname_to_streamname(name):
    return name.replace("/","").replace("-","").title().replace(" ", "")

def get_cdb_device(url, name):
    try:
        if url is None:
            url = config.get('URL')
        api_key =  config.get('API_KEY')
        if api_key is None:
            import setup_device
            url, api_key = setup_device.setup_device(MAIN_CONF, config, url, name)
        device = connectordb.ConnectorDB(api_key, url=url)
        return device
    except requests.exceptions.ConnectionError as e:
        print("ConnectionError exception while connecting to %s" % url)
        print(sys.exc_info()[1])
    sys.exit(1)

def parse_args():
    DBFILE = None
    URL = None
    NAME = None
    for arg in sys.argv[1:]:
        if os.path.isfile(arg):
            DBFILE = arg
        elif arg[:4] == "http":
            URL = arg
        else:
            NAME= arg
    return (DBFILE, URL, NAME)

def main():
    dbfile, url, name=parse_args()
    device = get_cdb_device(url,name)
    tg = tickdb_generator(dbfile)
    points = {}
    for r in tg:
        stream_name = trackname_to_streamname(r["tracks_name"])
        t = datetime.datetime(r["year"], r["month"] + 1, r["day"], r["hour"], r["minute"], r["second"] ).timestamp()
        d = 1
        if stream_name in points.keys():
            points[stream_name].append({"t": t, "d": d})
        else:
            points[stream_name] = [{"t": t, "d": d}]

    for stream_name in points.keys():
        stream = device[stream_name]
        if not stream.exists():
            stream.create({"type": "number"})
        last=stream(transform="if last")
        if last is None:
            last = 0
        else:
            last = last[0]['t']
        datapoint_array = points[stream_name]
        datapoint_array = list(filter(lambda item: item['t'] > last, datapoint_array),)
        datapoint_array.sort(key=lambda item: item['t'])
        if len(datapoint_array) > 0:
            print("Inserting to %s: %s" % (stream_name, datapoint_array))
            stream.insert_array(datapoint_array, restamp=False)
        else:
            print("No updates for %s" % stream_name)


def tickdb_generator(filename):
    if filename is None:
        print("Please pass the path to your tickmate db file.")
        sys.exit(1)
    print(filename)
    dbcxn = sqlite3.connect(filename)
    c = dbcxn.cursor()
    c.row_factory = sqlite3.Row
    for row in c.execute(''' select tracks._id as tracks_id, tracks.name as tracks_name, ticks._id as ticks_id,
            ticks.year as year, ticks.month as month, ticks.day as day,
            ticks.hour as hour, ticks.minute as minute, ticks.second as second,
            ticks.has_time_info as has_time_info
            from tracks, ticks where tracks._id = ticks._track_id; '''):
        yield row

if __name__ == '__main__':
    main()

