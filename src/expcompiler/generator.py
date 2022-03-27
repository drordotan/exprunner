"""
Generate the experiment script
"""

import os
import html
import enum

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
    html_mouse_response = 'html-mouse-response'


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
        self.trail_col = {}

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
        script = script.replace('${instructions}', self.generate_instructions_code(exp))
        script = script.replace('${trials}', self.generate_trials_code(exp))
        script = script.replace('${trial_flow}', self.generate_trial_flow_code(exp))
        script = script.replace('${on_finish}', self.generate_on_finsh_code(exp))

        return script

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
        choices = self.step_response_keys(step_num, response_names, type_name, exp)

        result = """
        const instruction${pos}_step =
        {
            type: jsPsychHtmlKeyboardResponse,
            stimulus: "<div>${instruction_text}</div>",
            choices: ${choices},
        }
        
        const instruction${pos}_flow =
        {
            timeline: [instruction${pos}_step]
        }
        
        timeline.push(instruction${pos}_flow);
        """.replace('${pos}', str(pos)).replace('${choices}', choices).replace('${instruction_text}', text)
        

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
        trial_index = 0
        for trial in exp.trials:
            if trial.trial_type == trial_type:
                trial_index += 1
                for line in self.generate_trial(trial, trial_index, exp):
                    lines.append(line)

        return "\n".join(lines)

    # ----------------------------------------------------------------------------
    def generate_trial(self, trial, trial_index, exp):
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
            
            #indexing will not working when remove null rows
            #step_line += "trial_index: %s, " % (trial_index)

            if exp.save_results:
                for col_name in trial.control_values:
                    step_line += '%s: "%s", ' % (col_name, trial.control_values[col_name] if trial.control_values[col_name] != 'nan' else '')
                    if col_name not in self.trail_col.keys():
                        self.trail_col[col_name] = "stim_{}".format(col_name)

                for col_name in trial.save_values:
                    step_line += '%s: "%s", ' % (col_name, trial.save_values[col_name] if trial.save_values[col_name] != 'nan' else '')
                    if col_name not in self.trail_col.keys():
                        self.trail_col[col_name] = "val_{}".format(col_name)

                for layout in trial.css:
                    for attr in trial.css[layout]:
                        formate_attr = attr.replace('-', '') 
                        col_name = layout + "_" + formate_attr
                        step_line += '%s: "%s", ' % (col_name, trial.css[layout][attr] if trial.css[layout][attr] != 'nan' else '')

                        if col_name not in self.trail_col.keys():
                            self.trail_col[col_name] = col_name
                #indexing will not working when remove null rows
                #self.trail_col["trial_index"] = "trial_index"
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

        result.append('const ' + step_name + ' = {')
        result.append("    type: {},".format('' if step_type is None else step_type.js_type))
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
        return 'trial_type_{}_step{}'.format(ttype.name, step.num)

    # ----------------------------------------------------------------------------
    def _step_type(self, step, ttype, exp):
        """
        Get the type of this step according to the controls it uses

        :return: StepType
        """
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

        step_type_names = [self._step_name(step, ttype) for step in ttype.steps]

        csv_field = []
        if exp.save_results:
            for column in self.trail_col:
                csv_field.append('%s: jsPsych.timelineVariable("%s")' % (self.trail_col[column], column))
        
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
    # Code to replace the ${on_finish} keyword
    #------------------------------------------------------------

    def generate_on_finsh_code(self, exp):
        if not exp.save_results:
            return ''
        
        filter_condidition = ""
        instructions_indexes = [pos for pos, instruction in enumerate(exp.instructions)]
        
        if len(instructions_indexes):
            filter_condidition = """
                data = data.filterCustom(function(trial) {
                    return %s.indexOf(trial.trial_index) == -1 && trial.rt != null;
                });
                
            """ % (json.dumps(instructions_indexes))

        keys_obj = {}

        for response in exp.responses.values():
            if isinstance(response, expcompiler.experiment.KbResponse):
                keys_obj[response.key] = response.value
        
        js_custom_code = """
            <keys_val>
            for (var trial_index = 0; trial_index < data.trials.length; trial_index++) {
                    <set_keys_val>
                    data.trials[trial_index].trial_number = trial_index + 1;
                }
        """

        if len(keys_obj.values()):
            js_custom_code = js_custom_code.replace("<keys_val>", "let keys_val = %s;" % (json.dumps(keys_obj))).replace("<set_keys_val>", "data.trials[trial_index].response_value = keys_val[data.trials[trial_index].response];")
        else:
            js_custom_code = js_custom_code.replace("<keys_val>", "").replace("<set_keys_val>", "")

        
        return """
        on_finish: function() {
            var data = jsPsych.data.get();
            %s
            data.ignore('internal_node_id').ignore('trial_type').ignore('stimulus').localSave('csv', %s);
        }
        """ % (filter_condidition + js_custom_code, "'"+ exp.results_filename + "'.replace('${date}', new Date().toISOString().slice(0, 10))")
