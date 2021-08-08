"""
Generate the experiment script
"""

import os
import html
import enum

import expcompiler.experiment as expobj
from expcompiler.parser import _to_str


class StepType(enum.Enum):

    def __new__(cls, *args):
        value = len(cls.__members__)+1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, js_type):
        self.js_type = js_type

    html_kb_response = 'html-keyboard-response'
    html_mouse_response = 'html-mouse-response'



class ExpGenerator(object):

    #----------------------------------------------------------------------------
    def __init__(self, logger):
        self.template = self._load_template()
        self.logger = logger
        self.errors_found = False


    #----------------------------------------------------------------------------
    def _load_template(self):
        template_filename = os.path.dirname(__file__) + os.sep + 'script_template.js'
        with open(template_filename, 'r') as fp:
            return fp.read()


    #----------------------------------------------------------------------------
    def generate(self, exp):
        """
        Generate the script.

        :type exp: expcompiler.experiment.Experiment
        """

        if exp is None:
            self.logger.error('Internal error: "exp" argument not provided', 'INTERNAL_ERROR')
            self.errors_found = True
            return None

        self.errors_found = False
        script = self.template

        script = script.replace('${title}', self.generate_title_part(exp))
        script = script.replace('${layout_css}', self.generate_layout_css(exp))
        # script = script.replace('${instructions}', self.generate_instructions(exp))
        script = script.replace('${trials}', self.generate_trials(exp))
        script = script.replace('${trial_flow}', self.generate_trial_flow(exp))

        return script


    #------------------------------------------------------------
    #  Code replacing the ${title} keyword
    #------------------------------------------------------------

    def generate_title_part(self, exp):
        return html.escape(exp.title or '')


    #------------------------------------------------------------
    #  Code replacing the ${layout} keyword
    #------------------------------------------------------------

    #----------------------------------------------------------------------------
    def generate_layout_css(self, exp):
        result = []
        for control in exp.layout.values():
            if isinstance(control, expobj.TextControl):
                result.extend(self.generate_layout_css_text(control))

        return "\n".join([(" " * 8) + r for r in result])


    #----------------------------------------------------------------------------
    def generate_layout_css_text(self, ctl):
        result = []
        result.append(".{}".format(ctl.name) + " {")
        result.append("    top: {};".format(ctl.y))
        result.append("    left: {};".format(ctl.x))
        result.append("    width: {};".format(ctl.width))
        for k, v in ctl.css.items():
            result.append("    {}: {};".format(k, v))
        result.append("}")
        return result


    #------------------------------------------------------------
    #  Code replacing the ${trials} keyword
    #------------------------------------------------------------

    #----------------------------------------------------------------------------
    def generate_trials(self, exp):
        lines = [line for trial in exp.trials for line in self.generate_trial(trial, exp)]
        return "\n".join(lines)


    #----------------------------------------------------------------------------
    def generate_trial(self, trial, exp):
        result = []

        ttype = exp.trial_types[trial.trial_type]
        line_prefix = "{ "
        for step in ttype.steps:

            step_line = '{}{}: "'.format(line_prefix, self._step_name(step, ttype))

            #-- Add one <div> for each control
            for ctl_name in sorted(step.control_names):

                #-- <div> definition
                step_line += '<div class='.format(line_prefix, ctl_name) + "'" + ctl_name + "'"

                #-- Trial-specific formatting
                if ctl_name in trial.css:
                    for css_attr, value in trial.css[ctl_name].items():
                        step_line += " {}='{}'".format(css_attr, _to_str(value))

                step_line += '>'

                #-- Value of this control.
                #todo: Probably this would be needed only for TextControl; TBD later
                if ctl_name in trial.control_values:
                    step_line += trial.control_values[ctl_name]

                step_line += '</div>'

            step_line += '",'
            result.append(step_line)

            line_prefix = "  "

        result[-1] += " }, "

        return [(" " * 8) + r for r in result]


    #------------------------------------------------------------
    #  Code replacing the ${trial_flow} keyword
    #------------------------------------------------------------

    #----------------------------------------------------------------------------
    def generate_trial_flow(self, exp):
        if len(exp.trial_types) > 1:
            self.logger.error('Error: currently, only one trial type is supported.', 'MULTIPLE_TRIAL_TYPES_TBD')
            self.errors_found = True

        ttype = exp.trial_types[list(exp.trial_types)[0]]
        step_type_def_lines = [line for step in ttype.steps for line in self.generate_trial_step_flow(step, ttype, exp)]

        trial_procedure_lines = self.trial_procedure_lines(ttype, exp)

        all_lines = [(" " * 4) + line for line in step_type_def_lines + [''] + trial_procedure_lines]
        return "\n".join(all_lines)


    #----------------------------------------------------------------------------
    def generate_trial_step_flow(self, step, ttype, exp):
        result = []

        step_name = self._step_name(step, ttype)
        step_type = self._step_type(step, ttype, exp)
        if step_type is None:
            self.errors_found = True
            return ""

        result.append('const ' + step_name + ' = {')
        result.append("    type: '{}',".format('' if step_type is None else step_type.js_type))
        result.append("    stimulus: jsPsych.timelineVariable('{}'), ".format(step_name))

        if step_type == StepType.html_kb_response:
            result.append("    choices: {},".format(self.step_response_keys(step, ttype, exp)))
        else:
            self.logger('Error in compiler - step type {} not supported'.format(step_type.name))
            self.errors_found = True
            return ""

        if step.duration is not None:
            result.append("    trial_duration: {},".format(_to_str(step.duration)))

        result.append('}')

        return result


    #----------------------------------------------------------------------------
    def _step_name(self, step, ttype):
        return '{}_step{}'.format(ttype.name, step.num)


    #----------------------------------------------------------------------------
    def _step_type(self, step, ttype, exp):
        """
        Get the type of this step according to the controls it uses

        :return: StepType
        """
        control_types = {type(exp.layout[c]) for c in step.control_names}
        if len(control_types) != 1:
            type_names = ", ".join([t.__name__ for t in control_types])
            self.logger.error('Error in trial type {}: step #{} contains layout items of several types ({}), this is invalid'
                              .format(ttype.name, step.num, type_names), 'MULTIPLE_CONTROL_TYPES_IN_ONE_STEP')
            return None

        control_type = list(control_types)[0]
        if control_type == expobj.TextControl:
            return StepType.html_kb_response
        else:
            self.logger.error('Error: unsupported layout-item type ({})'.format(control_type.__name__), 'MULTIPLE_CONTROL_TYPES_IN_ONE_STEP')
            return None


    #----------------------------------------------------------------------------
    def step_response_keys(self, step, ttype, exp):
        if step.responses is None:
            return 'jsPsych.NO_KEYS'

        invalid_resp = [r for r in step.responses if r not in exp.responses]
        if len(invalid_resp) > 0:
            self.logger.error('Error in trial type {}: step #{} contains some undefined responses ({})'
                              .format(ttype.name, step.num, ",".join(invalid_resp)),
                              'UNDEFINED_RESPONSE')
            self.errors_found = True
            return 'jsPsych.NO_KEYS'

        responses = [exp.responses[r] for r in step.responses]
        if len(responses) == 0:
            return 'jsPsych.NO_KEYS'
        else:
            return "[" + ", ".join(["'{}'".format(resp.key) for resp in responses]) + "]"


    #----------------------------------------------------------------------------
    def trial_procedure_lines(self, ttype, exp):

        step_type_names = [self._step_name(step, ttype) for step in ttype.steps]

        result = []

        result.append('const trial_procedure = {')
        result.append('  timeline: [{}],'.format(", ".join(step_type_names)))
        result.append('  timeline_variables: trial_data,')
        result.append('}')

        return result
