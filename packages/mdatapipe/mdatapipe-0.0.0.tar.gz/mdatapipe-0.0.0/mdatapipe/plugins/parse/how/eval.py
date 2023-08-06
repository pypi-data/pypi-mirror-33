#!/usr/bin/python


from mdatapipe.plugin import PipelinePlugin


class Plugin(PipelinePlugin):

    def on_input(self, item):
        new_item = eval("item." + self.config)
        self.put(new_item)
