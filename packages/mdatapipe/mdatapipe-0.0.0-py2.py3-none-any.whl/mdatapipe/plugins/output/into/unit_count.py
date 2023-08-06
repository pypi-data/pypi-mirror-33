#!/usr/bin/python
"""
This plugin counts and prints the number of records that have been received
"""
from mdatapipe.plugin import PipelinePlugin


class Plugin(PipelinePlugin):

    def run(self):
        self.item_count = 0
        self.unit_size = self.config.get("unit_size", 1)
        self.input_loop(self.unit_count)

    def unit_count(self, record):
        self.item_count += 1
        if self.item_count % self.unit_size == 0:
            print(self.item_count)
        self.put(record)
