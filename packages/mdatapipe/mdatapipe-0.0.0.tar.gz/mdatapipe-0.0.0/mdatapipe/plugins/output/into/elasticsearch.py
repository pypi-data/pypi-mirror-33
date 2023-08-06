#!/usr/bin/python
"""
    https://www.elastic.co/guide/en/elasticsearch/reference/6.3/docs-bulk.html


- output:
    - into:
        - elasticsearch:
            buffer_size: 1000
            index_name: myindex
            url: http://localhost:9200/

"""
import requests
from time import strftime
from json import dumps
from mdatapipe.plugin import PipelinePlugin
from datetime import datetime


class Plugin(PipelinePlugin):

    def on_load(self):
        url = self.config.get('url', 'http://localhost:9200/')
        self._url = url + "/_doc/_bulk"
        self._index_name = self.config['index_name']
        self.session = requests.Session()

    def on_input_buffer(self, buffer):
        date_stamp = strftime("%Y-%m-%d")
        for item in self.buffer:
            json_items = []
            for key, value in item.items():
                if isinstance(value, datetime):
                    value = str(value.date()) + "T" + str(value.time())
                json_items.append('"%s": %s' % (key, dumps(value)))
            json_data = '{"index": {"_index": "%s-%s", "_type": "_doc" }}\n' % (self._index_name, date_stamp)
            json_data += '{%s}\n' % ', '.join(json_items)
        response = self.session.post(
            self._url, json_data,  headers={'Content-Type': 'application/x-ndjson'}
        )
        if not response.ok:
            print(json_data)
            print(response.content)
            response.raise_for_status()
            raise Exception("Unable to insert into elasticsearch")
