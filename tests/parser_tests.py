
import unittest

from testutils import *


NO_VALUE = "__NO_VALUE__"


#-----------------------------------------------------------------------------
def test_parse(general=None, layout=None, trial_types=None, responses=None, trials=None, return_exp=False):

    reader = ReaderForTests(general=general, layout=layout, trial_types=trial_types, respones=responses, trials=trials)

    parser = ParserForTests(reader,
                            parse_layout=layout is not None,
                            parse_trial_types=trial_types is not None,
                            parse_trials=trials is not None)
    exp = parser.parse()

    if return_exp:
        return parser, exp
    else:
        return parser


#-----------------------------------------------------------------------------
# noinspection PyPep8Naming
def G(param_name, param_value):
    return dict(param=param_name, value=param_value)


#-----------------------------------------------------------------------------
# noinspection PyPep8Naming
def Text(ctl_name, text='', **kwargs):
    kwargs['name'] = ctl_name
    kwargs['type'] = 'text'
    kwargs['text'] = text
    return kwargs


#-----------------------------------------------------------------------------
# noinspection PyPep8Naming
def KbResponse(resp_id, value, key, **kwargs):
    kwargs['id'] = resp_id
    kwargs['type'] = 'key'
    kwargs['value'] = value
    kwargs['key'] = key
    return kwargs


#-----------------------------------------------------------------------------
# noinspection PyPep8Naming
def BtnResponse(resp_id, value, text, **kwargs):
    kwargs['id'] = resp_id
    kwargs['type'] = 'button'
    kwargs['value'] = value
    kwargs['text'] = text
    return kwargs


#-----------------------------------------------------------------------------
# noinspection PyPep8Naming
def TType(fields, **kwargs):
    kwargs['layout items'] = fields

    if 'delay_before' in kwargs:
        kwargs['delay-before'] = kwargs['delay_before']
        del kwargs['delay_before']

    if 'delay_after' in kwargs:
        kwargs['delay-after'] = kwargs['delay_after']
        del kwargs['delay_after']

    return kwargs


#-----------------------------------------------------------------------------
# noinspection PyPep8Naming,PyShadowingBuiltins
def Trial(type=NO_VALUE, **kwargs):
    if type != NO_VALUE:
        kwargs['type'] = type
    return kwargs


