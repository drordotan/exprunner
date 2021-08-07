"""
Generate the experiment script
"""

import os
import html

import expcompiler.experiment as expobj
from expcompiler.parser import _to_str


class ExpGenerator(object):

    #----------------------------------------------------------------------------
    def __init__(self, logger):
        self.template = self._load_template()
        self.logger = logger
        self.errors_found = False


    #----------------------------------------------------------------------------
    def generate(self, exp):

        self.errors_found = False
        script = self.template

        script = script.replace('${title}', self.generate_title_part(exp))
        script = script.replace('${layout_css}', self.generate_layout_css(exp))
        # script = script.replace('${instructions}', self.generate_instructions(exp))
        script = script.replace('${trials}', self.generate_trials(exp))
        # script = script.replace('${trial_flow}', self.generate_trial_flow(exp))

        return script


    #----------------------------------------------------------------------------
    def generate_title_part(self, exp):
        return html.escape(exp.title or '')


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


    #----------------------------------------------------------------------------
    def generate_trials(self, exp):
        lines = [line for trial in exp.trials for line in self.generate_trial(trial, exp)]
        return "\n".join(lines)


    #----------------------------------------------------------------------------
    def generate_trial(self, trial, exp):
        result = []

        ttype = exp.trial_types[trial.trial_type]
        line_prefix = "{ "
        for ctl_name in sorted(ttype.control_names):
            line = '{}{}: "<div class='.format(line_prefix, ctl_name) + "'" + ctl_name + "'"
            if ctl_name in trial.css:
                for css_attr, value in trial.css[ctl_name].items():
                    line += " {}='{}'".format(css_attr, _to_str(value))
            line += '>'
            if ctl_name in trial.control_values:
                line += trial.control_values[ctl_name]
            line += '</div>", '
            line_prefix = "  "
            result.append(line)

        result[-1] += " }, "

        return [(" " * 8) + r for r in result]


    #----------------------------------------------------------------------------
    def _load_template(self):
        template_filename = os.path.dirname(__file__) + os.sep + 'script_template.js'
        with open(template_filename, 'r') as fp:
            return fp.read()
