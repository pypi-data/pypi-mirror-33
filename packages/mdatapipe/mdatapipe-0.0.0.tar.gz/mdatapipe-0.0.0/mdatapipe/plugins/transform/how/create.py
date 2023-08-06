from mdatapipe.plugin import PipelinePlugin


class Plugin(PipelinePlugin):

    def on_input(self, item):
        new_item = {}
        for key, value in self.config.items():
            new_item[key] = value
        self.put(new_item)
