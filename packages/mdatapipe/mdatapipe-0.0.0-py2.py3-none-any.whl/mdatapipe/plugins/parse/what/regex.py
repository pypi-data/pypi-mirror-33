from mdatapipe.plugin import PipelinePlugin
import re


class Plugin(PipelinePlugin):

    def run(self):
        match = self.config.get('match')
        not_match = self.config.get('not_match')
        self._match_re = re.compile(match) if match else None
        self._not_match_re = re.compile(not_match) if not_match else None
        self.input_loop(self.regex)

    def regex(self, item):

        # Ignore items wich match the "no_match" regex
        if self._not_match_re and self._not_match_re.match(item):
            return  # skip elements tat have a no match

        # Ignore items wich do not match the "match" regex
        if self._match_re and not self._match_re.match(item):
            return

        self.put(item)
