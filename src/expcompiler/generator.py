"""
Generate the experiment script
"""

import os
import html
import enum

import expcompiler
import expcompiler.experiment as expobj
from expcompiler.parser import _to_str


class StepType(enum.Enum):

    def __new__(cls, *args):
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, js_type):
        self.js_type = js_type

    html_kb_response = 'html-keyboard-response'
    html_mouse_response = 'html-mouse-response'


class ExpGenerator(object):

    # ----------------------------------------------------------------------------
    def __init__(self, logger):
        self.template = self._load_template()
        self.logger = logger
        self.errors_found = False

    # ----------------------------------------------------------------------------
    def _load_template(self):
        template_filename = os.path.dirname(__file__) + os.sep + 'script_template.js'
        with open(template_filename, 'r') as fp:
            return fp.read()

    # ----------------------------------------------------------------------------
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
        script = script.replace('${instructions}', self.generate_instructions(exp))
        script = script.replace('${trials}', self.generate_experiments(exp))
        script = script.replace('${trial_flow}', self.generate_trials_flow(exp))

        return script

    # ------------------------------------------------------------
    #  Code replacing the ${title} keyword
    # ------------------------------------------------------------

    def generate_title_part(self, exp):
        return html.escape(exp.title or '')

    # ------------------------------------------------------------
    #  Code replacing the ${layout} keyword
    # ------------------------------------------------------------

    # ----------------------------------------------------------------------------
    def generate_layout_css(self, exp):
        result = []
        for control in exp.layout.values():
            if isinstance(control, expobj.TextControl):
                result.extend(self.generate_layout_css_text(control))

        return "\n".join([(" " * 8) + r for r in result])

    # ----------------------------------------------------------------------------
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

    # ------------------------------------------------------------
    #  Code replacing the ${instructions} keyword
    # ------------------------------------------------------------
    # ------------------------------------------------------------
    # TODO: finish func generate_instructions
    def generate_instructions(self, exp):
        lst = []
        for pos, instruction in enumerate(exp.instructions):
            lst.append(self.generate_instruction(instruction, pos, exp))

        return "\n".join(lst)

    # ----------------------------------------------------------------------------
    def generate_instruction(self, instruction, pos, exp):

        text = instruction.text
        response_names = instruction.response_names

        result = self.generate_instruction_type(pos, text, exp)
        result += self.generate_instruction_flow(exp, pos, response_names)
        return result

    # ----------------------------------------------------------------------------
    def generate_instruction_type(self, pos, text, exp):
        result = "const instruction{}_data = [\n".format(pos)
        result += "        { "
        result += "exp: \"<div>{}</div>\"".format(text)
        result += " }\n]\n"
        return result

    # ----------------------------------------------------------------------------
    def generate_instruction_flow(self, exp, pos, response_names):
        step_num = 'instruction{}_step = '.format(pos)
        type_name = 'instruction{} = '.format(pos)
        result = []
        result.append('\nconst instruction{}_step = '.format(pos))
        result.append('{')
        result.append("    type: 'html-keyboard-response',")
        result.append("    stimulus: jsPsych.timelineVariable('instruction{}_step'), ".format(pos))
        result.append("    choices: {},".format(self.step_response_keys(step_num, response_names, type_name, exp)))
        result.append("}\n")

        result.append('const instruction{}_procedure = '.format(pos))
        result.append('{')
        result.append('  timeline: [instruction{}_step],'.format(pos))
        result.append('  timeline_variables: instruction{}_data,'.format(pos))
        result.append('}')
        result.append("timeline.push(instruction{}_procedure);\n".format(pos))
        return "\n".join(result)

    # ------------------------------------------------------------
    #  Code replacing the ${trials} keyword
    # ------------------------------------------------------------
    # ----------------------------------------------------------------------------
    def generate_experiments(self, exp):
        lines = []
        for trial_type in exp.trial_types:
            lines.append(self.generate_trial_type(trial_type, exp))
        return "\n".join(lines)

    # ----------------------------------------------------------------------------
    def generate_trial_type(self, trial_type, exp):
        result = "const {}_data = [\n".format(trial_type)
        result += self.generate_trials(exp, trial_type) + "\n]\n"
        return result

    # ----------------------------------------------------------------------------
    def generate_trials(self, exp, trial_type):
        lines = []
        for trial in exp.trials:
            if trial.trial_type == trial_type:
                for line in self.generate_trial(trial, exp):
                    lines.append(line)

        return "\n".join(lines)

    # ----------------------------------------------------------------------------
    def generate_trial(self, trial, exp):
        result = []

        ttype = exp.trial_types[trial.trial_type]
        line_prefix = "{ "

        for step in ttype.steps:

            step_line = '{}{}: "'.format(line_prefix, self._step_name(step, ttype))

            # -- Add one <div> for each control
            for ctl_name in sorted(step.control_names):

                # -- <div> definition
                step_line += '<div class='.format(line_prefix, ctl_name) + "'" + ctl_name + "'"

                # -- Trial-specific formatting
                if ctl_name in trial.css:
                    for css_attr, value in trial.css[ctl_name].items():
                        step_line += " {}='{}'".format(css_attr, _to_str(value))

                step_line += '>'

                # -- Value of this control.
                # todo: Probably this would be needed only for TextControl; TBD later
                if ctl_name in trial.control_values:
                    step_line += trial.control_values[ctl_name]

                step_line += '</div>'

            step_line += '",'
            result.append(step_line)

            line_prefix = "  "

        result[-1] += " }, "

        return [(" " * 8) + r for r in result]

    # ------------------------------------------------------------
    #  Code replacing the ${trial_flow} keyword
    # ------------------------------------------------------------
    # ----------------------------------------------------------------------------
    def generate_trials_flow(self, exp):

        lst = [self.generate_trial_flow(exp, trial_type) for trial_type in exp.trial_types]
        return "\n".join(lst)

    # ----------------------------------------------------------------------------
    def generate_trial_flow(self, exp, trial_type):

        ttype = exp.trial_types[trial_type]
        step_type_def_lines = [line for step in ttype.steps for line in self.generate_trial_step_flow(step, ttype, exp)]

        trial_procedure_lines = self.trial_procedure_lines(ttype, exp)

        all_lines = [(" " * 4) + line for line in step_type_def_lines + [''] + trial_procedure_lines]
        return "\n".join(all_lines)

    # ----------------------------------------------------------------------------
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
            result.append("    choices: {},".format(self.step_response_keys(step.num, step.responses, ttype.name, exp)))
        else:
            self.logger('Error in compiler - step type {} not supported'.format(step_type.name))
            self.errors_found = True
            return ""

        if step.duration is not None:
            result.append("    trial_duration: {},".format(_to_str(step.duration)))

        result.append('}')

        return result

    # ----------------------------------------------------------------------------
    def _step_name(self, step, ttype):
        return '{}_step{}'.format(ttype.name, step.num)

    # ----------------------------------------------------------------------------
    def _step_type(self, step, ttype, exp):
        """
        Get the type of this step according to the controls it uses

        :return: StepType
        """
        print("start")
        for c in step.control_names:
            print(c)
        print("end")
        control_types = {type(exp.layout[c]) for c in step.control_names}
        if len(control_types) != 1:
            type_names = ", ".join([t.__name__ for t in control_types])
            self.logger.error(
                'Error in trial type {}: step #{} contains layout items of several types ({}), this is invalid'
                .format(ttype.name, step.num, type_names), 'MULTIPLE_CONTROL_TYPES_IN_ONE_STEP')
            return None

        control_type = list(control_types)[0]
        if control_type == expobj.TextControl:
            return StepType.html_kb_response
        else:
            self.logger.error('Error: unsupported layout-item type ({})'.format(control_type.__name__),
                              'MULTIPLE_CONTROL_TYPES_IN_ONE_STEP')
            return None

    # ----------------------------------------------------------------------------
    def step_response_keys(self, step_num, step_responses, type_name, exp):
        if step_responses is None:
            return 'jsPsych.NO_KEYS'

        invalid_resp = [r for r in step_responses if r not in exp.responses]
        if len(invalid_resp) > 0:
            self.logger.error('Error in trial type {}: step #{} contains some undefined responses ({})'
                              .format(type_name, step_num, ",".join(invalid_resp)),
                              'UNDEFINED_RESPONSE')
            self.errors_found = True
            return 'jsPsych.NO_KEYS'

        responses = [exp.responses[r] for r in step_responses]
        if len(responses) == 0:
            return 'jsPsych.NO_KEYS'
        else:
            return "[" + ", ".join(["'{}'".format(resp.key) for resp in responses]) + "]"

    # ----------------------------------------------------------------------------
    def trial_procedure_lines(self, ttype, exp):

        step_type_names = [self._step_name(step, ttype) for step in ttype.steps]

        result = []

        result.append('const {}_procedure = '.format(ttype.name))
        result.append('{')
        result.append('  timeline: [{}],'.format(", ".join(step_type_names)))
        result.append('  timeline_variables: {}_data,'.format(ttype.name))
        result.append('}')
        result.append('\ntimeline.push({}_procedure);\n'.format(ttype.name))

        return result
