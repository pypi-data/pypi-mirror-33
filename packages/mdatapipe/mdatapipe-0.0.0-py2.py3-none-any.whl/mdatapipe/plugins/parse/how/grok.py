from mdatapipe.plugin import PipelinePlugin
from pygrok import Grok


class Plugin(PipelinePlugin):

    def on_load(self):
        self._expr = self.config['expr'].strip()
        self._grok = Grok(self._expr)
        self._ignore_invalid = self.config.get('ignore_invalid', False)

    def on_input(self, item):
        result = self._grok.match(item)
        if result is not None:
            self.put(result)
        else:
            if not self._ignore_invalid:
                print(self._grok.pattern)
                raise Exception("Grok mismatch")
