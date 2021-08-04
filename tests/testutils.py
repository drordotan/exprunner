
import pandas as pd
from expcompiler.parser import Parser

class ReaderForTests(object):

    def __init__(self, general=None, layout=None, trial_types=None, respones=None, trials=None):
        self._general = self._to_df(general, ['param', 'value'])
        self._layout = self._to_df(layout, ['field_name', 'type', 'text'])
        self._trial_types = self._to_df(trial_types, ['fields'])
        self._respones = self._to_df(respones, ['id', 'type', 'value'])
        self._trials = self._to_df(trials, [])


    def _to_df(self, data, cols):
        if data is None:
            return pd.DataFrame({c: [] for c in cols})
        elif isinstance(data, (list, tuple, dict)):
            return pd.DataFrame(data)
        else:
            return data


    def open(self):
        return True

    def general_config(self):
        return self._general

    def layout(self):
        return self._layout

    def trial_types(self):
        return self._trial_types

    def response_modes(self):
        return self._respones

    def trials(self):
        return self._trials



class ParserForTests(Parser):

    def __init__(self, reader=None):
        super().__init__(None, reader=reader)
