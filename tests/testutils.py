
import pandas as pd
from expgen.parser import Parser


#----------------------------------------------------------------------------------------------
class ReaderForTests(object):

    def __init__(self, general=None, layout=None, trial_types=None, respones=None, trials=None, instructions=None):
        self._general = _to_df(general, ['param', 'value'])
        self._instructions_config = _to_df(instructions, ['instructions', 'text', 'responses'])
        self._layout = _to_df(layout, ['layout_name', 'type', 'text'])
        self._trial_types = _to_df(trial_types, ['layout items'])
        self._respones = _to_df(respones, ['response_name', 'type', 'value'])
        self._trials = _to_df(trials, [])


    # noinspection PyMethodMayBeStatic
    def open(self):
        return True

    def general_config(self):
        return self._general

    def instructions_config(self):
        return self._instructions_config

    def layout(self):
        return self._layout

    def trial_types(self):
        return self._trial_types

    def response_modes(self):
        return self._respones

    def trials(self):
        return self._trials


def _to_df(data, cols):
    if data is None:
        return pd.DataFrame({c: [] for c in cols})
    elif isinstance(data, (list, tuple, dict)):
        return pd.DataFrame(data)
    else:
        return data


#----------------------------------------------------------------------------------------------
class ParserForTests(Parser):

    def __init__(self, reader=None, parse_trial_types=False, parse_layout=False, parse_trials=False):
        super().__init__(None, reader=reader)
        self.do_parse_ttype = parse_trial_types
        self.do_parse_layout = parse_layout
        self.do_parse_trials = parse_trials

    def parse_layout(self, exp):
        if self.do_parse_layout:
            super().parse_layout(exp)

    def parse_trial_types(self, exp):
        if self.do_parse_ttype:
            super().parse_trial_types(exp)

    def parse_trials(self, exp):
        if self.do_parse_trials:
            super().parse_trials(exp)
