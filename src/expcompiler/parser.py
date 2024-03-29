"""
Parse an excel file with the experiment definitions (stage 1 of the compilation)
"""

import webcolors
import re
from numbers import Number
import math
import cssutils

import expcompiler


_css_prefix = 'format:'

_valid_response_key_codes = 'Alt', 'AltGraph', 'CapsLock', 'Control', 'Fn', 'FnLock', 'Hyper', 'Meta', 'NumLock', 'ScrollLock', \
                            'Shift', 'Super', 'Symbol', 'SymbolLock', 'Enter', 'Tab', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'ArrowUp', \
                            'End', 'Home', 'PageDown', 'PageUp', 'Backspace', 'Clear', 'Copy', 'CrSel', 'Cut', 'Delete', 'EraseEof', 'ExSel', \
                            'Insert', 'Paste', 'Redo', 'Undo'

#===============================================================================================================================
class Parser(object):
    """
    Parse the experiment config (from xls file)
    """

    #-----------------------------------------------------------------------------
    def __init__(self, filename, reader=None, logger=None):
        self.logger = logger or expcompiler.logger.Logger()
        self.reader = reader or expcompiler.xlsreader.XlsReader(filename, logger=self.logger)
        self.errors_found = False
        self.warnings_found = False
        self._parsing_config = None


    #-----------------------------------------------------------------------------
    def parse(self, parsing_config=None):
        """
        Compile the experiment into a script.
        Returns True if succeeded, False if failed.

        :param parsing_config: a dict with various config parameters as for how to parse
        """
        self._parsing_config = parsing_config
        self.errors_found = False
        self.warnings_found = False

        if not self.reader.open():
            self.errors_found = True
            return None

        self._parsing_config = None

        return self.parse_experiment()


    #-----------------------------------------------------------------------------
    def _pconfig(self, param_name, default_value):
        """
        Get the value of one of the parsing-config parameters
        """
        assert param_name is not None
        if self._parsing_config is None or param_name not in self._parsing_config:
            return default_value

        return self._parsing_config[param_name]

    #-----------------------------------------------------------------------------
    def parse_experiment(self):
        exp = self.create_experiment()
        self.parse_layout(exp)
        self.parse_responses(exp)
        self.parse_trial_type(exp)
        self.parse_instructions(exp)
        self.parse_trials(exp)

        return exp


    #=========================================================================================
    # Parse the "general" tab
    #=========================================================================================

    #-----------------------------------------------------------------------------
    def create_experiment(self):

        df = self.reader.general_config()

        get_subj_id = self._get_bool_param(df, 'get_subj_id', False)
        get_session_id = self._get_bool_param(df, 'get_session_id', False)
        start_of_session_beep = self._get_bool_param(df, 'start_of_session_beep', False)
        results_filename_prefix = self._get_param(df, 'results_filename_prefix')

        background_color = self._get_param(df, 'background_color')
        if background_color is not None:
            self._validate_color_code(background_color, expcompiler.xlsreader.XlsReader.ws_general, 'parameter "background_color"')

        exp = expcompiler.experiment.Experiment(get_subj_id=get_subj_id,
                                                get_session_id=get_session_id,
                                                save_results=self._get_bool_param(df, 'save_results', False),
                                                results_filename=self._results_filename(results_filename_prefix, get_subj_id, get_session_id),
                                                background_color=background_color,
                                                full_screen=self._get_bool_param(df, 'full_screen', False),
                                                start_of_session_beep=start_of_session_beep,
                                                title=self._get_param(df, 'title', as_str=True) or '')
        return exp


    #-----------------------------------------------------------------------------
    def _get_param(self, df, param_name, as_str=False):
        """
        Get a config parameter from the "general" worksheet.
        There must be only one row with this parameter name
        """
        if df.shape[0] == 0:
            return None

        df = df[df.param.str.lower() == param_name]
        if df.shape[0] == 0:
            return None

        if df.shape[0] > 1:
            self.logger.error('Error in worksheet "{}": the parameter "{}" can only appear once but it appears 2 or more times'.
                              format(expcompiler.xlsreader.XlsReader.ws_general, param_name), 'MULTIPLE_PARAM_VALUES')
            self.errors_found = True

        result = df.reset_index().value[0]
        if as_str and result is not None:
            result = str(result)

        return result


    #-----------------------------------------------------------------------------
    def _get_bool_param(self, df, param_name, default_value):
        val = self._get_param(df, param_name)
        return self._parse_cfg_bool(val, param_name, default_value, allow_none=True)


    #-----------------------------------------------------------------------------
    # noinspection PyMethodMayBeStatic
    def _get_param_multi_values(self, df, param_name, as_str=False):
        """
        Get a config parameter from the "general" worksheet.
        The parameter may have multiple values
        """
        if df.shape[0] == 0:
            return []

        result = df.value[df.param.str.lower() == param_name]
        if as_str:
            result = [str(r) for r in result]

        return tuple(result)


    #-----------------------------------------------------------------------------
    def _parse_cfg_bool(self, value, param_name, default_value, allow_none=False):
        """
        Parse a parameter from the general-config worksheet
        The parameter represents a boolean value
        """
        if value is None and allow_none:
            return default_value

        value = "" if value is None else str(value).upper()

        if value in ('Y', 'YES', 'T', 'TRUE', '1'):
            return True

        elif value in ('N', 'NO', 'F', 'FALSE', '0'):
            return False

        else:
            self.logger.error('Error in worksheet "{}": The value of parameter "{}" is "{}"; this is invalid and was ignored. Please specify either "Y" or "N"'.
                              format(expcompiler.xlsreader.XlsReader.ws_general, param_name, value), 'INVALID_BOOL_PARAM')
            self.errors_found = True
            return default_value


    #-----------------------------------------------------------------------------
    def _results_filename(self, prefix, with_subj_id, with_session_id):

        if prefix is None or prefix == '':
            prefix = 'results'

        elif re.match('^[a-zA-Z_&$#-]+$', prefix) is None:
            self.logger.error('Error in worksheet "{}": Invalid "results_filename_prefix" ({})'.
                              format(expcompiler.xlsreader.XlsReader.ws_general, prefix) +
                              ' - it can contain only letters, digits, or the characters -,_,&,#,$',
                              'INVALID_FILENAME_PREFIX')
            self.errors_found = True
            prefix = 'results'

        fn = prefix

        if with_subj_id:
            fn += '_${subj_id}'

        if with_session_id:
            fn += '_${session_id}'

        return fn + "_${date}.csv"


    #=========================================================================================
    # Parse the "layout" tab
    #=========================================================================================

    #-----------------------------------------------------------------------------
    def parse_layout(self, exp):
        """
        Parse the "layout" worksheet, which contains one line per control
        """
        df = self.reader.layout()
        if df.shape[0] == 0:
            self.logger.error('Error in worksheet "{}": the worksheet is empty.'.format(expcompiler.xlsreader.XlsReader.ws_layout),
                              'NO_CONTROLS')
            self.errors_found = True
            return

        existing_cols_to_letter_mapping = _col_names_to_letters(df)

        for mandatory_col in ('layout_name', 'type'):
            ok = True
            if mandatory_col not in existing_cols_to_letter_mapping:
                self.logger.error('Error in worksheet "{}": Column "{}" is missing. All layouts were ignored.'
                                  .format(expcompiler.xlsreader.XlsReader.ws_layout, mandatory_col),
                                  'MISSING_COL')
                self.errors_found = True
                ok = False
            if not ok:
                return

        for i, row in df.iterrows():
            ctl = self._parse_layout_control(exp, row, i+2, existing_cols_to_letter_mapping)
            if ctl is not None:
                exp.layout[ctl.name] = ctl


    #-----------------------------------------------------------------------------
    def _parse_layout_control(self, exp, row, xls_line_num, existing_cols_to_letter_mapping):

        control_name = str(row['layout_name'])
        self._validate_control_name(control_name, existing_cols_to_letter_mapping, xls_line_num)

        control_type = str(row['type']).lower()

        if control_type == 'text':
            control = self._parse_text_control(control_name, row, xls_line_num, existing_cols_to_letter_mapping,
                                               expcompiler.xlsreader.XlsReader.ws_layout)

        else:
            self.logger.error('Error in worksheet "{}", cell {}{}: type="{}" is unknown, only "text" is supported'.
                              format(expcompiler.xlsreader.XlsReader.ws_layout, existing_cols_to_letter_mapping['type'], xls_line_num, row.type),
                              'INVALID_CONTROL_TYPE')
            self.errors_found = True
            return None

        if control.name.lower() in [k.lower() for k in exp.layout.keys()]:
            self.logger.error('Error in worksheet "{}", cell {}{}: a layout item named "{}" was already defined in a previous line. This line was ignored.'.
                              format(expcompiler.xlsreader.XlsReader.ws_layout, existing_cols_to_letter_mapping['layout_name'], xls_line_num, control.name),
                              'DUPLICATE_CONTROL_NAME')
            self.errors_found = True
            return None
        return control


    #-----------------------------------------------------------------------------
    def _validate_control_name(self, control_name, existing_cols_to_letter_mapping, xls_line_num):
        if re.match('^[a-zA-Z0-9_]+$', control_name) is not None:
            return

        self.logger.error('Error in worksheet "{}", cell {}{}: layout item name "{}" is invalid - only letters, digits, and _ are allowed in the name.'.
                          format(expcompiler.xlsreader.XlsReader.ws_layout, existing_cols_to_letter_mapping['layout_name'], xls_line_num, control_name),
                          'INVALID_CONTROL_NAME')
        self.errors_found = True

    #-----------------------------------------------------------------------------
    def _parse_text_control(self, control_name, row, xls_line_num, existing_cols_to_letter_mapping, ws_name):

        text = ""

        frame, frame_cols = self._parse_frame(row, xls_line_num, existing_cols_to_letter_mapping, ws_name)
        css, css_cols = self.parse_css(row, xls_line_num, existing_cols_to_letter_mapping)

        for col_name in row.index:
            if col_name.lower() in ('layout_name', 'type', 'explanation') + frame_cols + css_cols:
                pass

            elif col_name.lower() == 'text':
                text = str(row.text) if 'text' in row and not _isempty(row.text, also_empty_str=False) else ""

            elif xls_line_num == 2:  # this error is issued only once per column
                self.logger.error('Warning in worksheet "{}", column {}: the column name "{}" is invalid and was ignored.'.
                                  format(expcompiler.xlsreader.XlsReader.ws_layout, existing_cols_to_letter_mapping[col_name], col_name), 'EXCESSIVE_COLUMN')
                self.warnings_found = True

        return expcompiler.experiment.TextControl(control_name, text, frame, css)


    #-----------------------------------------------------------------------------
    def _parse_frame(self, row, xls_line_num, existing_cols_to_letter_mapping, ws_name):

        col_names_nocase_to_case = {col_name.lower(): col_name for col_name in row.index}
        found_cols = []

        coord_attrs = {}

        for attr in ('left', 'top', 'width', 'height'):
            if attr in col_names_nocase_to_case:
                coord_attrs[attr] = self._parse_coord(value=_nan_to_none(getattr(row, attr)),
                                                      ws_name=expcompiler.xlsreader.XlsReader.ws_layout,
                                                      col_name=col_names_nocase_to_case[attr],
                                                      xls_col=existing_cols_to_letter_mapping[attr],
                                                      xls_line_num=xls_line_num)
                found_cols.append(col_names_nocase_to_case[attr])
            else:
                coord_attrs[attr] = None

        border_color = None
        if 'border-color' in col_names_nocase_to_case:
            border_color = _nan_to_none(row['border-color'])
            if border_color is not None:
                self._validate_css_attr_value('border-color', border_color, ws_name,
                                              existing_cols_to_letter_mapping[col_names_nocase_to_case['border-color']],
                                              xls_line_num, 'border-color')
                found_cols.append('border-color')

        frame = expcompiler.experiment.Frame(coord_attrs['left'], coord_attrs['top'], coord_attrs['width'], coord_attrs['height'],
                                             border_color)
        return frame, tuple(found_cols)


    #-----------------------------------------------------------------------------
    def parse_css(self, row, xls_line_num, existing_cols_to_letter_mapping):

        css = {}
        used_cols = []

        for col_name in row.index:
            if col_name.lower().startswith(_css_prefix):
                used_cols.append(col_name)
                css_control_name = col_name.lower()[len(_css_prefix):]
                value = row[col_name]
                value = self._parse_css_value(_nan_to_none(value), expcompiler.xlsreader.XlsReader.ws_layout, col_name,
                                              existing_cols_to_letter_mapping[col_name], xls_line_num)
                if not _isempty(value):
                    css[css_control_name] = _to_str(value)

        return css, tuple(used_cols)


    #=========================================================================================
    # Parse the "response" sheet
    #=========================================================================================

    #-----------------------------------------------------------------------------
    def parse_responses(self, exp):
        """
        Parse the "trial_type" worksheet, which contains one line per trial type
        """
        df = self.reader.response_modes()
        if df is None:
            return

        existing_cols_to_letter_mapping = _col_names_to_letters(df)
        response_keys = set()

        for i, row in df.iterrows():
            self._parse_one_response(exp, row, i+2, existing_cols_to_letter_mapping, response_keys)


    #-----------------------------------------------------------------------------
    def _parse_one_response(self, exp, row, xls_line_num, existing_cols_to_letter_mapping, response_keys):

        resp_id = row['response_name']
        if _isempty(resp_id):
            self.logger.error('Error in worksheet "{}", cell {}{}: response name was not specified, please specify it'.
                              format(expcompiler.xlsreader.XlsReader.ws_response,
                                     existing_cols_to_letter_mapping['response_name'],
                                     xls_line_num,
                                     row.response_name),
                              'MISSING_RESPONSE_ID')
            self.errors_found = True
            resp_id = ''
        else:
            resp_id = str(resp_id).lower()

        value = _nan_to_none(row.value)
        if value is None or value == '':
            self.logger.error('Error in worksheet "{}", cell {}{}: value is empty, please specify it'.
                              format(expcompiler.xlsreader.XlsReader.ws_response, existing_cols_to_letter_mapping['value'], xls_line_num, value),
                              'MISSING_RESPONSE_VALUE')
            self.errors_found = True
            value = '(value not specified)'

        resp_type = str(row.type).lower()
        if resp_type == 'key':
            resp = self._parse_key_response(row, resp_id, value, response_keys, xls_line_num, existing_cols_to_letter_mapping)

        elif resp_type == 'button':
            resp = self._parse_button_response(row, resp_id, value, xls_line_num, existing_cols_to_letter_mapping,
                                               expcompiler.xlsreader.XlsReader.ws_response)

        else:
            self.logger.error('Error in worksheet "{}", cell {}{}: type="{}" is unknown, only "key" and "button" are supported'.
                              format(expcompiler.xlsreader.XlsReader.ws_response, existing_cols_to_letter_mapping['type'], xls_line_num, row.type),
                              'INVALID_RESPONSE_TYPE')
            self.errors_found = True
            return None

        if resp.resp_id.lower() in [r.lower() for r in exp.responses]:
            self.logger.error('Error in worksheet "{}", cell {}{}: response name="{}" was defined twice, this is invalid'.
                              format(expcompiler.xlsreader.XlsReader.ws_response, existing_cols_to_letter_mapping['response_name'],
                                     xls_line_num, row.response_name),
                              'DUPLICATE_RESPONSE_ID')
            self.errors_found = True
            return None

        if resp_id is not None:
            exp.responses[resp_id] = resp


    #-----------------------------------------------------------------------------
    def _parse_key_response(self, row, resp_id, value, response_keys, xls_line_num, existing_cols_to_letter_mapping):
        if 'key' not in existing_cols_to_letter_mapping:
            key = '`'
            if 'MISSING_KB_RESPONSE_KEY_COL' not in self.logger.err_codes:
                self.logger.error('Error in worksheet "{}": Column "key" was not specified, but it must exist for button responses'.
                                  format(expcompiler.xlsreader.XlsReader.ws_response), 'MISSING_KB_RESPONSE_KEY_COL')
                self.errors_found = True
        else:
            key = row.key
            if key == 'space':
                key = ' '

            if _isempty(key):
                self.logger.error('Error in worksheet "{}", cell {}{}: key was not specified, please specify it'.
                                  format(expcompiler.xlsreader.XlsReader.ws_response, existing_cols_to_letter_mapping['key'], xls_line_num),
                                  'MISSING_KB_RESPONSE_KEY')
                self.errors_found = True
                key = ''

            if len(key) != 1 and key not in _valid_response_key_codes:
                self.logger.error('Warning in worksheet "{}", cell {}{}: the key code "{}" may be incorrect, please double check it.\n'.
                                  format(expcompiler.xlsreader.XlsReader.ws_response, existing_cols_to_letter_mapping['key'], xls_line_num, key) +
                                  'Main supported keys are any single-character key, and: {}\n'.format(', '.join(_valid_response_key_codes)) +
                                  'For a full list of keys supported by jsPsych, see http://developer.mozilla.org/en-US/docs/Web/API/UI_Events/Keyboard_event_key_values',
                                  'UNKNOWN_KB_KEY_CODE')
                self.errors_found = True

            if key in response_keys:
                self.logger.error('Error in worksheet "{}", cell {}{}: key="{}" was used in more than one response type'.
                                  format(expcompiler.xlsreader.XlsReader.ws_response, existing_cols_to_letter_mapping['key'], xls_line_num, key),
                                  'DUPLICATE_RESPONSE_KEY')
                self.errors_found = True

            if key != '':
                response_keys.add(key)

        return expcompiler.experiment.KbResponse(resp_id, value, key)


    #-----------------------------------------------------------------------------
    def _parse_button_response(self, row, resp_id, value, xls_line_num, existing_cols_to_letter_mapping, ws_name):

        if 'text' not in existing_cols_to_letter_mapping:
            text = 'N/A'
            if 'MISSING_BUTTON_RESPONSE_TEXT_COL' not in self.logger.err_codes:
                self.logger.error('Error in worksheet "{}": Column "text" was not specified, but it must exist for button responses'.
                                  format(expcompiler.xlsreader.XlsReader.ws_response), 'MISSING_BUTTON_RESPONSE_TEXT_COL')
                self.errors_found = True
        else:
            text = '' if _isempty(row.text) else row.text

        frame, frame_cols = self._parse_frame(row, xls_line_num, existing_cols_to_letter_mapping, ws_name)

        return expcompiler.experiment.ClickButtonResponse(resp_id, value, text, None if len(frame_cols) == 0 else frame)


    #=========================================================================================
    # Parse the "instructions" sheet
    #=========================================================================================

    #-----------------------------------------------------------------------------
    def parse_instructions(self, exp):
        """
        Parse the "instructions" worksheet, which contains one line per trial type
        """
        df = self.reader.instructions_config()
        if df.shape[0] == 0 and self._pconfig('instructions_mandatory', True):
            self.logger.error('Warning: worksheet "{}" was not provided; no instructions will be shown.'.
                              format(expcompiler.xlsreader.XlsReader.ws_instructions),
                              'NO_INSTRUCTIONS')
            self.warnings_found = True
            return

        col_names = _col_names_to_letters(df)

        if 'text' not in col_names:
            self.logger.error('Error in worksheet "{}": Please add a column named "text", which specifies the text to show in the instructions page.'
                              .format(expcompiler.xlsreader.XlsReader.ws_instructions),
                              'INSTRUCTIONS_MISSING_TEXT_COL')
            self.errors_found = True
            return

        if 'responses' not in col_names:
            self.logger.error('Error in worksheet "{}": Please add a column named "responses", which specifies the response alternatives in each instructions page.'
                              .format(expcompiler.xlsreader.XlsReader.ws_instructions),
                              'INSTRUCTIONS_MISSING_RESPONSE_COL')
            self.errors_found = True
            return

        for i, row in df.iterrows():
            instruction = self._parse_instruction(exp, row, i+2, col_names)
            if instruction is not None:
                exp.instructions.append(instruction)


    #-----------------------------------------------------------------------------
    def _parse_instruction(self, exp, row, xls_line_num, col_names):
        """
        Parse one instruction - i.e. one line from the instructions worksheet

        :param exp: The Experiment object
        :param row: The row from the DataFrame
        :param xls_line_num: The Excel line number
        """

        text = self._parse_text(row, xls_line_num, col_names)
        response_names = self._parse_instruction_responses(exp, row, xls_line_num, col_names)

        if text is None or response_names is None:
            return None
        else:
            return expcompiler.experiment.Instruction(text, response_names)


    #-----------------------------------------------------------------------------
    def _parse_text(self, row, xls_line_num, col_names):

        if _isempty(row.text):
            self.logger.error('Error in worksheet "{}", cell {}{}: the instruction text is empty, this is invalid.'
                              .format(expcompiler.xlsreader.XlsReader.ws_instructions, col_names['text'], xls_line_num),
                              'INSTRUCTION_TEXT_MISSING')
            self.errors_found = True
            return None

        return str(row.text)


    #-----------------------------------------------------------------------------
    def _parse_instruction_responses(self, exp, row, xls_line_num, col_names):

        if 'responses' not in col_names or _isempty(row.responses):
            responses = ()
        else:
            responses = [r.strip() for r in row.responses.split(",") if r.strip() != '']

        #-- At least one response must exist
        if len(responses) == 0:
            self.logger.error('Error in worksheet "{}", line {}: An instruction page without any response is invalid.'
                              .format(expcompiler.xlsreader.XlsReader.ws_instructions, xls_line_num),
                              'INSTRUCTIONS_MUST_DEFINE_RESPONSE')
            self.errors_found = True
            return []

        #-- Avoid duplicate responses
        if len(responses) != len(set(responses)):
            self.logger.error('Warning in worksheet "{}", cell {}{}, column "responses": some responses were specified more than once (the duplicates were ignored).'
                              .format(expcompiler.xlsreader.XlsReader.ws_instructions, col_names['responses'], xls_line_num),
                              'INSTRUCTION_DUPLICATE_RESPONSES')
            self.warnings_found = True
            responses = list(set(responses))

        #-- Validate that the responses actually exist
        invalid_resp = [r for r in responses if r not in exp.responses]
        if len(invalid_resp) > 0:
            self.logger.error('Error in worksheet "{}", cell {}{}: the response(s) "{}" were not specified in the "{}" worksheet. They were ignored.'
                              .format(expcompiler.xlsreader.XlsReader.ws_instructions, col_names['responses'], xls_line_num, ",".join(invalid_resp),
                                      expcompiler.xlsreader.XlsReader.ws_response),
                              'INSTRUCTION_INVALID_RESPONSE_NAMES')
            self.errors_found = True
            responses = [r for r in responses if r not in invalid_resp]

        response_types = set([type(exp.responses[r]) for r in responses])
        if len(response_types) > 1:
            self.logger.error('Warning in worksheet "{}", cell {}{}: the response/s "{}" are of different types (keyboard, mouse, etc.).'
                              .format(expcompiler.xlsreader.XlsReader.ws_trial_type, col_names['responses'], xls_line_num, ",".join(responses)) +
                              'All responses in an instruction page must be of the same type.',
                              'INSTRUCTIONS_WITH_MULTIPLE_RESPONSE_TYPES')
            self.errors_found = True

        return responses

    #=========================================================================================
    # Parse the "trial_type" sheet
    #=========================================================================================

    #-----------------------------------------------------------------------------
    def parse_trial_type(self, exp):
        """
        Parse the "trial_type" worksheet, which contains one line per trial type
        """
        df = self.reader.trial_types()
        if df.shape[0] == 0:
            self.logger.error('Error in worksheet "{}": no trial types were specified.'.format(expcompiler.xlsreader.XlsReader.ws_trial_type),
                              'NO_TRIAL_TYPES')
            self.errors_found = True
            return

        col_names = _col_names_to_letters(df)
        last_type_name = None

        for i, row in df.iterrows():

            step, trial_type = self._parse_step(exp, row, last_type_name, i+2, col_names)

            if step is None:
                continue

            if trial_type not in exp.trial_types:
                exp.trial_types[trial_type] = expcompiler.experiment.TrialType(trial_type)
            exp.trial_types[trial_type].steps.append(step)
            last_type_name = trial_type


    #-----------------------------------------------------------------------------
    def _parse_step(self, exp, row, last_type_name, xls_line_num, col_names):
        """
        Parse one step of a trial - i.e. one line from the trial_types worksheet

        :param exp: The Experiment object
        :param row: The row from the DataFrame
        :param xls_line_num: The Excel line number
        :param col_names: Names of the columns that exist in this worksheet
        :param last_type_name: Name of the previous
        """

        type_name = self._parse_trial_type(row, last_type_name, xls_line_num, col_names)
        step_num = self._step_num(exp, type_name)
        response_names = self._parse_trial_type_responses(exp, row, xls_line_num, col_names)
        responses_defined = response_names is not None and len(response_names) > 0
        control_names = self._parse_trial_type_control_names(exp, row, xls_line_num, col_names, responses_defined)

        duration = self._parse_positive_number_or_param(row, 'duration', col_names, expcompiler.xlsreader.XlsReader.ws_trial_type,
                                                        xls_line_num, mandatory=False, default_value=None, zero_allowed=False, non_int_allowed=False)
        delay_before = self._parse_positive_number_or_param(row, 'delay-before', col_names, expcompiler.xlsreader.XlsReader.ws_trial_type,
                                                            xls_line_num, mandatory=False, default_value=0, zero_allowed=True, non_int_allowed=False)
        delay_after = self._parse_positive_number_or_param(row, 'delay-after', col_names, expcompiler.xlsreader.XlsReader.ws_trial_type,
                                                           xls_line_num, mandatory=False, default_value=0, zero_allowed=True, non_int_allowed=False)

        exp.url_parameters.extend(v for v in (duration, delay_before, delay_after) if isinstance(v, expcompiler.experiment.UrlParameter))

        if not responses_defined and duration is None:
            self.logger.error('Error in worksheet "{}", line {}: An unlimited-time step without response is invalid. Either "duration" or "responses" must be defined.'
                              .format(expcompiler.xlsreader.XlsReader.ws_trial_type, xls_line_num),
                              'MUST_DEFINE_RESPONSE_OR_DURATION')
            self.errors_found = True

        if delay_after is not None and 0 < delay_after <= 3:
            self.logger.error('Warning in worksheet "{}" in {}{}: the specified post-trial delay ({}) is very small. '
                              .format(expcompiler.xlsreader.XlsReader.ws_trial_type, col_names['delay-after'], xls_line_num, delay_after) +
                              'Note that this value should be specified in milliseconds.',
                              'WARN_POST_TRIAL_DELAY_SMALL')

        if type_name is None or control_names is None:
            step = None
        else:
            step = expcompiler.experiment.TrialStep(step_num, control_names, response_names, duration, delay_before, delay_after)

        return step, type_name


    #-----------------------------------------------------------------------------
    def _parse_trial_type(self, row, last_type_name, xls_line_num, col_names):

        if 'type_name' not in col_names:
            return expcompiler.experiment.TrialType.default_name

        type_name = row.type_name
        if _isempty(type_name):
            if last_type_name is None:
                type_name = expcompiler.experiment.TrialType.default_name
                self.logger.error('Error in worksheet "{}", cell {}{}: "type" was not specified. Type="{}" will be used, but this is invalid.'
                                  .format(expcompiler.xlsreader.XlsReader.ws_trial_type, col_names['type'], xls_line_num, type_name),
                                  'TRIAL_TYPE_MISSING')
                self.errors_found = True
            else:
                type_name = last_type_name
                self.logger.error(
                    'Warning in worksheet "{}", cell {}{}: "type_name" was not specified. Assuming this step belongs to the last specified trial type ({}).'
                    .format(expcompiler.xlsreader.XlsReader.ws_trial_type, col_names['type_name'], xls_line_num, type_name), 'TRIAL_TYPE_MISSING')
                self.warnings_found = True

        else:
            type_name = str(type_name)

        if type_name.lower() == 'type':
            self.logger.error('Error in worksheet "{}", cell {}{}: A trial type named "{}" is invalid.'
                              .format(expcompiler.xlsreader.XlsReader.ws_trial_type, col_names['type_name'], xls_line_num, type_name),
                              'TRIAL_TYPE_INVALID_TYPE_NAME')
            self.errors_found = True
            return None

        return type_name


    #-----------------------------------------------------------------------------
    # noinspection PyMethodMayBeStatic
    def _step_num(self, exp, trial_type):

        if trial_type in exp.trial_types:
            return len(exp.trial_types[trial_type].steps) + 1

        else:
            return 1


    #-----------------------------------------------------------------------------
    def _parse_trial_type_control_names(self, exp, row, xls_line_num, col_names, has_responses):

        layout_str = row['layout items']
        if _isempty(layout_str):
            if not has_responses:
                self.logger.error('Warning in worksheet "{}", cell {}{}: If this step has no responses, you must specify something in the "layout items" column. '
                                  .format(expcompiler.xlsreader.XlsReader.ws_trial_type, col_names['layout items'], xls_line_num), 'TRIAL_TYPE_NO_FIELDS')
                self.errors_found = True
            return ()
        else:
            control_names = [f.strip() for f in layout_str.split(",")]

        #-- Avoid duplicate controls
        if len(control_names) != len(set(control_names)):
            self.logger.error('Warning in worksheet "{}", cell {}{}: some layout items were specified more than once. The duplicates were ignored.'
                              .format(expcompiler.xlsreader.XlsReader.ws_trial_type, col_names['layout items'], xls_line_num),
                              'TRIAL_TYPE_DUPLICATE_CONTROLS')
            self.warnings_found = True
            control_names = list(set(control_names))

        #-- Validate that the fields actually exist
        invalid_controls = [ctl for ctl in control_names if ctl not in exp.layout]
        if len(invalid_controls) > 0:
            self.logger.error('Error in worksheet "{}", cell {}{}: the layout item/s "{}" were not specified in the "{}" worksheet. They were ignored.'
                              .format(expcompiler.xlsreader.XlsReader.ws_trial_type, col_names['layout items'],  xls_line_num, ",".join(invalid_controls),
                                      expcompiler.xlsreader.XlsReader.ws_layout),
                              'TRIAL_TYPE_INVALID_CONTROL_NAMES')
            self.errors_found = True
            control_names = [ctl for ctl in control_names if ctl not in invalid_controls]

        if len(control_names) == 0:
            return None

        return control_names


    #-----------------------------------------------------------------------------
    def _parse_trial_type_responses(self, exp, row, xls_line_num, col_names):

        if 'responses' not in col_names:
            return None

        responses_str = row.responses
        if _isempty(responses_str):
            return None
        else:
            responses = [r.strip() for r in responses_str.split(",")]

        #-- Avoid duplicate responses
        if len(responses) != len(set(responses)):
            self.logger.error('Warning in worksheet "{}", cell {}{}, column "responses": some responses were specified more than once (the duplicates were ignored).'
                              .format(expcompiler.xlsreader.XlsReader.ws_trial_type, col_names['responses'], xls_line_num),
                              'TRIAL_TYPE_DUPLICATE_RESPONSES')
            self.warnings_found = True
            responses = list(set(responses))

        #-- Validate that the responses actually exist
        invalid_resp = [r for r in responses if r not in exp.responses]
        if len(invalid_resp) > 0:
            self.logger.error('Error in worksheet "{}", cell {}{}: the response/s "{}" were not specified in the "{}" worksheet. They were ignored.'
                              .format(expcompiler.xlsreader.XlsReader.ws_trial_type, col_names['responses'], xls_line_num, ",".join(invalid_resp),
                                      expcompiler.xlsreader.XlsReader.ws_response),
                              'TRIAL_TYPE_INVALID_RESPONSE_NAMES')
            self.errors_found = True
            responses = [r for r in responses if r not in invalid_resp]

        if len(responses) == 0:
            return None

        response_types = set([type(exp.responses[r]) for r in responses])
        if len(response_types) > 1:
            self.logger.error('Warning in worksheet "{}", cell {}{}: the response/s "{}" are of several types. Normally, all responses in a single step are of the same type.'
                              .format(expcompiler.xlsreader.XlsReader.ws_trial_type, col_names['responses'], xls_line_num, ",".join(responses)),
                              'TRIAL_TYPE_MULTIPLE_RESPONSE_TYPES')
            self.warnings_found = True

        return responses


    #-----------------------------------------------------------------------------
    def _parse_positive_number_or_param(self, row, col_name, col_names, ws_name, xls_line_num, mandatory, default_value,
                                        zero_allowed=False, non_int_allowed=True):

        if col_name not in col_names or _isempty(row[col_name]):
            if mandatory:
                self.logger.error('Error in worksheet "{}", cell {}{}: column "{}" is missing'.format(ws_name, col_names[col_name], xls_line_num, col_name),
                                  'MISSING_COL')
                self.errors_found = True
                return default_value
            else:
                return default_value

        value = row[col_name]

        m = re.match('^param:([a-zA-Z][a-z0-9_]*)=(.+)$', str(value))

        if m is None:
            #-- A concrete value
            return self._check_positive_number(value, col_name, col_names, ws_name, xls_line_num, default_value, zero_allowed, non_int_allowed)

        else:
            #-- A URL parameter
            param_name = m.group(1)
            v = self._check_positive_number(m.group(2), col_name, col_names, ws_name, xls_line_num, default_value, zero_allowed, non_int_allowed)
            return expcompiler.experiment.UrlParameter(param_name, v)


    #-----------------------------------------------------------------------------
    def _check_positive_number(self, value, col_name, col_names, ws_name, xls_line_num, default_value, zero_allowed, non_int_allowed):

        try:
            fval = float(value)
        except ValueError:
            self.logger.error('Error in worksheet "{}", cell {}{} (column "{}"): the value "{}" is invalid (expecting a {} float number'
                              .format(ws_name, col_names[col_name], xls_line_num, col_name, value, 'non-negative' if zero_allowed else 'positive'),
                              'NON_NUMERIC_VALUE')
            self.errors_found = True
            return default_value

        if fval < 0 or (not zero_allowed and fval == 0):
            self.logger.error('Error in worksheet "{}", cell {}{} (column "{}"): the value "{}" is invalid (only value {} 0 is allowed)'
                              .format(ws_name, col_names[col_name], xls_line_num, col_name, value, '>=' if zero_allowed else '>'),
                              'INVALID_NUMERIC_VALUE')
            self.errors_found = True

        if not non_int_allowed and int(fval) != fval:
            self.logger.error('Error in worksheet "{}", cell {}{} (column "{}"): the value "{}" is invalid - only integer numbers are allowed here, no fractions'
                              .format(ws_name, col_names[col_name], xls_line_num, col_name, value),
                              'INVALID_NON_INT_VALUE')
            self.errors_found = True

        return int(fval) if int(fval) == fval else fval


    #=========================================================================================
    # Trials
    #=========================================================================================

    #-----------------------------------------------------------------------------
    def parse_trials(self, exp):

        if len(exp.trial_types) == 0:
            #-- Trials can't be parsed because there are no trial types
            self.logger.error('All trials were ignored because no trial types are defined', 'TRIALS_IGNORED')
            return

        df = self.reader.trials()
        if df.shape[0] == 0:
            self.logger.error('Error in worksheet "{}": no trials were specified.'.format(expcompiler.xlsreader.XlsReader.ws_trials),
                              'NO_TRIALS')
            self.errors_found = True
            return

        col_names = _col_names_to_letters(df)
        if 'type' not in col_names and len(exp.trial_types) > 1:
            self.logger.error('Error in worksheet "{}": When there is more than one trial type, you must specify the "type" column in this worksheet to indicate the type of each trial.'
                              .format(expcompiler.xlsreader.XlsReader.ws_trials), 'NO_TYPE_IN_TRIALS_WS')
            self.errors_found = True
            return

        data_col_names, save_col_names, formatting_cols = self._check_trials_col_names(col_names, exp)

        for i, row in df.iterrows():
            trial = self._parse_trial(exp, row, i+2, data_col_names, save_col_names, formatting_cols, col_names)
            if trial is not None:
                exp.trials.append(trial)
                
    #-----------------------------------------------------------------------------
    def _check_trials_col_names(self, col_names, exp):

        save_col_names = []
        data_col_names = []
        formatting_cols = []

        for col in col_names:

            if col == 'type':
                continue

            if col.lower().startswith('save:'):
                if re.match('^save:\\s*$', col.lower()):
                    self.logger.error(
                        'Error in worksheet "{}": A column named "save:" is invalid, you must write something after the "save:" (e.g., "save:xyz" if you want column "xyz" to appear in the output file).'
                        .format(expcompiler.xlsreader.XlsReader.ws_trials, col), 'TRIALS_INVALID_SAVE_COL')
                    self.errors_found = True
                else:
                    save_col_names.append(col)

                continue

            fmt_matcher = re.match('format:([^.]+)\\.(.+)', col)

            if fmt_matcher is not None:
                control_name = fmt_matcher.group(1)
                css_attr = fmt_matcher.group(2)
                if control_name in exp.layout:
                    formatting_cols.append((col, control_name, css_attr))
                else:
                    self.logger.error('Error in worksheet "{}", column {}: There is no layout item named "{}".'
                                      .format(expcompiler.xlsreader.XlsReader.ws_trials, col_names[col], control_name),
                                      'TRIALS_UNKNOWN_CONTROL')
                    self.errors_found = True

                continue

            if col in exp.layout:
                data_col_names.append(col)

            else:
                self.warnings_found = True

                if col.lower().startswith(_css_prefix):
                    self.logger.error('Error in worksheet "{}", column {}: Column name "{}" is invalid. To specify the formatting of a layout item,'
                                      .format(expcompiler.xlsreader.XlsReader.ws_trials, col_names[col], col) +
                                      ' the column name should be {}:LLL.CCC, where LLL is the layout item name and '.format(_css_prefix) +
                                      'CCC is the specific formatting (CSS) specifier',
                                      'TRIALS_INVALID_COL_NAME')
                else:
                    self.logger.error('Error in worksheet "{}", column {}: Column name "{}" is invalid. Specify one of the following:\n'
                                      .format(expcompiler.xlsreader.XlsReader.ws_trials, col_names[col], col) +
                                      '(1) A layout item name, to specify its value.\n' +
                                      '(2) {}:LLL.CCC for trial-specific formatting of a layout item, '.format(_css_prefix) +
                                      'where LLL is the layout item name and CCC is the specific formatting (CSS) specifier.\n' +
                                      '(3) save:CCC to save a value as-is to the results file (CCC is the column name in the results file)',
                                      'TRIALS_INVALID_COL_NAME')

        return data_col_names, save_col_names, formatting_cols


    #-----------------------------------------------------------------------------
    def _parse_trial(self, exp, row, xls_line_num, data_col_names, save_col_names, formatting_cols, all_col_names):

        if 'type' in all_col_names:
            type_name = row.type
        else:
            type_name = tuple(exp.trial_types.keys())[0]

        if _isempty(type_name):
            self.logger.error('Error in worksheet "{}", cell {}{}: Trial type was not specified.'
                              .format(expcompiler.xlsreader.XlsReader.ws_trials, all_col_names['type'], xls_line_num), 'TRIALS_NO_TRIAL_TYPE')
            self.errors_found = True
            return None

        if type_name not in exp.trial_types:
            self.logger.error('Error in worksheet "{}", line {}: Trial type "{}" was not defined in worksheet "{}". This trial was ignored.'
                              .format(expcompiler.xlsreader.XlsReader.ws_trials, xls_line_num, type_name,
                                      expcompiler.xlsreader.XlsReader.ws_trial_type), 'TRIALS_INVALID_TRIAL_TYPE')
            self.errors_found = True
            return None

        trial = expcompiler.experiment.Trial(type_name)
        ttype = exp.trial_types[type_name]

        #-- Columns indicating the main data of each control (e.g. the text)
        for col in data_col_names:
            value = row[col]
            trial.control_values[col] = str(value)

        #-- Columns indicating values to save as-is
        for col in save_col_names:
            saved_col = col[5:]
            value = _nan_to_none(row[col])
            if value is not None:
                trial.save_values[saved_col] = value

        #-- Columns indicating the formatting of various controls
        for col_name, control_name, css_attr in formatting_cols:
            value = _nan_to_none(row[col_name])
            if value is None:
                continue

            value = self._parse_css_value(value, expcompiler.xlsreader.XlsReader.ws_trials, col_name, all_col_names[col_name], xls_line_num)

            if control_name in ttype.control_names:
                trial.add_css(control_name, css_attr, value)      
            else:
                self.logger.error('Error in worksheet "{}", cell {}{}: Layout item "{}" is inactive for trials of type "{}".'
                                  .format(expcompiler.xlsreader.XlsReader.ws_trials, all_col_names[col_name], xls_line_num, control_name, ttype.name),
                                  'TRIALS_CSS_TRIALTYPE_MISMATCH')
                self.errors_found = True

        return trial


    #=========================================================================================
    # Helper funcs
    #=========================================================================================

    #-----------------------------------------------------------------------------
    def _validate_color_code(self, color, ws_name, cell_name):
        if color is None:
            color = ""

        #-- Check whether it's a valid color name
        try:
            webcolors.name_to_hex(color)
            return
        except ValueError:
            pass

        #-- Check whether it's a valid HEX color
        try:
            webcolors.hex_to_rgb(color)
            return
        except ValueError:
            pass

        self.logger.error('WARNING in worksheet "{}", in {}: the color "{}" seems invalid and may fail. '.format(ws_name, cell_name, color) +
                          'For an explanation about valid color speficication (as color name or color code), see http://htmlcolorcodes.com', 'INVALID_COLOR')
        self.warnings_found = True


    #-----------------------------------------------------------------------------
    def _parse_coord(self, value, ws_name, col_name, xls_col, xls_line_num, validate_message=None):

        if value is None:
            return None

        #-- Percentages are handled in excel as numeric values
        # noinspection PyTypeChecker
        if value == 0:
            return "0px"

        elif isinstance(value, Number) and (-1 <= value <= 1):
            # noinspection PyTypeChecker
            if value*100 == int(value*100):
                # noinspection PyTypeChecker
                return '{}%'.format(int(value*100))
            else:
                # noinspection PyTypeChecker
                return '{:.2f}%'.format(value*100)

        value = str(value)

        m = re.match('^(-?\\d+(\\.\\d+)?)(\\s*)((px)|%)$', value)
        if m is None:
            if validate_message is None:
                validate_message = 'expecting an x/y coordinate (i.e., a number with either "%" or "px" after it)'

            self.logger.error('Error in worksheet "{}", cell {}{} (column "{}"): The value "{}" is invalid, '.
                              format(ws_name, xls_col, xls_line_num, col_name, value) + validate_message,
                              'INVALID_COORD')
            self.errors_found = True
            return None

        return value
    
    #-----------------------------------------------------------------------------
    def _parse_css_value(self, value, ws_name, col_name, xls_col, xls_line_num):
        """
        Parse a cell with CSS formatting ("format:.....")
        """
        temp_col_name = col_name.lower().strip()

        # todo drorCR: temp_col_name.startswith("format:")
        if temp_col_name.find("format:") == -1 or value is None:
            #-- empty value / not a CSS definition
            return value
        
        temp_col_name = temp_col_name.replace("format:", "")

        if temp_col_name.find('.') != -1:
            [_, css_attr] = temp_col_name.split(".")
        else:
            css_attr = temp_col_name

        self._validate_css_attr_value(css_attr, value, ws_name, xls_col, xls_line_num, col_name)

        return value


    #-----------------------------------------------------------------------------
    def _validate_css_attr_value(self, css_attr, value, ws_name, xls_col, xls_line_num, col_name):

        try:
            css_property = cssutils.css.Property(css_attr, value)
            css_property._log.enabled = False
            valid_css_attr = css_property.validate()
        except:
            valid_css_attr = False

        if not valid_css_attr:
            error_message = "For more information about using this CSS attribute, see http://developer.mozilla.org/en-US/docs/Web/CSS/"+css_attr
            self.logger.error('Error in worksheet "{}", cell {}{} (column "{}"): The value "{}" is invalid, '.
                              format(ws_name, xls_col, xls_line_num, col_name, value) + error_message,
                              'INVALID_CSS_VALUE')
            self.errors_found = True


    valid_position = 'expecting an x/y coordinate (i.e., a number with either "%" or "px" after it)'


#-----------------------------------------------------------------------------
def _isempty(value, also_empty_str=True):
    # noinspection PyTypeChecker
    return value is None or (isinstance(value, Number) and math.isnan(value)) or (also_empty_str and value == '')


#-----------------------------------------------------------------------------
def _nan_to_none(value):
    return None if _isempty(value) else value


#-----------------------------------------------------------------------------
def _to_str(value):
    """Convert to string; make sure that integers are printed as such (even if their type is float)"""
    if isinstance(value, expcompiler.experiment.UrlParameter):
        return value.js_var_name

    try:
        value = int(value)
    except ValueError:
        pass
    return str(value)


#-----------------------------------------------------------------------------
def xls_col_letter(n):
    """
    Convert a column number (first col = 0) to an Excel column letter
    """
    if n < 26:
        return chr(n + ord('A'))
    else:
        n1 = n // 26
        n2 = n % 26
        return chr(n1+ord('A')) + chr(n2+ord('A'))


#-----------------------------------------------------------------------------
def _col_names_to_letters(df):
    """ Return the column names, and the number of each column as a letter """
    return {c: xls_col_letter(i) for i, c in enumerate(list(df))}
