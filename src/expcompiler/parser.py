"""
Parse an excel file with the experiment definitions (stage 1 of the compilation)
"""
import webcolors
import re
from numbers import Number
import math

import expcompiler


#todo support sounds

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


    #-----------------------------------------------------------------------------
    def parse(self):
        """
        Compile the experiment into a script.
        Returns True if succeeded, False if failed.
        """
        self.errors_found = False
        self.warnings_found = False

        if not self.reader.open():
            self.errors_found = True
            return None

        return self.parse_experiment()


    #-----------------------------------------------------------------------------
    def parse_experiment(self):
        exp = self.create_experiment()
        self.parse_layout(exp)
        self.parse_responses(exp)
        self.parse_trial_type(exp)
        self.parse_trials(exp)

        return exp


    #=========================================================================================
    # Parse the "general" tab
    #=========================================================================================

    #-----------------------------------------------------------------------------
    def create_experiment(self):

        df = self.reader.general_config()

        get_subj_id = self._get_param(df, 'get_subj_id')
        if get_subj_id is not None:
            get_subj_id = self._parse_cfg_bool(get_subj_id, 'get_subj_id', False)

        get_session_id = self._get_param(df, 'get_session_id')
        if get_session_id is not None:
            get_session_id = self._parse_cfg_bool(get_session_id, 'get_session_id', False)

        full_screen = self._get_param(df, 'full_screen')
        if full_screen is not None:
            full_screen = self._parse_cfg_bool(full_screen, 'full_screen', False)

        results_filename = self._get_param(df, 'results_filename')
        if results_filename is not None:
            self._validate_results_filename_keywords(results_filename, get_subj_id, get_session_id)

        background_color = self._get_param(df, 'background_color')
        if background_color is not None:
            self._validate_color_code(background_color, expcompiler.xlsreader.XlsReader.ws_general, 'parameter "background_color"')

        title = self._get_param(df, 'title', as_str=True) or ''
        instructions = self._get_param_multi_values(df, 'instructions', as_str=True)
        instructions = [i for i in instructions if not _isempty(i) and i != '']

        exp = expcompiler.experiment.Experiment(get_subj_id=get_subj_id,
                                                get_session_id=get_session_id,
                                                results_filename=results_filename,
                                                background_color=background_color,
                                                full_screen=full_screen,
                                                title=title,
                                                instructions=instructions)
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

        for i, row in df.iterrows():
            ctl = self._parse_layout_control(exp, row, i+2)
            if ctl is not None:
                exp.layout[ctl.name] = ctl


    #-----------------------------------------------------------------------------
    def _parse_layout_control(self, exp, row, xls_line_num):

        control_type = str(row.type).lower()

        if control_type == 'text':
            control = self._parse_text_control(row, xls_line_num)

        else:
            self.logger.error('Error in worksheet "{}", line {}: type="{}" is unknown, only "text" is supported'.
                              format(expcompiler.xlsreader.XlsReader.ws_layout, xls_line_num, row.type), 'INVALID_CONTROL_TYPE')
            self.errors_found = True
            return None

        if control.name in exp.layout:
            self.logger.error('Error in worksheet "{}", line {}: field_name "{}" was already used in a previous line. This line was ignored.'.
                              format(expcompiler.xlsreader.XlsReader.ws_layout, xls_line_num, row.field_name), 'DUPLICATE_FIELD')
            self.errors_found = True
            return None

        return control


    #-----------------------------------------------------------------------------
    def _parse_text_control(self, row, xls_line_num):

        text = ""
        x = 0
        y = 0
        css = None

        for col_name in row.index:
            if col_name.lower() in ('field_name', 'type'):
                pass

            elif col_name.lower() == 'x':
                x = self._parse_position(_nan_to_none(row.x), expcompiler.xlsreader.XlsReader.ws_layout, 'x', xls_line_num)

            elif col_name.lower() == 'y':
                y = self._parse_position(_nan_to_none(row.y), expcompiler.xlsreader.XlsReader.ws_layout, 'y', xls_line_num) if 'y' in row else 0

            elif col_name.lower() == 'text':
                text = str(row.text) if 'text' in row and not _isempty(row.text) else ""

            elif col_name.lower().startswith('css:'):
                css = css or {}
                css_field_name = col_name.lower()[4:]
                value = row[col_name]
                css[css_field_name] = "" if _isempty(value) else str(value)

            elif xls_line_num == 2:  # this error is issued only once per column
                self.logger.error('Warning in worksheet "{}": column name "{}" is invalid and was ignored.'.
                                  format(expcompiler.xlsreader.XlsReader.ws_layout, col_name), 'EXCESSIVE_COLUMN')
                self.warnings_found = True

        field_name = str(row.field_name)

        return expcompiler.experiment.TextControl(field_name, text, x, y, css)


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

        response_keys = set()

        for i, row in df.iterrows():
            self._parse_one_response(exp, row, i+2, tuple(df), response_keys)


    #-----------------------------------------------------------------------------
    def _parse_one_response(self, exp, row, xls_line_num, col_names, response_keys):

        resp_id = row.id
        if _isempty(resp_id) or resp_id == '':
            self.logger.error('Error in worksheet "{}", line {}: response id was not specified, please specify it'.
                              format(expcompiler.xlsreader.XlsReader.ws_response, xls_line_num, row.id), 'MISSING_RESPONSE_ID')
            self.errors_found = True
            resp_id = None
        else:
            resp_id = str(resp_id).lower()

        value = _nan_to_none(row.value)
        if value is None or value == '':
            self.logger.error('Error in worksheet "{}", line {}: value is empty, please specify it'.
                              format(expcompiler.xlsreader.XlsReader.ws_response, xls_line_num, value), 'MISSING_RESPONSE_VALUE')
            self.errors_found = True
            value = '(value not specified)'

        resp_type = str(row.type).lower()
        if resp_type == 'key':
            resp = self._parse_key_response(row, xls_line_num, resp_id, value, response_keys, col_names)

        elif resp_type == 'button':
            resp = self._parse_button_response(row, xls_line_num, resp_id, value, col_names)

        else:
            self.logger.error('Error in worksheet "{}", line {}: type="{}" is unknown, only "key" and "button" are supported'.
                              format(expcompiler.xlsreader.XlsReader.ws_response, xls_line_num, row.type), 'INVALID_RESPONSE_TYPE')
            self.errors_found = True
            return None

        if resp.resp_id in exp.responses:
            self.logger.error('Error in worksheet "{}", line {}: response id="{}" was defined twice, this is invalid'.
                              format(expcompiler.xlsreader.XlsReader.ws_response, xls_line_num, row.id), 'DUPLICATE_RESPONSE_ID')
            self.errors_found = True
            return None

        if resp_id is not None:
            exp.responses[resp_id] = resp


    #-----------------------------------------------------------------------------
    def _parse_key_response(self, row, xls_line_num, resp_id, value, response_keys, col_names):
        if 'key' not in col_names:
            key = '`'
            if 'MISSING_KB_RESPONSE_KEY_COL' not in self.logger.err_codes:
                self.logger.error('Error in worksheet "{}": Column "key" was not specified, but it must exist for button responses'.
                                  format(expcompiler.xlsreader.XlsReader.ws_response), 'MISSING_KB_RESPONSE_KEY_COL')
                self.errors_found = True
        else:
            key = row.key
            if _isempty(key) or key == '':
                self.logger.error('Error in worksheet "{}", line {}: key was not specified, please specify it'.
                                  format(expcompiler.xlsreader.XlsReader.ws_response, xls_line_num), 'MISSING_KB_RESPONSE_KEY')
                self.errors_found = True
                key = ''

            if key in response_keys:
                self.logger.error('Error in worksheet "{}", line {}: key="{}" was used in more than one response type'.
                                  format(expcompiler.xlsreader.XlsReader.ws_response, xls_line_num, key), 'DUPLICATE_RESPONSE_KEY')
                self.errors_found = True
            else:
                response_keys.add(key)

        return expcompiler.experiment.KbResponse(resp_id, value, key)


    #-----------------------------------------------------------------------------
    def _parse_button_response(self, row, xls_line_num, resp_id, value, col_names):

        if 'text' not in col_names:
            text = 'N/A'
            if 'MISSING_BUTTON_RESPONSE_TEXT_COL' not in self.logger.err_codes:
                self.logger.error('Error in worksheet "{}": Column "text" was not specified, but it must exist for button responses'.
                                  format(expcompiler.xlsreader.XlsReader.ws_response), 'MISSING_BUTTON_RESPONSE_TEXT_COL')
                self.errors_found = True
        else:
            text = row.text

        #todo x, y coordinates

        return expcompiler.experiment.ClickButtonResponse(resp_id, value, text)


    #=========================================================================================
    # Parse the "trial_type" sheet
    #=========================================================================================

    #-----------------------------------------------------------------------------
    def parse_trial_type(self, exp):
        """
        Parse the "trial_type" worksheet, which contains one line per trial type
        """
        df = self.reader.trial_type()
        if df.shape[0] == 0:
            self.logger.error('Error in worksheet "{}": no trial types were specified.'.format(expcompiler.xlsreader.XlsReader.ws_trial_type),
                              'NO_TRIAL_TYPES')
            self.errors_found = True
            return

        col_names = tuple(df)
        last_type_name = None

        for i, row in df.iterrows():

            step, trial_type = self._parse_step(exp, row, i+2, col_names, last_type_name)

            if step is None:
                continue

            if trial_type not in exp.trial_types:
                exp.trial_types[trial_type] = expcompiler.experiment.TrialType(trial_type)
            exp.trial_types[trial_type].steps.append(step)
            last_type_name = trial_type


    #-----------------------------------------------------------------------------
    def _parse_step(self, exp, row, xls_line_num, col_names, last_type_name):
        """
        Parse one step of a trial - i.e. one line from the trial_types worksheet

        :param exp: The Experiment object
        :param row: The row from the DataFrame
        :param xls_line_num: The Excel line number
        :param col_names: Names of the columns that exist in this worksheet
        :param last_type_name: Name of the previous
        """

        type_name = self._parse_trial_type(col_names, last_type_name, row, xls_line_num)
        step_num = self._step_num(exp, type_name)
        field_names = self._parse_trial_type_field_names(exp, row, xls_line_num)
        response_names = self._parse_trial_type_responses(exp, row, xls_line_num, col_names)

        duration = self._parse_positive_float(row, 'duration', col_names, expcompiler.xlsreader.XlsReader.ws_trial_type,
                                              xls_line_num, mandatory=False, default_value=None, zero_allowed=False)
        delay_before = self._parse_positive_float(row, 'delay-before', col_names, expcompiler.xlsreader.XlsReader.ws_trial_type,
                                                  xls_line_num, mandatory=False, default_value=0, zero_allowed=True)
        delay_after = self._parse_positive_float(row, 'delay-after', col_names,  expcompiler.xlsreader.XlsReader.ws_trial_type,
                                                 xls_line_num, mandatory=False, default_value=0, zero_allowed=True)

        #todo parse CSS entries

        if type_name is None or field_names is None:
            step = None
        else:
            step = expcompiler.experiment.TrialStep(step_num, field_names, response_names, duration, delay_before, delay_after)

        return step, type_name


    #-----------------------------------------------------------------------------
    def _parse_trial_type(self, col_names, last_type_name, row, xls_line_num):

        if 'type' not in col_names:
            return expcompiler.experiment.TrialType.default_name

        type_name = row.type
        if _isempty(type_name):
            if last_type_name is None:
                type_name = expcompiler.experiment.TrialType.default_name
                self.logger.error('Error in worksheet "{}", line {}: "type" was not specified. Type="{}" will be used, but this is invalid.'
                                  .format(expcompiler.xlsreader.XlsReader.ws_trial_type, xls_line_num, type_name), 'TRIAL_TYPE_MISSING')
                self.errors_found = True
            else:
                type_name = last_type_name
                self.logger.error(
                    'Warning in worksheet "{}", line {}: "type" was not specified. Assuming this step belongs to the last specified trial type ({}).'
                    .format(expcompiler.xlsreader.XlsReader.ws_trial_type, xls_line_num, type_name), 'TRIAL_TYPE_MISSING')
                self.warnings_found = True

        else:
            type_name = str(type_name)

        if type_name.lower() == 'type':
            self.logger.error('Error in worksheet "{}", line {}: A trial type named "{}" is invalid.'
                              .format(expcompiler.xlsreader.XlsReader.ws_trial_type, xls_line_num, type_name), 'TRIAL_TYPE_INVALID_TYPE_NAME')
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
    def _parse_trial_type_field_names(self, exp, row, xls_line_num):

        fields_str = row.fields
        if _isempty(fields_str) or fields_str == "":
            self.logger.error('Warning in worksheet "{}", line {}: No value was specified in the "fields" column.'
                              .format(expcompiler.xlsreader.XlsReader.ws_trial_type, xls_line_num), 'TRIAL_TYPE_NO_FIELDS')
            self.errors_found = True
            return ()
        else:
            fields = [f.strip() for f in fields_str.split(",")]

        #-- Avoid duplicate fields
        if len(fields) != len(set(fields)):
            self.logger.error('Warning in worksheet "{}", line {}, column "fields": some fields were specified more than once  (the duplicates were ignored).'
                              .format(expcompiler.xlsreader.XlsReader.ws_trial_type, xls_line_num), 'TRIAL_TYPE_DUPLICATE_FIELDS')
            self.warnings_found = True
            fields = list(set(fields))

        #-- Validate that the fields actually exist
        invalid_fields = [fld for fld in fields if fld not in exp.layout]
        if len(invalid_fields) > 0:
            self.logger.error('Error in worksheet "{}", line {}: the field/s "{}" were not specified in the "{}" worksheet. They were ignored.'
                              .format(expcompiler.xlsreader.XlsReader.ws_trial_type, xls_line_num, ",".join(invalid_fields),
                                      expcompiler.xlsreader.XlsReader.ws_layout), 'TRIAL_TYPE_INVALID_FIELD_NAMES')
            self.errors_found = True
            fields = [fld for fld in fields if fld not in invalid_fields]

        if len(fields) == 0:
            return None

        return fields


    #-----------------------------------------------------------------------------
    def _parse_trial_type_responses(self, exp, row, xls_line_num, col_names):

        if 'responses' not in col_names:
            return None

        responses_str = row.responses
        if _isempty(responses_str) or responses_str == "":
            return None
        else:
            responses = [r.strip() for r in responses_str.split(",")]

        #-- Avoid duplicate responses
        if len(responses) != len(set(responses)):
            self.logger.error('Warning in worksheet "{}", line {}, column "responses": some responses were specified more than once (the duplicates were ignored).'
                              .format(expcompiler.xlsreader.XlsReader.ws_trial_type, xls_line_num), 'TRIAL_TYPE_DUPLICATE_RESPONSES')
            self.warnings_found = True
            responses = list(set(responses))

        #-- Validate that the responses actually exist
        invalid_resp = [r for r in responses if r not in exp.responses]
        if len(invalid_resp) > 0:
            self.logger.error('Error in worksheet "{}", line {}: the response/s "{}" were not specified in the "{}" worksheet. They were ignored.'
                              .format(expcompiler.xlsreader.XlsReader.ws_trial_type, xls_line_num, ",".join(invalid_resp),
                                      expcompiler.xlsreader.XlsReader.ws_response), 'TRIAL_TYPE_INVALID_RESPONSE_NAMES')
            self.errors_found = True
            responses = [r for r in responses if r not in invalid_resp]

        if len(responses) == 0:
            return None

        response_types = set([type(exp.responses[r]) for r in responses])
        if len(response_types) > 1:
            self.logger.error('Warning in worksheet "{}", line {}: the response/s "{}" are of several types. Normally, all responses in a single step are of the same type.'
                              .format(expcompiler.xlsreader.XlsReader.ws_trial_type, xls_line_num, ",".join(responses)), 'TRIAL_TYPE_MULTIPLE_RESPONSE_TYPES')
            self.warnings_found = True

        return responses


    #-----------------------------------------------------------------------------
    def _parse_positive_float(self, row, col_name, col_names, ws_name, xls_line_num, mandatory, default_value, zero_allowed=False):

        if col_name not in col_names or _isempty(row[col_name]) or row[col_name] == '':
            if mandatory:
                self.logger.error('Error in worksheet "{}", line {}: column "{}" is missing'.format(ws_name, xls_line_num, col_name), 'MISSING_COL')
                self.errors_found = True
                return default_value
            else:
                return default_value

        value = row[col_name]
        try:
            fval = float(value)
        except ValueError:
            self.logger.error('Error in worksheet "{}", line {}, column "{}": the value "{}" is invalid (expecting a {} float number'
                              .format(ws_name, xls_line_num, col_name, value, 'non-negative' if zero_allowed else 'positive'), 'NON_NUMERIC_VALUE')
            self.errors_found = True
            return default_value

        if fval < 0 or (not zero_allowed and fval == 0):
            self.logger.error('Error in worksheet "{}", line {}, column "{}": the value "{}" is invalid (only value {} 0 is allowed)'
                              .format(ws_name, xls_line_num, col_name, value, '>=' if zero_allowed else '>'), 'INVALID_NUMERIC_VALUE')
            self.errors_found = True

        return fval


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

        col_names = tuple(df)
        if 'type' not in col_names and len(exp.trial_types) > 1:
            self.logger.error('Error in worksheet "{}": When there is more than one trial type, you must specify the "type" column in this worksheet to indicate the type of each trial.'
                              .format(expcompiler.xlsreader.XlsReader.ws_trials), 'NO_TYPE_IN_TRIALS_WS')
            self.errors_found = True
            return

        for i, row in df.iterrows():
            trial = self._parse_trial(exp, row, i+2, col_names)
            if trial is not None:
                exp.trials.append(trial)


    #-----------------------------------------------------------------------------
    def _parse_trial(self, exp, row, xls_line_num, col_names):

        if 'type' in col_names:
            type_name = row.type
        else:
            type_name = tuple(exp.trial_types.keys())[0]

        if _isempty(type_name) or type_name == '':
            self.logger.error('Error in worksheet "{}", line {}: Trial type was not specified.'
                              .format(expcompiler.xlsreader.XlsReader.ws_trials, xls_line_num), 'TRIALS_NO_TRIAL_TYPE')
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

        for col in col_names:
            if col == 'type' or col not in ttype.fields:
                continue
            value = row[col]
            if not _isempty(value) and value != '':
                trial.field_values[col] = str(value)

        return trial


    #=========================================================================================
    # Parsing specific fields
    #=========================================================================================

    #-----------------------------------------------------------------------------
    def _parse_cfg_bool(self, value, param_name, default_value, allow_empty=False):
        """
        Parse a parameter from the general-config worksheet
        The parameter represents a boolean value
        """
        value = "" if value is None else value.upper()

        if value in ('Y', 'YES', 'T', 'TRUE', '1'):
            return True

        elif value in ('N', 'NO', 'F', 'FALSE', '0'):
            return False

        elif value == "" and allow_empty:
            return default_value

        else:
            self.logger.error('Error in worksheet "{}": The value of parameter "{}" is "{}"; this is invalid and was ignored. Please specify either "Y" or "N"'.
                              format(expcompiler.xlsreader.XlsReader.ws_general, param_name, value), 'INVALID_BOOL_PARAM')
            self.errors_found = True
            return default_value


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
    def _validate_results_filename_keywords(self, filename, subj_id_available, session_id_available):

        valid_keywords = 'subj_id', 'session_id', 'date'

        remaining = filename
        while remaining is not None and remaining != "":
            m = re.match('^[^$]*\\${([^}]*)}(.*)$', remaining)
            if m is None:
                return
            keyword = m.group(1)
            if keyword == 'subj_id' and not subj_id_available:
                self.logger.error('Error in worksheet "{}": invalid value for the "results_filename" parameter - the keyword "{}" cannot be used because you did not ask to obtain the subject ID'
                                  .format(expcompiler.xlsreader.XlsReader.ws_general, keyword), 'INVALID_FILENAME(SUBJ_ID)')
                self.errors_found = True

            elif keyword == 'session_id' and not session_id_available:
                self.logger.error('Error in worksheet "{}": invalid value for the "results_filename" parameter - the keyword "{}" cannot be used because you did not ask to obtain a session ID'
                                  .format(expcompiler.xlsreader.XlsReader.ws_general, keyword), 'INVALID_FILENAME(SESSION_ID)')
                self.errors_found = True

            elif keyword not in valid_keywords:
                self.logger.error('Error in worksheet "{}": invalid value for the "results_filename" parameter - the keyword "{}" is unknown'
                                  .format(expcompiler.xlsreader.XlsReader.ws_general, keyword), 'INVALID_FILENAME(UNKNOWN_KEYWORD)')
                self.errors_found = True

            remaining = m.group(2)


    #-----------------------------------------------------------------------------
    def _parse_number(self, value, ws_name, col_name, xls_line_num):
        if value is None:
            self.logger.error('Error in worksheet "{}", column {}, line {}: Empty value is invalid, expecting a number'
                              .format(ws_name, col_name, xls_line_num), 'INVALID_NUMERIC_VALUE')
            self.errors_found = True
            return None

        try:
            value = float(value)
            return int(value) if value == int(value) else value

        except ValueError:
            pass

        self.logger.error('Error in worksheet "{}", column {}, line {}: The value "{}" is invalid, expecting a number'
                          .format(ws_name, col_name, xls_line_num, value), 'INVALID_NUMERIC_VALUE')
        self.errors_found = True
        return None


    #-----------------------------------------------------------------------------
    def _parse_position(self, value, ws_name, col_name, xls_line_num):
        if value is None:
            self.logger.error('Error in worksheet "{}", column {}, line {}: Empty value is invalid, '.format(ws_name, col_name, xls_line_num) +
                              Parser.valid_position, 'EMPTY_COORD')
            self.errors_found = True
            return None

        #-- Percentages are handled in excel as numeric values
        # noinspection PyTypeChecker
        if value == 0:
            return 0

        elif isinstance(value, Number) and (-1 <= value <= 1):
            # noinspection PyTypeChecker
            return '{:.2f}%'.format(value*100)

        value = str(value)

        m = re.match('^(-?\\d+(\\.\\d+)?)(\\s*)((px)|%)$', value)
        if m is None:
            self.logger.error('Error in worksheet "{}", column {}, line {}: The value "{}" is invalid, '.format(ws_name, col_name, xls_line_num, value) +
                              Parser.valid_position, 'INVALID_COORD')
            self.errors_found = True
            return None

        return value

    valid_position = 'expecting an x/y coordinate (i.e., a number with either "%" or "px" after it)'


#-----------------------------------------------------------------------------
def _isempty(value):
    # noinspection PyTypeChecker
    return value is None or (isinstance(value, Number) and math.isnan(value))


def _nan_to_none(value):
    return None if _isempty(value) else value

