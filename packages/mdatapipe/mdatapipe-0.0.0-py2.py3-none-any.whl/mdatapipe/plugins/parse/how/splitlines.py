#!/usr/bin/python


from mdatapipe.plugin import PipelinePlugin


class Plugin(PipelinePlugin):

    def on_input(self, value):
        for line in value.splitlines():
            self.put(line)
