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
        script = self.template
        script = script.replace('${title}', self.generate_title_code(exp))
        script = script.replace('${layout_css}', self.generate_layout_code(exp))
        script = script.replace('${url_parameters}', self.generate_url_parameters(exp))
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

        return "\n".join([tabs(2) + r for r in result])

    #----------------------------------------------------------------------------
    def generate_single_layout_css_text(self, ctl):
        """
        Generate the CSS for a single control
        """
        result = [".{}".format(ctl.name)+" {"]

        result.extend(tabs(1) + e for e in self.frame_css_entries(ctl.frame))
        result.extend(tabs(1) + '{}: {};'.format(k, v) for k, v in ctl.css.items())

        result.append("}")

        return result


    #----------------------------------------------------------------------------
    def frame_css_entries(self, frame):
        """ Generate the CSS entries for a Frame object """

        result = []

        if frame.top is not None or frame.left is not None:
            result.append('position: absolute;')

        if frame.top is not None:
            result.append('top: {};'.format(frame.top))

        if frame.left is not None:
            result.append('left: {};'.format(frame.left))

        result.append('width: {};'.format('100%' if frame.width is None else frame.width))

        if frame.height is not None:
            result.append('height: {};'.format(frame.height))

        if frame.border_color is not None:
            result.append('border-color: {};'.format(frame.border_color))

        return result


    #------------------------------------------------------------
    #  Code replacing the ${url_parameters} keyword
    #------------------------------------------------------------

    #------------------------------------------------------------
    def generate_url_parameters(self, exp):

        lines = []

        if len(exp.url_parameters) > 0:
            lines.append(tabs(2) + 'const url = new URL(window.location.href);')
            lines.append('')

        for param in exp.url_parameters:
            lines.append(tabs(2) + 'let param_{} = {};'.format(param.name, param.default_value))
            lines.append(tabs(2) + "const url_{} = url.searchParams.get('{}');".format(param.name, param.name))
            lines.append(tabs(2) + 'if (url_{}) {{'.format(param.name))
            lines.append(tabs(3) + '{} = url_{};'.format(param.js_var_name, param.name))
            lines.append(tabs(2) + '}')

        return '\n'.join(lines)


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
    # noinspection PyUnusedLocal
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
        
        if step_resposne_type is not None and step_resposne_type is not False:
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

    # ----------------------------------------------------------------------------
    def generate_trials_code(self, exp):
        """
        Generate an array with the data for each trial
        """
        lines = ['const trial_data = [']

        for config_trial_number, trial in enumerate(exp.trials):
            lines.extend(self.generate_one_trial_data(trial, exp, config_trial_number))

        lines.append('];')

        return "\n".join(lines)


    #----------------------------------------------------------------------------
    def generate_one_trial_data(self, trial, exp, config_trial_number):

        result = []

        ttype = exp.trial_types[trial.trial_type]

        for i_step, step in enumerate(ttype.steps):

            #-- Generate the HTML text for all controls of this step (one <div> for each control)
            controls_html = ''.join([self._one_control_html(ctl_name, trial, exp) for ctl_name in sorted(step.control_names)])

            step_line = '{ ' if i_step == 0 else '  '
            step_line += '{}: "{}", '.format(self._step_name(step, ttype), controls_html)

            if exp.save_results:

                save_values = {'stim_' + k: ('' if v == 'nan' else v) for k, v in trial.control_values.items()}
                save_values.update({'val_' + k: ('' if v == 'nan' else v) for k, v in trial.save_values.items()})

                save_html = ['{}: "{}", '.format(k, v) for k, v in save_values.items()]
                step_line += ''.join(save_html)

            step_line += 'config_trial_number: "{}", '.format(config_trial_number + 2)

            result.append(step_line)

        result[-1] += " }, "

        return [tabs(2) + r for r in result]


    #----------------------------------------------------------------------------
    def saved_data_custom_cols(self, exp):

        result = dict(config_trial_number='config_trial_number')

        for trial in exp.trials:

            for k in trial.control_values.keys():
                result[k] = 'stim_' + k

            for k in trial.save_values.keys():
                result[k] = 'val_' + k

        return result


    #----------------------------------------------------------------------------
    def _one_control_html(self, ctl_name, trial, exp):
        """
        Generate the HTML code (<div>) for a single control in one trial
        """

        html_of_css = self._generate_css_style_html_attr(trial.css[ctl_name]) if ctl_name in trial.css else ''

        ctl_value = ''
        if ctl_name in trial.control_values:
            ctl_value = trial.control_values[ctl_name]
        elif ctl_name in exp.layout:
            control = exp.layout[ctl_name]
            if hasattr(control, 'text') and control.text is not None:
                ctl_value = control.text

        html = "<div class='{}'{}>{}</div>".format(ctl_name, html_of_css, ctl_value)
        return html


    #----------------------------------------------------------------------------
    def _generate_css_style_html_attr(self, css_attrs):

        if len(css_attrs) == 0:
            return ''

        result = " style='"
        for css_attr, value in css_attrs.items():
            result += "{}: {};".format(css_attr, _to_str(value))
        return result + "'"


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

        if step_resposne_type is not None and step_resposne_type is not False:
            if step_resposne_type == StepType.html_button_response:
                trial_type_response = "jsPsychHtmlButtonResponse"
            else:
                trial_type_response = "jsPsychHtmlKeyboardResponse"
        else:
            trial_type_response = '' if step_type is None else step_type.js_type

        result.append('const ' + step_name + ' = {')
        result.append("    type: {},".format(trial_type_response))
        result.append("    stimulus: jsPsych.timelineVariable('{}'), ".format(step_name))
        
        if step_resposne_type is False:
            self.logger.error(
                 'Error in trial type {}: step #{} responses column contains multiple response types. '.format(ttype.name, step.num) +
                 'This is invalid - the response shoud be either buttons or keys.',
                 'MULTIPLE_CONTROL_TYPES_IN_ONE_STEP')
            return ""

        if step_resposne_type == StepType.html_kb_response or (step_resposne_type is None and step_type == StepType.html_kb_response):
            result.append("    choices: {},".format(self.step_response_keys(step.num, step.responses, ttype.name, exp)))

        elif step_resposne_type == StepType.html_button_response:
            n_specified_frames = sum(exp.responses[r].frame is not None for r in step.responses)
            if n_specified_frames > 0:
                button_html = [self.generate_button_html(exp.responses[r]) for r in step.responses]
                result.append('    button_html: [{}],'.format(', '.join("'{}'".format(h) for h in button_html)))

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
            result.append("    post_trial_gap: {},".format(_to_str(step.delay_after)))

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
            return "[" + ", ".join(["'{}'".format(resp.text) for resp in responses]) + "]"

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

    #----------------------------------------------------------------------------
    def generate_button_html(self, btn):

        button_html_css_attrs = self.frame_css_entries(btn.frame)
        return '<button style="vertical-align: top; {}">%choice%</button>'.format(' '.join(button_html_css_attrs))

    #----------------------------------------------------------------------------
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

        result = [
            'const {}_procedure = '.format(ttype.name),
            '{',
            tabs(1) + 'timeline: [{}],'.format(", ".join(step_type_names)),
            tabs(1) + 'timeline_variables: trial_data,']

        saved_data_col_names = self.saved_data_custom_cols(exp)
        if len(saved_data_col_names) > 0:
            result.append(tabs(1) + 'data: {')
            for column in saved_data_col_names:
                result.append(tabs(2) + '{}: jsPsych.timelineVariable("{}"),'.format(column, saved_data_col_names[column]))
            result.append(tabs(1) + '},')

        result.extend([
            '}',
            '',
            'timeline.push({}_procedure);\n'.format(ttype.name),
        ])

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


def tabs(n):
    return '    ' * n
