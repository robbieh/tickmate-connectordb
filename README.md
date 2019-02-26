# tickmate-connectordb
Upload your Tickmate data to ConnectorDB

[Tickmate](https://github.com/lordi/tickmate) is an Android app described as a "one-bit journal".

[ConnectorDB](http://connectordb.io/) is a Quantified Self / IoT server for storing and analyzing event-type data.

This is just a little Python script that takes a Tickmate database backup file and pushes the data into ConnectorDB.

I've been using NextCloud to automatically upload the Tickmate db files, and this now allows me to push those into ConnectorDB automatically.

## Usage

	tkcdb \[connectordb url] \[tickmake db file] \[login name]

Parameter order does not matter. It will prompt for login on first run, and then after that rely on the ConnectorDB API key. On subsequent runs only thefilename is required.

This will create a 'Tickmate' device in ConnectorDB and upload all of the data in the backup file. It will also look at the last entry for each stream and only include ticks that are newer.

Due to the nature of ConnectorDB, retroactively created ticks are a problem. If you need to start over, just delete the device in ConnectorDB and start over.
