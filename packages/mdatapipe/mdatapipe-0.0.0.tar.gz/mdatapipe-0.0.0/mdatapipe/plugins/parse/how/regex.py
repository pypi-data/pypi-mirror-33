from mdatapipe.plugin import PipelinePlugin
import re


class Plugin(PipelinePlugin):

    def on_load(self):
        self._expr = re.compile(self.config['expr'])
        self._fields = self.config.get('fields', '').split(" ")
        self._ignore_invalid = self.config.get('ignore_invalid', False)

    def on_input(self, item):
        item_dict = {}
        result = self._expr.findall(item)
        if result is None:
            if not self._ignore_invalid:
                print(self._expr)
                raise Exception("Regex mismatch")

        expected_len = len(self._fields)
        result_len = len(result)
        if not result_len == expected_len:
            if not self._ignore_invalid:
                raise Exception("Regex mistmatch, expected %d fields, got %d !" % (expected_len, result_len))

        i = 0
        for field_name in self._fields:
            if field_name[0] != "~":
                item_dict[field_name] = result[i]
            i += 1
        self.put(item_dict)
