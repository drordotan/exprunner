"""
The definitions of an experiment, in internal format
"""


#-----------------------------------------------------------
class Experiment(object):

    def __init__(self, get_subj_id=False, get_session_id=False, results_filename=None, background_color=None, full_screen=None,
                 title=None, instructions=()):

        self.get_subj_id = get_subj_id
        self.get_session_id = get_session_id
        self.results_filename = results_filename
        self.background_color = background_color
        self.full_screen = full_screen
        self.title = title
        self.instructions = () if instructions is None else tuple(instructions)

        self.layout = {}
        self.trial_types = {}
        self.responses = {}
        self.trials = []


#===============================================================================================
# Layout items
#===============================================================================================

#-----------------------------------------------------------
class Control(object):

    def __init__(self, name):
        self.name = name


#-----------------------------------------------------------
class TextControl(Control):

    def __init__(self, name, text="", x=0, y=0, css=None):
        super().__init__(name)
        self.text = text
        self.x = x
        self.y = y
        self.css = css


#===============================================================================================
# Responses
#===============================================================================================

#-----------------------------------------------------------
class Response(object):

    def __init__(self, resp_id, value):
        self.resp_id = resp_id
        self.value = value


#-----------------------------------------------------------
class ClickButtonResponse(Response):

    def __init__(self, resp_id, value, button_text):  # todo: x,y as generic attrs? hard coded?
        super().__init__(resp_id, value)
        self.button_text = button_text


#-----------------------------------------------------------
class KbResponse(Response):

    def __init__(self, resp_id, value, key):
        super().__init__(resp_id, value)
        self.key = key


#===============================================================================================
# Other items
#===============================================================================================

#-----------------------------------------------------------
class TrialType(object):

    default_name = "default"

    def __init__(self, name):
        self.name = name
        self.steps = []

    @property
    def fields(self):
        result = set()
        for step in self.steps:
            for fld in step.fields:
                result.add(fld)
        return result


#-----------------------------------------------------------
class TrialStep(object):

    def __init__(self, num, fields, responses, duration, delay_before, delay_after):
        self.num = num
        self.fields = fields
        self.responses = responses
        self.duration = duration
        self.delay_before = delay_before
        self.delay_after = delay_after


#-----------------------------------------------------------
class Trial(object):

    def __init__(self, trial_type):
        self.trial_type = trial_type
        self.field_values = {}
