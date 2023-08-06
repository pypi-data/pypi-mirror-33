from mdatapipe.plugin import PipelinePlugin


class Plugin(PipelinePlugin):

    def on_input(self, item):
        self.put(item)
