#!/usr/bin/python
"""
    https://docs.influxdata.com/influxdb/v1.5/guides/writing_data/

    curl -i -XPOST 'http://localhost:8086/write?db=mydb' \
    --data-binary 'cpu_load_short,host=server01,region=us-west value=0.64 1434055562000000000'

- output:
    - into:
        - influxdb:
            buffer_size: 1000
            dbname: mydb
            measurement: log_info
            tag_set: [ computername ]
            field_set: [ field1 ]
            url: http://localhost:8086/
"""
import requests
from calendar import timegm
from datetime import datetime
from dateutil.parser import parse
from mdatapipe.plugin import PipelinePlugin


class Plugin(PipelinePlugin):

    def on_load(self):
        self.url = self.config.get('url', 'http://localhost:8086/')
        self._timestamp = self.config.get('timestamp', 'timestamp')
        self._date_and_time = self.config.get('date_and_time', False)
        self.db_name = self.config['dbname']
        self.session = requests.Session()

    def on_input_buffer(self, buffer):  # NOQA
        # https://docs.influxdata.com/influxdb/v1.5/write_protocols/line_protocol_tutorial/
        # weather,location=us-midwest temperature=82 1465839830100400200
        data_lines = []
        for item in self.buffer:
            tag_set_list = []
            for tag_name in self.config.get('tag_set', ''):
                tag_set_list.append("%s=%s" % (tag_name, item[tag_name]))
            tag_set = ','.join(tag_set_list)
            field_set_list = []
            skip_line = False
            for field_name in self.config['field_set']:
                field_value = item.get(field_name, None)
                # Skip lines with values set to None
                if field_value is None:
                    skip_line = True
                    break
                field_set_list.append("%s=%s" % (field_name, field_value))
            if skip_line:
                continue
            field_set = ','.join(field_set_list)
            timestamp = item.get(self._timestamp, None)
            if timestamp is None and self._date_and_time:
                timestamp = "%s %s" % (item['date'], item['time'])
                timestamp = parse(timestamp)
                timestamp = datetime.strftime(timestamp, "%s")
            elif isinstance(timestamp, datetime):
                timestamp = timegm(timestamp.utctimetuple())
                # Attemtp to identify and fix Apache date format [https://httpd.apache.org/docs/1.3/logs.html]
            else:
                if len(timestamp) > 11 and timestamp[11] == ':':
                    timestamp = timestamp.replace(':', ' ', 1)
                try:
                    timestamp = parse(timestamp)
                except ValueError:
                    print(timestamp)
                    raise
                timestamp = timegm(timestamp.utctimetuple())
            if tag_set:
                tag_set = ',' + tag_set
            data = "%s%s %s %s" % (self.config['measurement'], tag_set, field_set, timestamp)
            data_lines.append(data)
        url = "%swrite?db=%s&precision=s" % (self.url, self.db_name)
        data = '\n'.join(data_lines)
        response = self.session.post(
            url, data,  headers={'Content-Type': 'application/octet-stream'}
        )
        if not response.ok:
            print(response.content)
            response.raise_for_status()
            raise Exception("Unable to insert into influxdb")
