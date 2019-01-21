import os
import sys
import yaml
import getpass
import connectordb
import requests.exceptions
from configloader import ConfigLoader

def setup_device(conf_file,config,url,name):
    print("No configuration file found, so attempting to log in to generate an API key.")
    if url is None or name is None:
        print("\nPlease specify a URL and username for your ConnectorDB instance.")
        sys.exit(1)
    try:
        print("Logging in to %s@%s\n" % ( name, url ))
        passwd=getpass.getpass()
        cdb = connectordb.ConnectorDB(name,passwd,url)
        print("Succesfully logged in")
        newdevice = cdb.user["Tickmate"]
        if not newdevice.exists():
            newdevice.create()
        key = newdevice.apikey

        config["API_KEY"] = key
        config["URL"] = url
        print("Creating configuration file %s" % conf_file)
        with open(conf_file, 'w') as output:
            yaml.dump(config.copy(), output, default_flow_style=False)
        return (url,key)
    except requests.exceptions.ConnectionError as e:
        print("ConnectionError exception while connecting to %s" % url)
        print(sys.exc_info()[1])
    sys.exit(1)
