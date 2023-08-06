#!/usr/bin/python
from datetime import datetime
from mdatapipe.plugin import PipelinePlugin


class Plugin(PipelinePlugin):

    def on_input(self, value):
        output = ''
        if self.config:
            if self.config.get('add_timestamp'):
                output += str(datetime.now()) + " "

        output += str(value)
        print(output)
