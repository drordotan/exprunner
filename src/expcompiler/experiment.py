"""
The definitions of an experiment, in internal format
"""


#-----------------------------------------------------------
class Experiment(object):
    """
    A whole definition of an experiment
    """

    def __init__(self, get_subj_id=False, get_session_id=False, save_results=False,
                 results_filename=None, background_color=None, full_screen=None, title=None, instructions=()):

        assert isinstance(get_subj_id, bool)
        assert isinstance(get_session_id, bool)
        assert isinstance(full_screen, bool)
        assert isinstance(save_results, bool)
        assert results_filename is None or isinstance(results_filename, str)
        assert background_color is None or isinstance(background_color, str)
        assert background_color is None or isinstance(background_color, str)
        assert title is None or isinstance(title, str)
        assert instructions is None or isinstance(instructions, (list, tuple))

        self.get_subj_id = get_subj_id              # Whether to ask for the subject ID
        self.get_session_id = get_session_id        # Whether to ask for the session ID
        self.results_filename = results_filename    # Filename for saving results (None = don't save)
        self.background_color = background_color    # Background color (using valid HTML/CSS definitions)
        self.full_screen = full_screen              # Whether app should run in full screen mode
        self.save_results = save_results            # Whether results should be saved or not
        self.title = title
        self.instructions = [] if instructions is None else list(instructions)

        self.save_steps_without_responses = False

        self.layout = {}        # Layout items (controls), key = name
        self.trial_types = {}   # key = name, value = TrialType
        self.responses = {}     # key = name, value = Response
        self.trials = []        # list of Trial objects


#===============================================================================================
# Layout items
#===============================================================================================

#-----------------------------------------------------------
class Control(object):
    """
    A control (defined as part of the layout)
    """

    def __init__(self, name):
        self.name = name        # name by which this control is referred to


#-----------------------------------------------------------
class TextControl(Control):

    def __init__(self, name, text, frame, css=None):
        assert frame is not None and isinstance(frame, Frame)

        super().__init__(name)
        self.text = text
        self.frame = frame
        self.css = css or {}    # CSS definitions

#-----------------------------------------------------------
class Frame(object):

    def __init__(self, pos_left, pos_top, width, height):
        self.left = pos_left
        self.top = pos_top
        self.width = width
        self.height = height

#===============================================================================================
# Responses
#===============================================================================================

#-----------------------------------------------------------
class Response(object):

    def __init__(self, resp_id, value):
        self.resp_id = resp_id
        self.value = value      # The value associated with this response (saved to results file)


#-----------------------------------------------------------
class ClickButtonResponse(Response):

    def __init__(self, resp_id, value, text, frame):
        assert frame is None or isinstance(frame, Frame)
        super().__init__(resp_id, value)
        self.text = text
        self.frame = frame


#-----------------------------------------------------------
class KbResponse(Response):

    def __init__(self, resp_id, value, key):
        super().__init__(resp_id, value)
        self.key = key          # Keyboard key, using JsPsych key names


#===============================================================================================
# Other items
#===============================================================================================
class Instruction(object):
    """
    Defines an instruction
    """

    def __init__(self, text, response_names):
        self.text = text
        self.response_names = response_names


#-----------------------------------------------------------
class TrialType(object):
    """
    Defines the flow of a trial
    """

    default_name = "default"

    def __init__(self, name):
        self.name = name
        self.steps = []

    @property
    def control_names(self):
        result = set()
        for step in self.steps:
            for c in step.control_names:
                result.add(c)
        return result


#-----------------------------------------------------------
class TrialStep(object):
    """
    Defines one step in a trial
    """

    def __init__(self, num, control_names, responses, duration, delay_before, delay_after):
        self.num = num
        self.control_names = control_names      # Controls presented/active in this step
        self.responses = responses              # Valid responses in this step.
        self.duration = duration                # Duration of presenting the control
        self.delay_before = delay_before        # Delay before this step (in millisec)
        self.delay_after = delay_after          # Delay after this step (in millisec)
        #todo RT limit


#-----------------------------------------------------------
class Trial(object):
    """
    One trial in the experiment.
    """

    def __init__(self, trial_type):
        self.trial_type = trial_type
        self.control_values = {}    # Values to assign to each control (e.g., the text for a TextControl). dict key = the control name
        self.save_values = {}       # Values to save to the results file (dict key = output column name)
        self.css = {}

    def add_css(self, control_name, css_attr, value):
        if control_name not in self.css:
            self.css[control_name] = {}
        self.css[control_name][css_attr] = value