#=============================================================================================
class GeneralWsTests(unittest.TestCase):

    #--------------------------------------------------------
    # Specify subj ID
    #--------------------------------------------------------

    def test_specify_results_filename_subj_id_y(self):
        parser = test_parse(general=[G('get_subj_id', 'Y')])
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_specify_results_filename_subj_id_n(self):
        parser = test_parse(general=[G('get_subj_id', 'Y')])
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_specify_results_filename_subj_id_none(self):
        parser = test_parse(general=[G('get_subj_id', None)])
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_specify_results_filename_subj_id_empty(self):
        parser = test_parse(general=[G('get_subj_id', '')])
        self.assertTrue(parser.errors_found)
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_specify_results_filename_subj_id_invalid(self):
        parser = test_parse(general=[G('get_subj_id', 'xyz')])
        self.assertTrue(parser.errors_found)
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))


    #--------------------------------------------------------
    # Specify session ID
    #--------------------------------------------------------

    def test_specify_results_filename_session_id_y(self):
        parser = test_parse(general=[G('get_session_id', 'Y')])
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_specify_results_filename_session_id_n(self):
        parser = test_parse(general=[G('get_session_id', 'Y')])
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_specify_results_filename_session_id_none(self):
        parser = test_parse(general=[G('get_session_id', None)])
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_specify_results_filename_session_id_empty(self):
        parser = test_parse(general=[G('get_session_id', '')])
        self.assertTrue(parser.errors_found)

    def test_specify_results_filename_session_id_invalid(self):
        parser = test_parse(general=[G('get_session_id', 'xyz')])
        self.assertTrue(parser.errors_found)


    #--------------------------------------------------------
    # Specify results filename
    #--------------------------------------------------------

    def test_specify_results_filename_without_keywords(self):
        parser = test_parse(general=[G('results_filename', 'stam.pdf')])
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_specify_results_filename_with_date(self):
        parser = test_parse(general=[G('results_filename', 'a${date}.pdf')])
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_specify_results_filename_with_valid_subj_id(self):
        parser = test_parse(general=[G('results_filename', 'a${subj_id}.pdf'), G('get_subj_id', 'Y')])
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_specify_results_filename_with_invalid_subj_id(self):
        parser = test_parse(general=[G('results_filename', 'a${subj_id}.pdf')])
        self.assertTrue(parser.errors_found)
        self.assertTrue('INVALID_FILENAME(SUBJ_ID)' in parser.logger.err_codes, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_specify_results_filename_with_valid_session_id(self):
        parser = test_parse(general=[G('results_filename', 'a${session_id}.pdf'), G('get_session_id', 'Y')])
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_specify_results_filename_with_invalid_session_id(self):
        parser = test_parse(general=[G('results_filename', 'a${session_id}.pdf')])
        self.assertTrue(parser.errors_found)
        self.assertTrue('INVALID_FILENAME(SESSION_ID)' in parser.logger.err_codes, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_specify_results_filename_with_invalid_keyword(self):
        parser = test_parse(general=[G('results_filename', 'a${stam}.pdf')])
        self.assertTrue(parser.errors_found)
        self.assertTrue('INVALID_FILENAME(UNKNOWN_KEYWORD)' in parser.logger.err_codes, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    #--------------------------------------------------------
    # Specify background color
    #--------------------------------------------------------

    def test_specify_results_background_color_name(self):
        parser = test_parse(general=[G('background_color', 'white')])
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_specify_results_background_color_invalid_name(self):
        parser = test_parse(general=[G('background_color', 'bullshit')])
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertTrue(parser.warnings_found)

    def test_specify_results_background_color_hex(self):
        parser = test_parse(general=[G('background_color', '#FEFEFE')])
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_specify_results_background_color_invalid_hex(self):
        parser = test_parse(general=[G('background_color', '#FFFFFG')])
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertTrue(parser.warnings_found)

    #--------------------------------------------------------
    # Title
    #--------------------------------------------------------

    def test_title_default(self):
        parser, exp = test_parse(general=[], return_exp=True)
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertEqual('', exp.title)

    def test_title_none(self):
        parser, exp = test_parse(general=[G('title', None)], return_exp=True)
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertEqual('', exp.title)

    def test_title_str(self):
        parser, exp = test_parse(general=[G('title', 'my title')], return_exp=True)
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertEqual('my title', exp.title)

    def test_title_numeric(self):
        parser, exp = test_parse(general=[G('title', 5)], return_exp=True)
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertEqual('5', exp.title)

    def test_title_duplicate(self):
        parser, exp = test_parse(general=[G('title', 't1'), G('title', 't2')], return_exp=True)
        self.assertTrue(parser.errors_found)
        self.assertTrue('MULTIPLE_PARAM_VALUES' in parser.logger.err_codes, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertEqual('t1', exp.title)


    #--------------------------------------------------------
    # Instructions
    #--------------------------------------------------------

    def test_instructions_default(self):
        parser, exp = test_parse(general=[], return_exp=True)
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertEqual((), exp.instructions)

    def test_instructions_once(self):
        parser, exp = test_parse(general=[G('instructions', 'line 1')], return_exp=True)
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertEqual(('line 1', ), exp.instructions)

    def test_instructions_once_numeric(self):
        parser, exp = test_parse(general=[G('instructions', 1)], return_exp=True)
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertEqual(('1', ), exp.instructions)

    def test_instructions_multiple(self):
        parser, exp = test_parse(general=[G('instructions', 'line 1'), G('instructions', 'line 2'), G('instructions', 'line 3')], return_exp=True)
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertEqual(('line 1', 'line 2', 'line 3'), exp.instructions)

    def test_instructions_empty_value_ignored(self):
        parser, exp = test_parse(general=[G('instructions', 'line 1'), G('instructions', ''), G('instructions', 'line 3')], return_exp=True)
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertEqual(('line 1', 'line 3'), exp.instructions)


#=============================================================================================
class LayoutTests(unittest.TestCase):

    #--------------------------------------------------------
    def test_minimal_valid_definitions(self):
        parser = test_parse(layout=[Text('field1'), Text('field2')])
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_minimal_valid_definitions_with_text(self):
        parser = test_parse(layout=[Text('field1', text='hello')])
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    #--------------------------------------------------------
    def test_no_layouts(self):
        parser = test_parse(layout=[])
        self.assertTrue(parser.errors_found)

    #--------------------------------------------------------
    # Specify position
    #--------------------------------------------------------

    def test_specify_x_as_pcnt(self):
        parser, exp = test_parse(layout=[Text('field1', x='50%')], return_exp=True)
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertEqual('50%', list(exp.layout.values())[0].x)

    def test_specify_y_as_pcnt(self):
        parser, exp = test_parse(layout=[Text('field1', y='-50%')], return_exp=True)
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertEqual('-50%', list(exp.layout.values())[0].y)

    def test_specify_x_as_px(self):
        parser, exp = test_parse(layout=[Text('field1', x='-50px')], return_exp=True)
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertEqual('-50px', list(exp.layout.values())[0].x)

    def test_specify_y_as_px(self):
        parser, exp = test_parse(layout=[Text('field1', y='5000px')], return_exp=True)
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertEqual('5000px', list(exp.layout.values())[0].y)

    def test_specify_width_as_px(self):
        parser, exp = test_parse(layout=[Text('field1', width='30px')], return_exp=True)
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertEqual('30px', list(exp.layout.values())[0].width)

    def test_specify_x_in_invalid_format(self):
        parser = test_parse(layout=[Text('field1', x='5000')])
        self.assertTrue(parser.errors_found)
        self.assertTrue('INVALID_COORD' in parser.logger.err_codes, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_specify_y_in_invalid_format(self):
        parser = test_parse(layout=[Text('field1', y='--500')])
        self.assertTrue(parser.errors_found)
        self.assertTrue('INVALID_COORD' in parser.logger.err_codes, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_missing_x(self):
        parser = test_parse(layout=[Text('field1', x=None)])
        self.assertTrue(parser.errors_found)
        self.assertTrue('EMPTY_COORD' in parser.logger.err_codes, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))


    #--------------------------------------------------------
    # Errors
    #--------------------------------------------------------

    def test_invalid_control_type(self):
        parser = test_parse(layout=[dict(field_name='fld', type='magic')])
        self.assertTrue(parser.errors_found)
        self.assertTrue('INVALID_CONTROL_TYPE' in parser.logger.err_codes, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_duplicate_field_names_are_invalid(self):
        parser = test_parse(layout=[Text('field1'), Text('field2'), Text('field1')])
        self.assertTrue(parser.errors_found)
        self.assertTrue('DUPLICATE_CONTROL_NAME' in parser.logger.err_codes, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_excessive_column_yield_warning(self):
        parser = test_parse(layout=[Text('field1', stam=1)])
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertTrue(parser.warnings_found)
        self.assertTrue('EXCESSIVE_COLUMN' in parser.logger.err_codes, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))


#=============================================================================================
class ResponsesTests(unittest.TestCase):

    def test_resp_id_none(self):
        parser = test_parse(responses=[KbResponse(None, 1, '/')])
        self.assertTrue(parser.errors_found)
        self.assertTrue('MISSING_RESPONSE_ID' in parser.logger.err_codes, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_resp_id_empty(self):
        parser = test_parse(responses=[KbResponse('', 1, '/')])
        self.assertTrue(parser.errors_found)
        self.assertTrue('MISSING_RESPONSE_ID' in parser.logger.err_codes, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_resp_value_none(self):
        parser = test_parse(responses=[KbResponse('id1', None, '/')])
        self.assertTrue(parser.errors_found)
        self.assertTrue('MISSING_RESPONSE_VALUE' in parser.logger.err_codes, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_resp_value_empty(self):
        parser = test_parse(responses=[KbResponse('id1', '', '/')])
        self.assertTrue(parser.errors_found)
        self.assertTrue('MISSING_RESPONSE_VALUE' in parser.logger.err_codes, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_invalid_response_type(self):
        parser = test_parse(responses=[dict(id='r1', type='badtype', value=1)])
        self.assertTrue(parser.errors_found)
        self.assertTrue('INVALID_RESPONSE_TYPE' in parser.logger.err_codes, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))


    #--------------------------------------------------------
    # Keyboard responses
    #--------------------------------------------------------

    def test_kbresp_valid(self):
        parser = test_parse(responses=[KbResponse('r1', 1, '/')])
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_kbresp_key_missing_col(self):
        parser = test_parse(responses=[dict(id='r1', type='key', value=1)])
        self.assertTrue(parser.errors_found)
        self.assertTrue('MISSING_KB_RESPONSE_KEY_COL' in parser.logger.err_codes, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_kbresp_key_empty(self):
        parser = test_parse(responses=[KbResponse('r1', 1, '')])
        self.assertTrue(parser.errors_found)
        self.assertTrue('MISSING_KB_RESPONSE_KEY' in parser.logger.err_codes, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_kbresp_key_none(self):
        parser = test_parse(responses=[KbResponse('r1', 1, None)])
        self.assertTrue(parser.errors_found)
        self.assertTrue('MISSING_KB_RESPONSE_KEY' in parser.logger.err_codes, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_kbresp_duplicate_keys_are_invalid(self):
        parser = test_parse(responses=[KbResponse('r1', 1, '/'), KbResponse('r2', 2, '/')])
        self.assertTrue(parser.errors_found)
        self.assertTrue('DUPLICATE_RESPONSE_KEY' in parser.logger.err_codes, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_kbresp_duplicate_response_ids_are_invalid(self):
        parser = test_parse(responses=[KbResponse('r1', 1, '/'), KbResponse('r1', 2, '.')])
        self.assertTrue(parser.errors_found)
        self.assertTrue('DUPLICATE_RESPONSE_ID' in parser.logger.err_codes, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    #--------------------------------------------------------
    # Button responses
    #--------------------------------------------------------

    def test_btnresp_valid(self):
        parser = test_parse(responses=[BtnResponse('r1', 1, 'Click me')])
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_btnresp_text_missing(self):
        parser = test_parse(responses=[dict(id='r1', type='button', value=1)])
        self.assertTrue(parser.errors_found)
        self.assertTrue('MISSING_BUTTON_RESPONSE_TEXT_COL' in parser.logger.err_codes, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))


#=============================================================================================
class TrialTypesTests(unittest.TestCase):

    def test_no_types(self):
        parser = test_parse(trial_types=[])
        self.assertTrue(parser.errors_found)

    #--------------------------------------------------------
    # Type name
    #--------------------------------------------------------

    def test_invalid_type_name(self):
        parser = test_parse(trial_types=[TType('f1,f2', type='type')])
        self.assertTrue(parser.errors_found)
        self.assertTrue('TRIAL_TYPE_INVALID_TYPE_NAME' in parser.logger.err_codes, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    #--------------------------------------------------------
    # Fields
    #--------------------------------------------------------

    def test_valid_fields(self):
        parser, exp = test_parse(trial_types=[TType('a, b', type='t')], layout=[Text('a', 'text1'), Text('b', 'text2')], return_exp=True)
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        fields = exp.trial_types['t'].control_names
        self.assertTrue('a' in fields, 'Field names: ' + ",".join(fields))
        self.assertTrue('b' in fields, 'Field names: ' + ",".join(fields))

    def test_valid_fields_with_numeric_name(self):
        parser = test_parse(trial_types=[TType('1, 2', type='t')], layout=[Text(1, 'text1'), Text(2, 'text2')])
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_fields_empty(self):
        parser = test_parse(trial_types=[TType('', type='t')])
        self.assertTrue(parser.errors_found)
        self.assertTrue('TRIAL_TYPE_NO_FIELDS' in parser.logger.err_codes, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_fields_none(self):
        parser = test_parse(trial_types=[TType(None, type='t')])
        self.assertTrue(parser.errors_found)
        self.assertTrue('TRIAL_TYPE_NO_FIELDS' in parser.logger.err_codes, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_duplicate_field_names(self):
        parser = test_parse(trial_types=[TType('a,a', type='t')], layout=[Text('a', 'text1')])
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertTrue(parser.warnings_found)
        self.assertTrue('TRIAL_TYPE_DUPLICATE_CONTROLS' in parser.logger.err_codes, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_some_field_names_invalid(self):
        parser, exp = test_parse(trial_types=[TType('a,b', type='t')], layout=[Text('b', 'text2')], return_exp=True)
        self.assertTrue(parser.errors_found)
        self.assertTrue('TRIAL_TYPE_INVALID_CONTROL_NAMES' in parser.logger.err_codes, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        if 't' in exp.trial_types:
            self.assertEqual(1, len(exp.trial_types['t'].steps))
        else:
            self.fail("Trial types: {}".format(",".join(exp.trial_types.keys())))

    def test_all_field_names_invalid(self):
        parser, exp = test_parse(trial_types=[TType('a', type='t')], layout=[Text('b', 'text2')], return_exp=True)
        self.assertTrue(parser.errors_found)
        self.assertTrue('TRIAL_TYPE_INVALID_CONTROL_NAMES' in parser.logger.err_codes, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertEqual(0, len(exp.trial_types), "Trial types: {}".format(",".join(exp.trial_types.keys())))


    #--------------------------------------------------------
    # Responses
    #--------------------------------------------------------

    def test_no_responses(self):
        parser = test_parse(trial_types=[TType('a', type='t')], layout=[Text('a', '')])
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_valid_responses(self):
        parser = test_parse(trial_types=[TType('a', type='t', responses='r1,r2')], layout=[Text('a', '')],
                            responses=[KbResponse('r1', 1, 'a'), KbResponse('r2', 2, 'b')])
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_valid_responses_numeric_id(self):
        parser = test_parse(trial_types=[TType('a', type='t', responses='1,2')], layout=[Text('a', '')],
                            responses=[KbResponse(1, 1, 'a'), KbResponse(2, 2, 'b')])
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_responses_empty(self):
        parser = test_parse(trial_types=[TType('a', type='t', responses='')], layout=[Text('a', '')],
                            responses=[KbResponse('r1', 1, 'a'), KbResponse('r2', 2, 'b')])
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_responses_none(self):
        parser = test_parse(trial_types=[TType('a', type='t', responses=None)], layout=[Text('a', '')],
                            responses=[KbResponse('r1', 1, 'a'), KbResponse('r2', 2, 'b')])
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_duplicate_responses(self):
        parser = test_parse(trial_types=[TType('a', type='t', responses='r1,r2,r1')], layout=[Text('a', '')],
                            responses=[KbResponse('r1', 1, 'a'), KbResponse('r2', 2, 'b')])
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertTrue(parser.warnings_found)
        self.assertTrue('TRIAL_TYPE_DUPLICATE_RESPONSES' in parser.logger.err_codes, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_some_unknown_responses(self):
        parser, exp = test_parse(trial_types=[TType('a', type='t', responses='r3,r2')], layout=[Text('a', '')],
                                 responses=[KbResponse('r1', 1, 'a'), KbResponse('r2', 2, 'b')], return_exp=True)
        self.assertTrue(parser.errors_found)
        self.assertTrue('TRIAL_TYPE_INVALID_RESPONSE_NAMES' in parser.logger.err_codes, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertEqual(1, len(exp.trial_types))
        self.assertEqual(1, len(exp.trial_types['t'].steps))

    def test_all_unknown_responses(self):
        parser, exp = test_parse(trial_types=[TType('a', type='t', responses='r3')], layout=[Text('a', '')], responses=[], return_exp=True)
        self.assertTrue(parser.errors_found)
        self.assertTrue('TRIAL_TYPE_INVALID_RESPONSE_NAMES' in parser.logger.err_codes, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertEqual(1, len(exp.trial_types))
        self.assertEqual(1, len(exp.trial_types['t'].steps))

    def test_multi_type_responses(self):
        parser = test_parse(trial_types=[TType('a', type='t', responses='1,2')], layout=[Text('a', '')],
                            responses=[KbResponse(1, 1, 'z'), BtnResponse(2, 2, '')])
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertTrue(parser.warnings_found)
        self.assertTrue('TRIAL_TYPE_MULTIPLE_RESPONSE_TYPES' in parser.logger.err_codes, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))


    #--------------------------------------------------------
    # Duration
    #--------------------------------------------------------

    def test_no_duration(self):
        parser = test_parse(trial_types=[TType('a', type='t')], layout=[Text('a', '')])
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_valid_duration(self):
        parser, exp = test_parse(trial_types=[TType('a', type='t', duration='1.5')], layout=[Text('a', '')], return_exp=True)
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertEqual(1.5, exp.trial_types['t'].steps[0].duration)

    def test_duration_0_is_invalid(self):
        parser = test_parse(trial_types=[TType('a', type='t', duration='0')], layout=[Text('a', '')])
        self.assertTrue(parser.errors_found)
        self.assertTrue('INVALID_NUMERIC_VALUE' in parser.logger.err_codes, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_negative_duration_is_invalid(self):
        parser = test_parse(trial_types=[TType('a', type='t', duration=-5)], layout=[Text('a', '')])
        self.assertTrue(parser.errors_found)
        self.assertTrue('INVALID_NUMERIC_VALUE' in parser.logger.err_codes, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_string_duration_is_invalid(self):
        parser = test_parse(trial_types=[TType('a', type='t', duration='hi')], layout=[Text('a', '')])
        self.assertTrue(parser.errors_found)
        self.assertTrue('NON_NUMERIC_VALUE' in parser.logger.err_codes, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_empty_duration_is_valid(self):
        parser, exp = test_parse(trial_types=[TType('a', type='t', duration='')], layout=[Text('a', '')], return_exp=True)
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertIsNone(exp.trial_types['t'].steps[0].duration)

    def test_duration_none_is_valid(self):
        parser, exp = test_parse(trial_types=[TType('a', type='t', duration=None)], layout=[Text('a', '')], return_exp=True)
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertIsNone(exp.trial_types['t'].steps[0].duration)

    #--------------------------------------------------------
    # Delay before/after trial
    #--------------------------------------------------------

    def test_valid_delay_before(self):
        parser, exp = test_parse(trial_types=[TType('a', type='t', delay_before='1.5')], layout=[Text('a', '')], return_exp=True)
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertEqual(1.5, exp.trial_types['t'].steps[0].delay_before)

    def test_valid_delay_before_0(self):
        parser, exp = test_parse(trial_types=[TType('a', type='t', delay_before=0)], layout=[Text('a', '')], return_exp=True)
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertEqual(0, exp.trial_types['t'].steps[0].delay_before)

    def test_negative_delay_before_is_invalid(self):
        parser, exp = test_parse(trial_types=[TType('a', type='t', delay_before=-1)], layout=[Text('a', '')], return_exp=True)
        self.assertTrue(parser.errors_found)
        self.assertTrue('INVALID_NUMERIC_VALUE' in parser.logger.err_codes, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_str_delay_before_is_invalid(self):
        parser, exp = test_parse(trial_types=[TType('a', type='t', delay_before='abc')], layout=[Text('a', '')], return_exp=True)
        self.assertTrue(parser.errors_found)
        self.assertTrue('NON_NUMERIC_VALUE' in parser.logger.err_codes, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_empty_delay_before_is_valid(self):
        parser, exp = test_parse(trial_types=[TType('a', type='t', delay_before='')], layout=[Text('a', '')], return_exp=True)
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertEqual(0, exp.trial_types['t'].steps[0].delay_before)

    def test_none_delay_before_is_valid(self):
        parser, exp = test_parse(trial_types=[TType('a', type='t', delay_before=None)], layout=[Text('a', '')], return_exp=True)
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertEqual(0, exp.trial_types['t'].steps[0].delay_before)


    def test_valid_delay_after(self):
        parser, exp = test_parse(trial_types=[TType('a', type='t', delay_after='1.5')], layout=[Text('a', '')], return_exp=True)
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertEqual(1.5, exp.trial_types['t'].steps[0].delay_after)

    def test_valid_delay_after_0(self):
        parser, exp = test_parse(trial_types=[TType('a', type='t', delay_after=0)], layout=[Text('a', '')], return_exp=True)
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertEqual(0, exp.trial_types['t'].steps[0].delay_after)

    def test_negative_delay_after_is_invalid(self):
        parser, exp = test_parse(trial_types=[TType('a', type='t', delay_after=-1)], layout=[Text('a', '')], return_exp=True)
        self.assertTrue(parser.errors_found)
        self.assertTrue('INVALID_NUMERIC_VALUE' in parser.logger.err_codes, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_str_delay_after_is_invalid(self):
        parser, exp = test_parse(trial_types=[TType('a', type='t', delay_after='abc')], layout=[Text('a', '')], return_exp=True)
        self.assertTrue(parser.errors_found)
        self.assertTrue('NON_NUMERIC_VALUE' in parser.logger.err_codes, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_empty_delay_after_is_valid(self):
        parser, exp = test_parse(trial_types=[TType('a', type='t', delay_after='')], layout=[Text('a', '')], return_exp=True)
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertEqual(0, exp.trial_types['t'].steps[0].delay_after)

    def test_none_delay_after_is_valid(self):
        parser, exp = test_parse(trial_types=[TType('a', type='t', delay_after=None)], layout=[Text('a', '')], return_exp=True)
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertEqual(0, exp.trial_types['t'].steps[0].delay_after)


#=============================================================================================
class TrialsTests(unittest.TestCase):

    #------------------------------------------
    # General definitions (no fields yet)
    #------------------------------------------

    def test_no_trials(self):
        parser = test_parse(trial_types=[TType('f1')], layout=[Text('f1', '')], trials=[])
        self.assertTrue(parser.errors_found)
        self.assertTrue('NO_TRIALS' in parser.logger.err_codes, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_trial_type_can_be_omitted_when_there_is_a_single_type(self):
        parser = test_parse(trial_types=[TType('f1')], layout=[Text('f1', '')], trials=[Trial()])
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_trial_type_can_be_specified_when_there_is_a_single_type(self):
        parser = test_parse(trial_types=[TType('f1', type='t1')], layout=[Text('f1', '')], trials=[Trial(type='t1')])
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_trial_col_must_be_specified_when_there_are_multiple_types(self):
        parser = test_parse(trial_types=[TType('f1', type='t1'), TType('f1', type='t2')], layout=[Text('f1', '')], trials=[Trial()])
        self.assertTrue(parser.errors_found)
        self.assertTrue('NO_TYPE_IN_TRIALS_WS' in parser.logger.err_codes, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_trial_type_must_be_specified_when_there_are_multiple_types(self):
        parser = test_parse(trial_types=[TType('f1', type='t1'), TType('f1', type='t2')], layout=[Text('f1', '')], trials=[Trial(type='')])
        self.assertTrue(parser.errors_found)
        self.assertTrue('TRIALS_NO_TRIAL_TYPE' in parser.logger.err_codes, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_unknown_trial_type(self):
        parser = test_parse(trial_types=[TType('f1', type='t1'), TType('f1', type='t2')], layout=[Text('f1', '')], trials=[Trial(type='ttt')])
        self.assertTrue(parser.errors_found)
        self.assertTrue('TRIALS_INVALID_TRIAL_TYPE' in parser.logger.err_codes, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    #------------------------------------------
    # With fields
    #------------------------------------------

    #----------------
    def test_fields_assigned(self):
        parser, exp = test_parse(trial_types=[TType('f1', type='t1')], layout=[Text('f1', '')],
                                 trials=[Trial(type='t1', f1='hello')],
                                 return_exp=True)
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertTrue('f1' in exp.trials[0].control_values, 'Field values: {}'.format(exp.trials[0].control_values))
        self.assertEqual('hello', exp.trials[0].control_values['f1'], 'Field values: {}'.format(exp.trials[0].control_values))

    #----------------
    def test_multiple_fields_assigned(self):
        parser, exp = test_parse(trial_types=[TType('f1,f2', type='t1')], layout=[Text('f1', ''), Text('f2', '')],
                                 trials=[Trial(type='t1', f1='hello', f2='there')],
                                 return_exp=True)
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertEqual('hello', exp.trials[0].control_values['f1'], 'Field values: {}'.format(exp.trials[0].control_values))
        self.assertEqual('there', exp.trials[0].control_values['f2'], 'Field values: {}'.format(exp.trials[0].control_values))

    #----------------
    def test_excessive_fields_ignored(self):
        parser, exp = test_parse(trial_types=[TType('f1', type='t1')], layout=[Text('f1', ''), Text('f2', '')],
                                 trials=[Trial(type='t1', f1='hello', f2='kuku')],
                                 return_exp=True)
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    #----------------
    def test_unknown_fields_are_invalid(self):
        parser, exp = test_parse(trial_types=[TType('f1', type='t1')], layout=[Text('f1', ''), Text('f2', '')],
                                 trials=[Trial(type='t1', f1='hello', f3='kuku')],
                                 return_exp=True)
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertTrue(parser.warnings_found)
        self.assertTrue('TRIALS_UNKNOWN_FIELDS' in parser.logger.err_codes, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))


#todo instructions - with trial flow potentially

if __name__ == '__main__':
    unittest.main()
