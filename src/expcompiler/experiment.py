"""
The definitions of an experiment, in internal format
"""

#-----------------------------------------------------------
class Experiment(object):

    def __init__(self, get_subj_id=False, get_session_id=False, results_filename=None, background_color=None, full_screen=None,
                 instructions=()):

        self.get_subj_id = get_subj_id
        self.get_session_id = get_session_id
        self.results_filename = results_filename
        self.background_color = background_color
        self.full_screen = full_screen
        self.instructions = instructions

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

    def __init__(self, id, value):
        self.id = id
        self.value = value


#-----------------------------------------------------------
class ClickButtonResponse(Response):

    def __init__(self, id, value, button_text):  # todo: x,y as generic attrs? hard coded?
        super().__init__(id, value)
        self.button_text = button_text


#-----------------------------------------------------------
class KbResponse(Response):

    def __init__(self, id, value, key):
        super().__init__(id, value)
        self.key = key


#===============================================================================================
# Other items
#===============================================================================================

#-----------------------------------------------------------
class TrialType(object):

    def __init__(self, name):
        self.name = name
        self.steps = []


#-----------------------------------------------------------
class TrialStep(object):

    def __init__(self, num, fields, responses):
        self.num = num
        self.fields = fields
        self.responses = responses
        #todo delays