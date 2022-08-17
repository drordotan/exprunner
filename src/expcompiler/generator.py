"""
Generate the experiment script
"""

import os
import html
import enum
import numbers

import json

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

    html_kb_response = 'jsPsychHtmlKeyboardResponse'
    html_button_response = 'jsPsychHtmlButtonResponse'


#============================================================================================
class ExpGenerator(object):
    """
    Generate the HTML file for an experiment
    """

    # ----------------------------------------------------------------------------
    def __init__(self, logger):
        self.template = self._load_template()
        self.logger = logger
        self.errors_found = False
        self.trial_col = {}

    # ----------------------------------------------------------------------------
    def _load_template(self):
        """
        Load the template file (contains HTML text with placeholders for JS code)
        """
        template_filename = os.path.dirname(__file__) + os.sep + 'script_template.js'
        with open(template_filename, 'r') as fp:
            return fp.read()

    # ----------------------------------------------------------------------------
    def generate(self, exp):
        """
        Generate the HTML script for the given experiment.

        :type exp: expcompiler.experiment.Experiment
        """

        if exp is None:
            self.logger.error('Internal error: "exp" argument not provided', 'INTERNAL_ERROR')
            self.errors_found = True
            return None

        self.errors_found = False
        self.trial_col = {}
        script = self.template
        script = script.replace('${title}', self.generate_title_code(exp))
        script = script.replace('${layout_css}', self.generate_layout_code(exp))
        script = script.replace('${instructions}', self.generate_instructions_code(exp))
        script = script.replace('${trials}', self.generate_trials_code(exp))
        script = script.replace('${trial_flow}', self.generate_trial_flow_code(exp))
        script = script.replace('${filter_trials_func}', self.generate_filter_trials_func(exp))
        script = script.replace('${init_jspsych_params}', self.generate_init_jspysch_params(exp))
        script = script.replace('${results_filename}', self.generate_results_file_name(exp))

        return script


    #------------------------------------------------------------
    #  Code replacing the ${results_filename} keyword
    #------------------------------------------------------------

    def generate_results_file_name(self, exp):
        return "'"+exp.results_filename+"'.replace('${date}', new Date().toISOString().slice(0, 10))"


    #------------------------------------------------------------
    #  Code replacing the ${title} keyword
    #------------------------------------------------------------

    def generate_title_code(self, exp):
        return html.escape(exp.title or '')


    #------------------------------------------------------------
    #  Code replacing the ${layout} keyword
    #------------------------------------------------------------

    #----------------------------------------------------------------------------
    def generate_layout_code(self, exp):
        """ Main function in this part - returns the text replacing the ${layout} keyword """
        result = []
        for control in exp.layout.values():
            if isinstance(control, expobj.TextControl):
                result.extend(self.generate_single_layout_css_text(control))

        return "\n".join([(" " * 8) + r for r in result])

    #----------------------------------------------------------------------------
    def generate_single_layout_css_text(self, ctl):
        """
        Generate the CSS for a single control
        """
        result = [
            ".{}".format(ctl.name)+" {",
            "    top: {};".format(ctl.y),
            "    left: {};".format(ctl.x),
            "    width: {};".format(ctl.width)
        ]

        for k, v in ctl.css.items():
            result.append("    {}: {};".format(k, v))
        result.append("}")
        return result

    #------------------------------------------------------------
    #  Code replacing the ${instructions} keyword
    #------------------------------------------------------------

    # ------------------------------------------------------------
    # TODO: finish func generate_instructions
    def generate_instructions_code(self, exp):
        lst = []
        for pos, instruction in enumerate(exp.instructions):
            lst.append(self.generate_instruction(instruction, pos, exp))

        return "\n".join(lst)

    # ----------------------------------------------------------------------------
    def generate_instruction(self, instruction, pos, exp):

        text = instruction.text
        response_names = instruction.response_names

        #result = self.generate_instruction_type(pos, text, exp)
        result = self.generate_instruction_flow(exp, pos, text, response_names)
        return result

    # ----------------------------------------------------------------------------
    def generate_instruction_type(self, pos, text, exp):
        result = "const instruction{}_data = [\n".format(pos)
        result += "        { "
        result += "exp: \"<div>{}</div>\"".format(text)
        result += " }\n]\n"
        return result

    # ----------------------------------------------------------------------------
    def generate_instruction_flow(self, exp, pos, text, response_names):
        step_num = 'instruction{}_step = '.format(pos)
        type_name = 'instruction{} = '.format(pos)

        step_resposne_type = self.check_response_type(response_names, exp)
        trial_type_response = "jsPsychHtmlKeyboardResponse"
        
        if step_resposne_type is not None and step_resposne_type != False:
            if step_resposne_type == StepType.html_button_response:
                trial_type_response = "jsPsychHtmlButtonResponse"
        
        if step_resposne_type == StepType.html_button_response:
            choices = self.gen_choices_for_button_response_step(step_num, response_names, type_name, exp)
        else:
            choices = self.step_response_keys(step_num, response_names, type_name, exp)

        text = text.replace('\n', '<p>').replace('"', '\\"')

        result = """
        const instruction${pos}_step =
        {
            type: ${response_type},
            stimulus: "<div>${instruction_text}</div>",
            choices: ${choices},
        }
        
        const instruction${pos}_flow =
        {
            timeline: [instruction${pos}_step]
        }
        
        timeline.push(instruction${pos}_flow);
        """.replace('${pos}', str(pos)).replace('${choices}', choices).replace('${instruction_text}', text).replace("${response_type}", trial_type_response)

        return result

    #------------------------------------------------------------
    #  Code replacing the ${trials} keyword
    #------------------------------------------------------------

    #----------------------------------------------------------------------------
    def generate_trials_code(self, exp):
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
        for config_trial_number, trial in enumerate(exp.trials):
            if trial.trial_type == trial_type:
                for line in self.generate_trial(trial, exp, config_trial_number):
                    lines.append(line)

        return "\n".join(lines)

    # ----------------------------------------------------------------------------
    def generate_trial(self, trial, exp, config_trial_number):
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
                    step_line += " style='"
                    for css_attr, value in trial.css[ctl_name].items():
                        step_line += "{}: {};".format(css_attr, _to_str(value))
                    step_line += "'"
                step_line += '>'

                # -- Value of this control.
                # todo: Probably this would be needed only for TextControl; TBD later
                if ctl_name in trial.control_values:
                    step_line += trial.control_values[ctl_name] if trial.control_values[ctl_name] else '' 

                step_line += '</div>'

            step_line += '", '

            if exp.save_results:
                for col_name in trial.control_values:
                    step_line += '%s: "%s", ' % (col_name, trial.control_values[col_name] if trial.control_values[col_name] != 'nan' else '')
                    if col_name not in self.trial_col.keys():
                        self.trial_col[col_name] = "stim_{}".format(col_name)

                for col_name in trial.save_values:
                    step_line += '%s: "%s", ' % (col_name, trial.save_values[col_name] if trial.save_values[col_name] != 'nan' else '')
                    if col_name not in self.trial_col.keys():
                        self.trial_col[col_name] = "val_{}".format(col_name)
                        
            step_line += '%s: "%s", ' % ("config_trial_number", config_trial_number + 2)
            self.trial_col["config_trial_number"] = "config_trial_number"

            result.append(step_line)

            line_prefix = "  "

        result[-1] += " }, "

        return [(" " * 8) + r for r in result]

    # ------------------------------------------------------------
    #  Code replacing the ${trial_flow} keyword
    # ------------------------------------------------------------

    # ----------------------------------------------------------------------------
    def generate_trial_flow_code(self, exp):
        """
        Generate the full code replacing the ${trial_flow} keyword
        """

        #todo: probably need to create a single flow supporting all trial types (is this possible?)
        lst = [self.generate_flow_for_one_trial_type(exp, trial_type) for trial_type in exp.trial_types]
        return "\n".join(lst)

    # ----------------------------------------------------------------------------
    def generate_flow_for_one_trial_type(self, exp, trial_type):

        ttype = exp.trial_types[trial_type]
        step_type_def_lines = [line for step in ttype.steps for line in self.generate_flow_for_one_trial_step(step, ttype, exp)]

        trial_flow_lines = self.trial_flow_lines(ttype, exp)

        all_lines = [(" " * 4) + line for line in step_type_def_lines + [''] + trial_flow_lines]
        return "\n".join(all_lines)

    # ----------------------------------------------------------------------------
    def generate_flow_for_one_trial_step(self, step, ttype, exp):
        result = []

        step_name = self._step_name(step, ttype)
        step_type = self._step_type(step, ttype, exp)
        if step_type is None:
            self.errors_found = True
            return ""

        step_resposne_type = self.check_response_type(step.responses, exp)

        if step_resposne_type is not None and step_resposne_type != False:
            if step_resposne_type == StepType.html_button_response:
                trial_type_response = "jsPsychHtmlButtonResponse"
            else:
                trial_type_response = "jsPsychHtmlKeyboardResponse"
        else:
            trial_type_response = '' if step_type is None else step_type.js_type

        result.append('const ' + step_name + ' = {')
        result.append("    type: {},".format(trial_type_response))
        result.append("    stimulus: jsPsych.timelineVariable('{}'), ".format(step_name))
        
        if step_resposne_type == False:
            self.logger.error(
                 'Error in trial type {}: step #{} responses column contains multiple response types. '.format(ttype.name, step.num) +
                 'This is invalid - the response shoud be either buttons or keys.',
                 'MULTIPLE_CONTROL_TYPES_IN_ONE_STEP')
            return ""

        if step_resposne_type == StepType.html_kb_response or (step_resposne_type == None and step_type == StepType.html_kb_response):
            result.append("    choices: {},".format(self.step_response_keys(step.num, step.responses, ttype.name, exp)))

        elif step_resposne_type == StepType.html_button_response:
            result.append("    choices: {},".format(self.gen_choices_for_button_response_step(step.num, step.responses, ttype.name, exp)))
            result.append("    on_finish: function(data) {")
            result.extend(["       " + line for line in self.gen_button_response_step_on_finish_func(step, exp)])
            result.append("    },")

        else:
            self.logger.error('Error in compiler - step type {} not supported'.format(step_type.name), 'MULTIPLE_CONTROL_TYPES_IN_ONE_STEP')
            self.errors_found = True
            return ""

        if step.duration is not None:
            result.append("    trial_duration: {},".format(_to_str(step.duration)))

        if step.delay_after is not None:
            result.append("    post_trial_gap: {},".format(_to_str(step.duration)))

        result.append('}')

        return result

    # ----------------------------------------------------------------------------
    def _step_name(self, step, ttype):
        return 'trial_type_{}_step{}'.format(ttype.name, step.num)

    # ----------------------------------------------------------------------------
    def _step_type(self, step, ttype, exp):
        """
        Get the type of this step according to the controls it uses

        :return: StepType
        """
        control_types = {type(exp.layout[c]) for c in step.control_names}
        if len(control_types) > 1:
            type_names = ", ".join([t.__name__ for t in control_types])
            self.logger.error(
                'Error in trial type {}: step #{} contains layout items of several types ({}), this is invalid'
                .format(ttype.name, step.num, type_names), 'MULTIPLE_CONTROL_TYPES_IN_ONE_STEP')
            return None

        control_type = expobj.TextControl if len(control_types) == 0 else list(control_types)[0]
        if control_type == expobj.TextControl:
            return StepType.html_kb_response
        else:
            self.logger.error('Error: unsupported layout-item type ({})'.format(control_type.__name__),
                              'MULTIPLE_CONTROL_TYPES_IN_ONE_STEP')
            return None

    # ----------------------------------------------------------------------------
    def check_response_type(self, step_responses, exp):
        """
        Get the response type for this step
        Return False if response type is inconsistent, None if there is no response
        """

        if step_responses is None:
            return None

        response_type = None

        for resp_key in step_responses:
            if resp_key not in exp.responses:
                continue

            if isinstance(exp.responses[resp_key], expcompiler.experiment.KbResponse):
                curr_response_type = StepType.html_kb_response
            elif isinstance(exp.responses[resp_key], expcompiler.experiment.ClickButtonResponse):
                curr_response_type = StepType.html_button_response
            else:
                curr_response_type = None

            if response_type is not None and response_type != curr_response_type:
                return False

            response_type = curr_response_type

        return response_type
    
    # ----------------------------------------------------------------------------
    def gen_choices_for_button_response_step(self, step_num, step_responses, type_name, exp):
        invalid_resp = [r for r in step_responses if r not in exp.responses]
        if len(invalid_resp) > 0:
            self.logger.error('Error in trial type {}: step #{} contains some undefined responses ({})'
                              .format(type_name, step_num, ",".join(invalid_resp)),
                              'UNDEFINED_RESPONSE')
            self.errors_found = True
            return "[]"
        
        responses = [exp.responses[r] for r in step_responses]
        if len(responses) == 0:
            return "[]"
        else:
            return "[" + ", ".join(["'{}'".format(resp.button_text) for resp in responses]) + "]"

    # ----------------------------------------------------------------------------
    def gen_button_response_step_on_finish_func(self, step, exp):
        responses = [exp.responses[r] if r in exp.responses else None for r in step.responses]
        if None in responses:
            return []

        values = [_format_value_to_js(r.value) for r in responses if isinstance(r, expcompiler.experiment.ClickButtonResponse)]
        return [
            "response_values = [{}];".format(", ".join(values)),
            "data.response_value = response_values[data.response];",
        ]

    # ----------------------------------------------------------------------------
    def step_response_keys(self, step_num, step_responses, type_name, exp):

        if step_responses is None:
            return "'NO_KEYS'"

        for resp_key in step_responses:

            if exp.responses[resp_key].key == "ALL_KEYS":
                return "'ALL_KEYS'"

        invalid_resp = [r for r in step_responses if r not in exp.responses]
        if len(invalid_resp) > 0:
            self.logger.error('Error in trial type {}: step #{} contains some undefined responses ({})'
                              .format(type_name, step_num, ",".join(invalid_resp)),
                              'UNDEFINED_RESPONSE')
            self.errors_found = True
            return "'NO_KEYS'"

        responses = [exp.responses[r] for r in step_responses]
        if len(responses) == 0:
            return "'NO_KEYS'"
        else:
            return "[" + ", ".join(["'{}'".format(resp.key) for resp in responses]) + "]"

    # ----------------------------------------------------------------------------
    def trial_flow_lines(self, ttype, exp):
        """ Generate the code part describing the full trial flow of a given trial type """

        step_type_names = [self._step_name(step, ttype) for step in ttype.steps]

        csv_field = []
        if exp.save_results:
            for column in self.trial_col:
                csv_field.append('%s: jsPsych.timelineVariable("%s")'%(self.trial_col[column], column))
        
        jsDataAttr = ""
        if len(csv_field) > 0:
            jsDataAttr = "data: {%s}" % ", ".join(csv_field)

        result = [
            'const {}_procedure = '.format(ttype.name),
            '{',
            '  timeline: [{}],'.format(", ".join(step_type_names)),
            '  timeline_variables: {}_data,'.format(ttype.name),
            jsDataAttr,
            '}',
            '',
            'timeline.push({}_procedure);\n'.format(ttype.name),
        ]
        return result


    #------------------------------------------------------------
    # Code to replace the ${filter_trials_func} keyword
    #------------------------------------------------------------

    def generate_filter_trials_func(self, exp):

        result = []

        #-- Remove instruction trials
        instructions_indexes = [pos for pos, instruction in enumerate(exp.instructions)]
        if len(instructions_indexes) > 0:
            result.append("if ({}.indexOf(trial.trial_index) != -1) {{".format(json.dumps(instructions_indexes)))
            result.append("   return false;")
            result.append("}")

        #-- Remove trials without response
        if not exp.save_steps_without_responses:
            result.append("if (trial.rt == null) {")
            result.append("   return false;")
            result.append("}")

        result.append("return true;")

        return '\n'.join('                ' + line for line in result)


    #------------------------------------------------------------
    # Code to replace the ${init_jspsych_params} keyword
    #------------------------------------------------------------

    def generate_init_jspysch_params(self, exp):

        if exp.save_results:
            return "{on_finish: on_jspsych_finish}"
        else:
            return "{}"


def _format_value_to_js(value):
    if isinstance(value, numbers.Number):
        return str(value)
    else:
        return "'{}'".format(value)
