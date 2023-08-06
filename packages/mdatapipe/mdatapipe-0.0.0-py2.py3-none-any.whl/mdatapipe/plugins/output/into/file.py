#!/usr/bin/python
from mdatapipe.plugin import PipelinePlugin


class Plugin(PipelinePlugin):

    def on_load(self):
        path = self.config['path']
        self.file = open(path, 'w')

    def on_input(self, item):
        self.file.write(str(item) + "\n")

    def on_terminate(self):
        self.file.close()
