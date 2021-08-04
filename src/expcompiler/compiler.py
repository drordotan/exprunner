
import webcolors
import re
from numbers import Number
import math

import expcompiler

_invalid_value = '__INVALID_VALUE__'


class Compiler(object):

    #-----------------------------------------------------------------------------
    def __init__(self, src_fn, target_fn, parser=None, logger=None):
        self.logger = logger or expcompiler.logger.Logger()
        self.parser = parser or expcompiler.xlsparser.XlsParser(src_fn, logger=self.logger)
        self.source_file = src_fn
        self.target_file = target_fn


    #-----------------------------------------------------------------------------
    # noinspection PyAttributeOutsideInit
    def compile(self):
        """
        Compile the experiment into a script.
        Returns True if succeeded, False if failed.
        """
        self.errors_found = False
        self.warnings_found = False

        if not self.parser.open():
            return 2

        exp = self.parse_experiment()
        if exp is None:
            return 2

        self.write_experiment()

        if self.errors_found:
            return 2
        elif self.warnings_found:
            return 1
        else:
            return 0


    #-----------------------------------------------------------------------------
    def parse_experiment(self):
        exp = self._create_experiment()
        self._parse_layouts(exp)

        return exp


    #-----------------------------------------------------------------------------
    def _create_experiment(self):
        df = self.parser.general_config()

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
            self._validate_color_code(background_color, expcompiler.xlsparser.XlsParser.ws_general, 'parameter "background_color"')

        exp = expcompiler.experiment.Experiment(get_subj_id=get_subj_id,
                                                get_session_id=get_session_id,
                                                results_filename=results_filename,
                                                background_color=background_color,
                                                full_screen=full_screen,
                                                instructions=self._get_param_multi_values(df, 'instructions'))

        return exp


    #-----------------------------------------------------------------------------
    def _get_param(self, df, param_name):
        """
        Get a config parameter from the "general" worksheet.
        There must be only one row with this parameter name
        """
        if df.shape[0] == 0:
            return None

        df = df[df.param.str.lower() == param_name]
        if df.shape[0] == 0:
            return None
        elif df.shape[0] == 1:
            return df.reset_index().value[0]
        else:
            self.logger.error('Error in worksheet {}: the parameter "{}" can only appear once but it appears 2 or more times'.
                              format(expcompiler.xlsparser.XlsParser.ws_general, param_name), 'MULTIPLE_PARAM_VALUES')


    #-----------------------------------------------------------------------------
    # noinspection PyMethodMayBeStatic
    def _get_param_multi_values(self, df, param_name):
        """
        Get a config parameter from the "general" worksheet.
        The parameter may have multiple values
        """
        if df.shape[0] == 0:
            return []

        return tuple(df.value[df.param.str.lower() == param_name])


    #-----------------------------------------------------------------------------
    def _parse_layouts(self, exp):
        """
        Parse the "layout" worksheet, which contains one line per control
        """
        df = self.parser.layout()
        for i, row in df.iterrows():
            ctl = self._parse_layout_control(exp, row, i+2)
            if ctl is not None:
                exp.layout[ctl.name] = ctl


    #-----------------------------------------------------------------------------
    def _parse_layout_control(self, exp, row, rownum):

        control_type = str(row.type).lower()

        if control_type == 'text':
            control = self._parse_text_control(row, rownum)

        else:
            self.logger.error('Error in worksheet {}, line {}: type="{}" is unknown, only "text" is supported'.
                              format(expcompiler.xlsparser.XlsParser.ws_layout, rownum, row.type), 'INVALID_CONTROL_TYPE')
            self.errors_found = True
            return None

        if control.name in exp.layout:
            self.logger.error('Error in worksheet {}, line {}: field_name "{}" was already used in a previous line. This line was ignored.'.
                              format(expcompiler.xlsparser.XlsParser.ws_layout, rownum, row.field_name), 'DUPLICATE_FIELD')
            self.errors_found = True
            return None

        return control


    #-----------------------------------------------------------------------------
    def _parse_text_control(self, row, rownum):

        text = ""
        x = 0
        y = 0
        css = None

        for col_name in row.index:
            if col_name.lower() in ('field_name', 'type'):
                pass

            elif col_name.lower() == 'x':
                x = self._parse_position(_nan_to_none(row.x), expcompiler.xlsparser.XlsParser.ws_layout, 'x', rownum)

            elif col_name.lower() == 'y':
                y = self._parse_position(_nan_to_none(row.y), expcompiler.xlsparser.XlsParser.ws_layout, 'y', rownum) if 'y' in row else 0

            elif col_name.lower() == 'text':
                text = str(row.text) if 'text' in row and not _isempty(row.text) else ""

            elif col_name.lower().startswith('css:'):
                css = css or {}
                css_field_name = col_name.lower()[4:]
                value = row[col_name]
                css[css_field_name] = "" if _isempty(value) else str(value)

            elif rownum == 2:  # this error is issued only once per column
                self.logger.error('Warning in worksheet {}: column name "{}" is invalid and was ignored.'.
                                  format(expcompiler.xlsparser.XlsParser.ws_layout, col_name), 'EXCESSIVE_COLUMN')
                self.warnings_found = True

        field_name = str(row.field_name)

        return expcompiler.experiment.TextControl(field_name, text, x, y, css)


    #-----------------------------------------------------------------------------
    def write_experiment(self):
        return True


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
            self.logger.error('Error in worksheet {}: The value of parameter "{}" is "{}"; this is invalid and was ignored. Please specify either "Y" or "N"'.
                              format(expcompiler.xlsparser.XlsParser.ws_general, param_name, value), 'INVALID_BOOL_PARAM')
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

        self.logger.error('WARNING in worksheet {}, in {}: the color "{}" seems invalid and may fail. '.format(ws_name, cell_name, color) +
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
                                  .format(expcompiler.xlsparser.XlsParser.ws_general, keyword), 'INVALID_FILENAME(SUBJ_ID)')
                self.errors_found = True

            elif keyword == 'session_id' and not session_id_available:
                self.logger.error('Error in worksheet "{}": invalid value for the "results_filename" parameter - the keyword "{}" cannot be used because you did not ask to obtain a session ID'
                                  .format(expcompiler.xlsparser.XlsParser.ws_general, keyword), 'INVALID_FILENAME(SESSION_ID)')
                self.errors_found = True

            elif keyword not in valid_keywords:
                self.logger.error('Error in worksheet "{}": invalid value for the "results_filename" parameter - the keyword "{}" is unknown'
                                  .format(expcompiler.xlsparser.XlsParser.ws_general, keyword), 'INVALID_FILENAME(UNKNOWN_KEYWORD)')
                self.errors_found = True

            remaining = m.group(2)


    #-----------------------------------------------------------------------------
    def _parse_number(self, value, ws_name, col_name, rownum):
        if value is None:
            self.logger.error('Error in worksheet {}, column {}, line {}: Empty value is invalid, expecting a number'
                              .format(ws_name, col_name, rownum), 'INVALID_NUMERIC_VALUE')
            self.errors_found = True
            return None

        try:
            value = float(value)
            return int(value) if value == int(value) else value

        except ValueError:
            pass

        self.logger.error('Error in worksheet {}, column {}, line {}: The value "{}" is invalid, expecting a number'
                          .format(ws_name, col_name, rownum, value), 'INVALID_NUMERIC_VALUE')
        self.errors_found = True
        return None


    #-----------------------------------------------------------------------------
    def _parse_position(self, value, ws_name, col_name, rownum):
        if value is None:
            self.logger.error('Error in worksheet {}, column {}, line {}: Empty value is invalid, '.format(ws_name, col_name, rownum) +
                              Compiler.valid_position, 'EMPTY_COORD')
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
            self.logger.error('Error in worksheet {}, column {}, line {}: The value "{}" is invalid, '.format(ws_name, col_name, rownum, value) +
                              Compiler.valid_position, 'INVALID_COORD')
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


#-----------------------------------------------------------------------------
def compile_exp(src_fn, target_fn, parser=None):
    compiler = Compiler(src_fn, target_fn, parser)
    return compiler.compile()
