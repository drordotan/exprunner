"""
Generate the experiment script
"""

import os
import html

import expcompiler.experiment as expobj


class ExpGenerator(object):

    #----------------------------------------------------------------------------
    def __init__(self):
        self.template = self._load_template()


    #----------------------------------------------------------------------------
    def generate(self, exp):

        script = self.template

        if '${title}' in script:
            script = script.replace('${title}', self.generate_title_part(exp))

        if '${layout_css}' in script:
            script = script.replace('${layout_css}', self.generate_layout_css(exp))
        else:
            #todo error
            pass

        """
        if '${instructions}' in script:
            script = script.replace('${instructions}', self.generate_instructions(exp))

        if '${trials}' in script:
            script = script.replace('${trials}', self.generate_trials(exp))
        else:
            #todo error
            pass

        if '${trial_flow}' in script:
            script = script.replace('${trial_flow}', self.generate_trial_flow(exp))
        else:
            #todo error
            pass
        """

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
    def _load_template(self):
        template_filename = os.path.dirname(__file__) + os.sep + 'script_template.js'
        with open(template_filename, 'r') as fp:
            return fp.read()
