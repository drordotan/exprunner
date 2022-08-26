
import unittest

from testutils import *


NO_VALUE = "__NO_VALUE__"


#-----------------------------------------------------------------------------
def test_parse(general=None, layout=None, trial_types=None, responses=None, trials=None, instructions=None, return_exp=False,
               parsing_config=None):

    if parsing_config is None:
        parsing_config = dict(instructions_mandatory=False)

    reader = ReaderForTests(general=general, layout=layout, trial_types=trial_types, respones=responses, trials=trials, instructions=instructions)

    parser = ParserForTests(reader,
                            parse_layout=layout is not None,
                            parse_trial_types=trial_types is not None,
                            parse_trials=trials is not None)

    exp = parser.parse(parsing_config)

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
    kwargs['layout_name'] = ctl_name
    kwargs['type'] = 'text'
    kwargs['text'] = text
    return kwargs


#-----------------------------------------------------------------------------
# noinspection PyPep8Naming
def Instruction(text, responses, **kwargs):
    kwargs['text'] = text
    kwargs['responses'] = responses
    return kwargs


#-----------------------------------------------------------------------------
# noinspection PyPep8Naming
def KbResponse(name, value, key, **kwargs):
    kwargs['response_name'] = name
    kwargs['type'] = 'key'
    kwargs['value'] = value
    kwargs['key'] = key
    return kwargs


#-----------------------------------------------------------------------------
# noinspection PyPep8Naming
def BtnResponse(name, value, text, **kwargs):
    kwargs['response_name'] = name
    kwargs['type'] = 'button'
    kwargs['value'] = value
    kwargs['text'] = text
    return kwargs


#-----------------------------------------------------------------------------
# noinspection PyPep8Naming
def TType(fields, duration=1, **kwargs):
    kwargs['layout items'] = fields

    if duration is not None:
        kwargs['duration'] = duration

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

    def test_subj_id_y(self):
        parser = test_parse(general=[G('get_subj_id', 'Y')])
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_subj_id_n(self):
        parser = test_parse(general=[G('get_subj_id', 'Y')])
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_subj_id_none(self):
        parser = test_parse(general=[G('get_subj_id', None)])
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_subj_id_empty(self):
        parser = test_parse(general=[G('get_subj_id', '')])
        self.assertTrue(parser.errors_found)
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_subj_id_invalid(self):
        parser = test_parse(general=[G('get_subj_id', 'xyz')])
        self.assertTrue(parser.errors_found)
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))


    #--------------------------------------------------------
    # Specify session ID
    #--------------------------------------------------------

    def test_session_id_y(self):
        parser = test_parse(general=[G('get_session_id', 'Y')])
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_session_id_n(self):
        parser = test_parse(general=[G('get_session_id', 'Y')])
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_session_id_none(self):
        parser = test_parse(general=[G('get_session_id', None)])
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_session_id_empty(self):
        parser = test_parse(general=[G('get_session_id', '')])
        self.assertTrue(parser.errors_found)

    def test_session_id_invalid(self):
        parser = test_parse(general=[G('get_session_id', 'xyz')])
        self.assertTrue(parser.errors_found)


    #--------------------------------------------------------
    # Specify results filename
    #--------------------------------------------------------

    def test_specify_results_filename_default(self):
        parser, exp = test_parse(general=[], return_exp=True)
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertEqual('results_${date}.csv', exp.results_filename)

    def test_specify_results_filename_without_details(self):
        parser, exp = test_parse(general=[G('results_filename_prefix', 'stam')], return_exp=True)
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertEqual('stam_${date}.csv', exp.results_filename)

    def test_specify_results_filename_with_subj(self):
        parser, exp = test_parse(general=[G('results_filename_prefix', 'stam'), G('get_subj_id', 'Y')], return_exp=True)
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertEqual('stam_${subj_id}_${date}.csv', exp.results_filename)

    def test_specify_results_filename_with_session(self):
        parser, exp = test_parse(general=[G('results_filename_prefix', 'stam'), G('get_session_id', 'Y')], return_exp=True)
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertEqual('stam_${session_id}_${date}.csv', exp.results_filename)

    def test_specify_results_filename_invalid_prefix(self):
        parser, exp = test_parse(general=[G('results_filename_prefix', '%')], return_exp=True)
        self.assertTrue(parser.errors_found)
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertTrue('INVALID_FILENAME_PREFIX' in parser.logger.err_codes, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))


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

    def test_specify_top_as_pcnt(self):
        parser, exp = test_parse(layout=[Text('field1', top='50%')], return_exp=True)
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertEqual('50%', list(exp.layout.values())[0].frame.top)

    def test_specify_left_as_pcnt(self):
        parser, exp = test_parse(layout=[Text('field1', left='-50%')], return_exp=True)
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertEqual('-50%', list(exp.layout.values())[0].frame.left)

    def test_specify_top_as_px(self):
        parser, exp = test_parse(layout=[Text('field1', top='-50px')], return_exp=True)
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertEqual('-50px', list(exp.layout.values())[0].frame.top)

    def test_specify_left_as_px(self):
        parser, exp = test_parse(layout=[Text('field1', left='5000px')], return_exp=True)
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertEqual('5000px', list(exp.layout.values())[0].frame.left)

    def test_specify_width_as_px(self):
        parser, exp = test_parse(layout=[Text('field1', width='30px')], return_exp=True)
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertEqual('30px', list(exp.layout.values())[0].frame.width)

    def test_specify_top_in_invalid_format(self):
        parser = test_parse(layout=[Text('field1', top='5000')])
        self.assertTrue(parser.errors_found)
        self.assertTrue('INVALID_COORD' in parser.logger.err_codes, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_specify_left_in_invalid_format(self):
        parser = test_parse(layout=[Text('field1', left='--500')])
        self.assertTrue(parser.errors_found)
        self.assertTrue('INVALID_COORD' in parser.logger.err_codes, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_warning_when_position_is_relative_and_top_specified_as_percent(self):
        parser = test_parse(layout=[Text('field1', top='50%', position='relative')])
        self.assertTrue(parser.warnings_found)
        self.assertTrue('POSITION_MISMATCHES_TOP_OR_LEFT' in parser.logger.err_codes, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_warning_when_position_is_relative_and_left_specified_as_percent(self):
        parser = test_parse(layout=[Text('field1', left='50%', position='relative')])
        self.assertTrue(parser.warnings_found)
        self.assertTrue('POSITION_MISMATCHES_TOP_OR_LEFT' in parser.logger.err_codes, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))


    #--------------------------------------------------------
    # Errors
    #--------------------------------------------------------

    def test_invalid_control_type(self):
        parser = test_parse(layout=[dict(layout_name='fld', type='magic')])
        self.assertTrue(parser.errors_found)
        self.assertTrue('INVALID_CONTROL_TYPE' in parser.logger.err_codes, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_invalid_control_name(self):
        parser = test_parse(layout=[Text('%')])
        self.assertTrue(parser.errors_found)
        self.assertTrue('INVALID_CONTROL_NAME' in parser.logger.err_codes, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_duplicate_field_names_are_invalid(self):
        parser = test_parse(layout=[Text('field1'), Text('field2'), Text('field1')])
        self.assertTrue(parser.errors_found)
        self.assertTrue('DUPLICATE_CONTROL_NAME' in parser.logger.err_codes, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_duplicate_field_names_are_invalid_case_insensitive(self):
        parser = test_parse(layout=[Text('field1'), Text('field2'), Text('FIEld1')])
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
        parser = test_parse(responses=[dict(response_name='r1', type='badtype', value=1)])
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
        parser = test_parse(responses=[dict(response_name='r1', type='key', value=1)])
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

    def test_kbresp_duplicate_response_ids_are_invalid_case_insensitive(self):
        parser = test_parse(responses=[KbResponse('r1', 1, '/'), KbResponse('R1', 2, '.')])
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
        parser = test_parse(responses=[dict(response_name='r1', type='button', value=1)])
        self.assertTrue(parser.errors_found)
        self.assertTrue('MISSING_BUTTON_RESPONSE_TEXT_COL' in parser.logger.err_codes, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))


# =============================================================================================
class InstructionsTests(unittest.TestCase):

    default_resp = [KbResponse('kb1', 1, '/'), KbResponse('kb2', 2, 'p')]

    def test_no_instructions_valid(self):
        parser, exp = test_parse(return_exp=True)
        self.assertFalse(parser.errors_found, 'error codes: '+','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: '+','.join(parser.logger.err_codes.keys()))
        self.assertEqual([], exp.instructions)

    def test_no_instructions_invalid(self):
        parser, exp = test_parse(return_exp=True, parsing_config=dict(instructions_mandatory=True))
        self.assertFalse(parser.errors_found, 'error codes: '+','.join(parser.logger.err_codes.keys()))
        self.assertTrue(parser.warnings_found)
        self.assertTrue('NO_INSTRUCTIONS' in parser.logger.err_codes, 'error codes: '+','.join(parser.logger.err_codes.keys()))
        self.assertEqual([], exp.instructions)

    def test_1_instructions_page(self):
        parser, exp = test_parse(return_exp=True, instructions=[Instruction('hi', 'kb1')], responses=InstructionsTests.default_resp)
        self.assertFalse(parser.errors_found, 'error codes: '+','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: '+','.join(parser.logger.err_codes.keys()))
        self.assertEqual(1, len(exp.instructions))
        i = exp.instructions[0]
        self.assertEqual('hi', i.text)
        self.assertEqual(['kb1'], i.response_names)

    def test_instructions_with_multiple_responses(self):
        parser, exp = test_parse(return_exp=True, instructions=[Instruction('hi', 'kb1,kb2')], responses=InstructionsTests.default_resp)
        self.assertFalse(parser.errors_found, 'error codes: '+','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: '+','.join(parser.logger.err_codes.keys()))
        self.assertEqual(1, len(exp.instructions))
        i = exp.instructions[0]
        self.assertEqual('hi', i.text)
        self.assertEqual(['kb1', 'kb2'], i.response_names)

    def test_2_instructions_pages(self):
        parser, exp = test_parse(return_exp=True, instructions=[Instruction('hi', 'kb1'), Instruction('hi2', 'kb2')],
                                 responses=InstructionsTests.default_resp)
        self.assertFalse(parser.errors_found, 'error codes: '+','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: '+','.join(parser.logger.err_codes.keys()))
        self.assertEqual(2, len(exp.instructions))
        i1 = exp.instructions[0]
        i2 = exp.instructions[1]
        self.assertEqual('hi', i1.text)
        self.assertEqual(['kb1'], i1.response_names)
        self.assertEqual('hi2', i2.text)
        self.assertEqual(['kb2'], i2.response_names)

    #---- Invalid definitions: problem with definition of instructions text

    def test_no_text_column(self):
        parser, exp = test_parse(return_exp=True, instructions=[dict(responses='kb1')], responses=InstructionsTests.default_resp)
        self.assertTrue(parser.errors_found)
        self.assertFalse(parser.warnings_found, 'error codes: '+','.join(parser.logger.err_codes.keys()))
        self.assertTrue('INSTRUCTIONS_MISSING_TEXT_COL' in parser.logger.err_codes, 'error codes: '+','.join(parser.logger.err_codes.keys()))

    def test_empty_text(self):
        parser, exp = test_parse(return_exp=True, instructions=[Instruction('', 'kb1')], responses=InstructionsTests.default_resp)
        self.assertTrue(parser.errors_found)
        self.assertFalse(parser.warnings_found, 'error codes: '+','.join(parser.logger.err_codes.keys()))
        self.assertTrue('INSTRUCTION_TEXT_MISSING' in parser.logger.err_codes, 'error codes: '+','.join(parser.logger.err_codes.keys()))

    #---- Invalid definitions: problem with definition of responses

    def test_no_responses_column(self):
        parser, exp = test_parse(return_exp=True, instructions=[dict(text='xxx')], responses=InstructionsTests.default_resp)
        self.assertTrue(parser.errors_found)
        self.assertFalse(parser.warnings_found, 'error codes: '+','.join(parser.logger.err_codes.keys()))
        self.assertTrue('INSTRUCTIONS_MISSING_RESPONSE_COL' in parser.logger.err_codes, 'error codes: '+','.join(parser.logger.err_codes.keys()))

    def test_responses_none(self):
        parser, exp = test_parse(return_exp=True, instructions=[Instruction('hi', None)], responses=InstructionsTests.default_resp)
        self.assertTrue(parser.errors_found)
        self.assertFalse(parser.warnings_found, 'error codes: '+','.join(parser.logger.err_codes.keys()))
        self.assertTrue('INSTRUCTIONS_MUST_DEFINE_RESPONSE' in parser.logger.err_codes, 'error codes: '+','.join(parser.logger.err_codes.keys()))

    def test_responses_empty(self):
        parser, exp = test_parse(return_exp=True, instructions=[Instruction('hi', '')], responses=InstructionsTests.default_resp)
        self.assertTrue(parser.errors_found)
        self.assertFalse(parser.warnings_found, 'error codes: '+','.join(parser.logger.err_codes.keys()))
        self.assertTrue('INSTRUCTIONS_MUST_DEFINE_RESPONSE' in parser.logger.err_codes, 'error codes: '+','.join(parser.logger.err_codes.keys()))

    def test_response_unknown(self):
        parser, exp = test_parse(return_exp=True, instructions=[Instruction('hi', 'x')], responses=InstructionsTests.default_resp)
        self.assertTrue(parser.errors_found)
        self.assertFalse(parser.warnings_found, 'error codes: '+','.join(parser.logger.err_codes.keys()))
        self.assertTrue('INSTRUCTION_INVALID_RESPONSE_NAMES' in parser.logger.err_codes, 'error codes: '+','.join(parser.logger.err_codes.keys()))

    def test_response_duplicate(self):
        parser, exp = test_parse(return_exp=True, instructions=[Instruction('hi', 'kb1,kb1')], responses=InstructionsTests.default_resp)
        self.assertFalse(parser.errors_found, 'error codes: '+','.join(parser.logger.err_codes.keys()))
        self.assertTrue(parser.warnings_found)
        self.assertTrue('INSTRUCTION_DUPLICATE_RESPONSES' in parser.logger.err_codes, 'error codes: '+','.join(parser.logger.err_codes.keys()))

    def test_responses_with_multiple_types(self):
        parser, exp = test_parse(return_exp=True, instructions=[Instruction('hi', 'kb1,btn1')],
                                 responses=[KbResponse('kb1', 1, '/'), BtnResponse('btn1', 2, 'p')])
        self.assertTrue(parser.errors_found)
        self.assertFalse(parser.warnings_found, 'error codes: '+','.join(parser.logger.err_codes.keys()))
        self.assertTrue('INSTRUCTIONS_WITH_MULTIPLE_RESPONSE_TYPES' in parser.logger.err_codes, 'error codes: '+','.join(parser.logger.err_codes.keys()))


#=============================================================================================
class TrialTypesTests(unittest.TestCase):

    def test_no_types(self):
        parser = test_parse(trial_types=[])
        self.assertTrue(parser.errors_found)

    #--------------------------------------------------------
    # Type name
    #--------------------------------------------------------

    def test_type_name_cannot_be_TYPE(self):
        parser = test_parse(trial_types=[TType('f1,f2', type_name='type')])
        self.assertTrue(parser.errors_found)
        self.assertTrue('TRIAL_TYPE_INVALID_TYPE_NAME' in parser.logger.err_codes, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_type_name_contains_invalid_characters(self):
        parser = test_parse(trial_types=[TType('f1,f2', type_name='some!thing')])
        self.assertTrue(parser.errors_found)
        self.assertTrue('TRIAL_TYPE_INVALID_TYPE_NAME' in parser.logger.err_codes, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_type_name_valid(self):
        parser = test_parse(trial_types=[TType('ctl1', type_name='soMe_509')], layout=[Text('ctl1', 'text1')])
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))


    #--------------------------------------------------------
    # Fields
    #--------------------------------------------------------

    def test_valid_fields(self):
        parser, exp = test_parse(trial_types=[TType('a, b', type_name='t')], layout=[Text('a', 'text1'), Text('b', 'text2')], return_exp=True)
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        fields = exp.trial_types['t'].control_names
        self.assertTrue('a' in fields, 'Field names: ' + ",".join(fields))
        self.assertTrue('b' in fields, 'Field names: ' + ",".join(fields))

    def test_valid_fields_with_numeric_name(self):
        parser = test_parse(trial_types=[TType('1, 2', type_name='t')], layout=[Text(1, 'text1'), Text(2, 'text2')])
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_fields_empty(self):
        parser = test_parse(trial_types=[TType('', type_name='t')])
        self.assertTrue(parser.errors_found)
        self.assertTrue('TRIAL_TYPE_NO_FIELDS' in parser.logger.err_codes, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_fields_none(self):
        parser = test_parse(trial_types=[TType(None, type_name='t')])
        self.assertTrue(parser.errors_found)
        self.assertTrue('TRIAL_TYPE_NO_FIELDS' in parser.logger.err_codes, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_duplicate_field_names(self):
        parser = test_parse(trial_types=[TType('a,a', type_name='t')], layout=[Text('a', 'text1')])
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertTrue(parser.warnings_found)
        self.assertTrue('TRIAL_TYPE_DUPLICATE_CONTROLS' in parser.logger.err_codes, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_some_field_names_invalid(self):
        parser, exp = test_parse(trial_types=[TType('a,b', type_name='t')], layout=[Text('b', 'text2')], return_exp=True)
        self.assertTrue(parser.errors_found)
        self.assertTrue('TRIAL_TYPE_INVALID_CONTROL_NAMES' in parser.logger.err_codes, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        if 't' in exp.trial_types:
            self.assertEqual(1, len(exp.trial_types['t'].steps))
        else:
            self.fail("Trial types: {}".format(",".join(exp.trial_types.keys())))

    def test_all_field_names_invalid(self):
        parser, exp = test_parse(trial_types=[TType('a', type_name='t')], layout=[Text('b', 'text2')], return_exp=True)
        self.assertTrue(parser.errors_found)
        self.assertTrue('TRIAL_TYPE_INVALID_CONTROL_NAMES' in parser.logger.err_codes, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertEqual(0, len(exp.trial_types), "Trial types: {}".format(",".join(exp.trial_types.keys())))

    #todo test duplicate trial type names

    #--------------------------------------------------------
    # Responses
    #--------------------------------------------------------

    def test_no_responses(self):
        parser = test_parse(trial_types=[TType('a', type_name='t')], layout=[Text('a', '')])
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_valid_responses(self):
        parser = test_parse(trial_types=[TType('a', type_name='t', responses='r1,r2')], layout=[Text('a', '')],
                            responses=[KbResponse('r1', 1, 'a'), KbResponse('r2', 2, 'b')])
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_valid_responses_numeric_id(self):
        parser = test_parse(trial_types=[TType('a', type_name='t', responses='1,2')], layout=[Text('a', '')],
                            responses=[KbResponse(1, 1, 'a'), KbResponse(2, 2, 'b')])
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_responses_empty(self):
        parser = test_parse(trial_types=[TType('a', type_name='t', responses='')], layout=[Text('a', '')],
                            responses=[KbResponse('r1', 1, 'a'), KbResponse('r2', 2, 'b')])
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_responses_none(self):
        parser = test_parse(trial_types=[TType('a', type_name='t', responses=None)], layout=[Text('a', '')],
                            responses=[KbResponse('r1', 1, 'a'), KbResponse('r2', 2, 'b')])
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_duplicate_responses(self):
        parser = test_parse(trial_types=[TType('a', type_name='t', responses='r1,r2,r1')], layout=[Text('a', '')],
                            responses=[KbResponse('r1', 1, 'a'), KbResponse('r2', 2, 'b')])
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertTrue(parser.warnings_found)
        self.assertTrue('TRIAL_TYPE_DUPLICATE_RESPONSES' in parser.logger.err_codes, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_some_unknown_responses(self):
        parser, exp = test_parse(trial_types=[TType('a', type_name='t', responses='r3,r2')], layout=[Text('a', '')],
                                 responses=[KbResponse('r1', 1, 'a'), KbResponse('r2', 2, 'b')], return_exp=True)
        self.assertTrue(parser.errors_found)
        self.assertTrue('TRIAL_TYPE_INVALID_RESPONSE_NAMES' in parser.logger.err_codes, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertEqual(1, len(exp.trial_types))
        self.assertEqual(1, len(exp.trial_types['t'].steps))

    def test_all_unknown_responses(self):
        parser, exp = test_parse(trial_types=[TType('a', type_name='t', responses='r3')], layout=[Text('a', '')], responses=[], return_exp=True)
        self.assertTrue(parser.errors_found)
        self.assertTrue('TRIAL_TYPE_INVALID_RESPONSE_NAMES' in parser.logger.err_codes, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertEqual(1, len(exp.trial_types))
        self.assertEqual(1, len(exp.trial_types['t'].steps))

    def test_multi_type_responses(self):
        parser = test_parse(trial_types=[TType('a', type_name='t', responses='1,2')], layout=[Text('a', '')],
                            responses=[KbResponse(1, 1, 'z'), BtnResponse(2, 2, '')])
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertTrue(parser.warnings_found)
        self.assertTrue('TRIAL_TYPE_MULTIPLE_RESPONSE_TYPES' in parser.logger.err_codes, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))


    #--------------------------------------------------------
    # Duration
    #--------------------------------------------------------

    def test_no_duration(self):
        parser = test_parse(trial_types=[TType('a', duration=None, type_name='t', responses='1')], layout=[Text('a', '')], responses=[KbResponse(1, 1, 'z')])
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_valid_duration(self):
        parser, exp = test_parse(trial_types=[TType('a', type_name='t', duration='1500')], layout=[Text('a', '')], return_exp=True)
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertEqual(1500, exp.trial_types['t'].steps[0].duration)

    def test_duration_0_is_invalid(self):
        parser = test_parse(trial_types=[TType('a', type_name='t', duration='0')], layout=[Text('a', '')])
        self.assertTrue(parser.errors_found)
        self.assertTrue('INVALID_NUMERIC_VALUE' in parser.logger.err_codes, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_negative_duration_is_invalid(self):
        parser = test_parse(trial_types=[TType('a', type_name='t', duration=-5)], layout=[Text('a', '')])
        self.assertTrue(parser.errors_found)
        self.assertTrue('INVALID_NUMERIC_VALUE' in parser.logger.err_codes, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_string_duration_is_invalid(self):
        parser = test_parse(trial_types=[TType('a', type_name='t', duration='hi')], layout=[Text('a', '')])
        self.assertTrue(parser.errors_found)
        self.assertTrue('NON_NUMERIC_VALUE' in parser.logger.err_codes, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_empty_duration_is_valid(self):
        parser, exp = test_parse(trial_types=[TType('a', type_name='t', duration='', responses='1')],
                                 layout=[Text('a', '')],
                                 responses=[KbResponse(1, 1, 'z')],
                                 return_exp=True)
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertIsNone(exp.trial_types['t'].steps[0].duration)

    def test_duration_none_is_valid(self):
        parser, exp = test_parse(trial_types=[TType('a', type_name='t', duration=None, responses='1')],
                                 layout=[Text('a', '')],
                                 responses=[KbResponse(1, 1, 'z')],
                                 return_exp=True)
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertIsNone(exp.trial_types['t'].steps[0].duration)

    def test_must_define_either_duration_or_response(self):
        parser = test_parse(trial_types=[TType('a', duration=None, type_name='t')], layout=[Text('a', '')])
        self.assertTrue(parser.errors_found)
        self.assertTrue('MUST_DEFINE_RESPONSE_OR_DURATION' in parser.logger.err_codes, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))


    #--------------------------------------------------------
    # Delay before/after trial
    #--------------------------------------------------------

    def test_valid_delay_before(self):
        parser, exp = test_parse(trial_types=[TType('a', type_name='t', delay_before='1500')], layout=[Text('a', '')], return_exp=True)
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertEqual(1500, exp.trial_types['t'].steps[0].delay_before)

    def test_valid_delay_before_0(self):
        parser, exp = test_parse(trial_types=[TType('a', type_name='t', delay_before=0)], layout=[Text('a', '')], return_exp=True)
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertEqual(0, exp.trial_types['t'].steps[0].delay_before)

    def test_negative_delay_before_is_invalid(self):
        parser, exp = test_parse(trial_types=[TType('a', type_name='t', delay_before=-1)], layout=[Text('a', '')], return_exp=True)
        self.assertTrue(parser.errors_found)
        self.assertTrue('INVALID_NUMERIC_VALUE' in parser.logger.err_codes, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_str_delay_before_is_invalid(self):
        parser, exp = test_parse(trial_types=[TType('a', type_name='t', delay_before='abc')], layout=[Text('a', '')], return_exp=True)
        self.assertTrue(parser.errors_found)
        self.assertTrue('NON_NUMERIC_VALUE' in parser.logger.err_codes, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_empty_delay_before_is_valid(self):
        parser, exp = test_parse(trial_types=[TType('a', type_name='t', delay_before='')], layout=[Text('a', '')], return_exp=True)
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertEqual(0, exp.trial_types['t'].steps[0].delay_before)

    def test_none_delay_before_is_valid(self):
        parser, exp = test_parse(trial_types=[TType('a', type_name='t', delay_before=None)], layout=[Text('a', '')], return_exp=True)
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertEqual(0, exp.trial_types['t'].steps[0].delay_before)


    def test_valid_delay_after(self):
        parser, exp = test_parse(trial_types=[TType('a', type_name='t', delay_after='1500')], layout=[Text('a', '')], return_exp=True)
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertEqual(1500, exp.trial_types['t'].steps[0].delay_after)

    def test_valid_delay_after_0(self):
        parser, exp = test_parse(trial_types=[TType('a', type_name='t', delay_after=0)], layout=[Text('a', '')], return_exp=True)
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertEqual(0, exp.trial_types['t'].steps[0].delay_after)

    def test_negative_delay_after_is_invalid(self):
        parser, exp = test_parse(trial_types=[TType('a', type_name='t', delay_after=-1)], layout=[Text('a', '')], return_exp=True)
        self.assertTrue(parser.errors_found)
        self.assertTrue('INVALID_NUMERIC_VALUE' in parser.logger.err_codes, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_str_delay_after_is_invalid(self):
        parser, exp = test_parse(trial_types=[TType('a', type_name='t', delay_after='abc')], layout=[Text('a', '')], return_exp=True)
        self.assertTrue(parser.errors_found)
        self.assertTrue('NON_NUMERIC_VALUE' in parser.logger.err_codes, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_empty_delay_after_is_valid(self):
        parser, exp = test_parse(trial_types=[TType('a', type_name='t', delay_after='')], layout=[Text('a', '')], return_exp=True)
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertEqual(0, exp.trial_types['t'].steps[0].delay_after)

    def test_none_delay_after_is_valid(self):
        parser, exp = test_parse(trial_types=[TType('a', type_name='t', delay_after=None)], layout=[Text('a', '')], return_exp=True)
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
        parser = test_parse(trial_types=[TType('f1', type_name='t1')], layout=[Text('f1', '')], trials=[Trial(type='t1')])
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_trial_col_must_be_specified_when_there_are_multiple_types(self):
        parser = test_parse(trial_types=[TType('f1', type_name='t1'), TType('f1', type_name='t2')], layout=[Text('f1', '')], trials=[Trial()])
        self.assertTrue(parser.errors_found)
        self.assertTrue('NO_TYPE_IN_TRIALS_WS' in parser.logger.err_codes, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_trial_type_must_be_specified_when_there_are_multiple_types(self):
        parser = test_parse(trial_types=[TType('f1', type_name='t1'), TType('f1', type_name='t2')], layout=[Text('f1', '')], trials=[Trial(type='')])
        self.assertTrue(parser.errors_found)
        self.assertTrue('TRIALS_NO_TRIAL_TYPE' in parser.logger.err_codes, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_unknown_trial_type(self):
        parser = test_parse(trial_types=[TType('f1', type_name='t1'), TType('f1', type_name='t2')], layout=[Text('f1', '')], trials=[Trial(type='ttt')])
        self.assertTrue(parser.errors_found)
        self.assertTrue('TRIALS_INVALID_TRIAL_TYPE' in parser.logger.err_codes, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    #------------------------------------------
    # With fields
    #------------------------------------------

    #----------------
    def test_fields_assigned(self):
        parser, exp = test_parse(trial_types=[TType('f1', type_name='t1')], layout=[Text('f1', '')],
                                 trials=[Trial(type='t1', f1='hello')],
                                 return_exp=True)
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertTrue('f1' in exp.trials[0].control_values, 'Field values: {}'.format(exp.trials[0].control_values))
        self.assertEqual('hello', exp.trials[0].control_values['f1'], 'Field values: {}'.format(exp.trials[0].control_values))

    #----------------
    def test_multiple_fields_assigned(self):
        parser, exp = test_parse(trial_types=[TType('f1,f2', type_name='t1')], layout=[Text('f1', ''), Text('f2', '')],
                                 trials=[Trial(type='t1', f1='hello', f2='there')],
                                 return_exp=True)
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertEqual('hello', exp.trials[0].control_values['f1'], 'Field values: {}'.format(exp.trials[0].control_values))
        self.assertEqual('there', exp.trials[0].control_values['f2'], 'Field values: {}'.format(exp.trials[0].control_values))

    #----------------
    def test_excessive_fields_ignored(self):
        parser, exp = test_parse(trial_types=[TType('f1', type_name='t1')], layout=[Text('f1', ''), Text('f2', '')],
                                 trials=[Trial(type='t1', f1='hello', f2='kuku')],
                                 return_exp=True)
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    #----------------
    def test_unknown_fields_are_invalid(self):
        parser, exp = test_parse(trial_types=[TType('f1', type_name='t1')], layout=[Text('f1', ''), Text('f2', '')],
                                 trials=[Trial(type='t1', f1='hello', f3='kuku')],
                                 return_exp=True)
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertTrue(parser.warnings_found)
        self.assertTrue('TRIALS_INVALID_COL_NAME' in parser.logger.err_codes, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    #------------------------------------------
    # Custom "save:" columns
    #------------------------------------------

    def test_save_values(self):
        parser, exp = test_parse(trial_types=[TType('f1')], layout=[Text('f1', '')],
                                 trials=[{'save:a': 'value1'}],
                                 return_exp=True)
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertTrue('a' in exp.trials[0].save_values)
        self.assertEqual('value1', exp.trials[0].save_values['a'])

    def test_no_saved_col_name(self):
        parser, exp = test_parse(trial_types=[TType('f1')], layout=[Text('f1', '')],
                                 trials=[{'save: ': 'value1'}],
                                 return_exp=True)
        self.assertTrue(parser.errors_found)
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertTrue('TRIALS_INVALID_SAVE_COL' in parser.logger.err_codes, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    #------------------------------------------
    # CSS formatting
    #------------------------------------------

    def test_valid_css_formatting(self):
        parser, exp = test_parse(trial_types=[TType('f1')], layout=[Text('f1', '')],
                                 trials=[{'format:f1.font-size': '3px'}],
                                 return_exp=True)
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertTrue('f1' in exp.trials[0].css)
        self.assertTrue('font-size' in exp.trials[0].css['f1'])
        self.assertEqual('3px', exp.trials[0].css['f1']['font-size'])

    def test_css_formatting_for_non_existing_control_is_invalid(self):
        parser, exp = test_parse(trial_types=[TType('f1')], layout=[Text('f1', '')],
                                 trials=[{'format:f2.font-size': '3'}],
                                 return_exp=True)
        self.assertTrue(parser.errors_found)
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertTrue('TRIALS_UNKNOWN_CONTROL' in parser.logger.err_codes, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_css_formatting_for_unused_control_is_invalid(self):
        parser, exp = test_parse(trial_types=[TType('f1')], layout=[Text('f1', ''), Text('f2', '')],
                                 trials=[{'format:f2.font-size': '3'}],
                                 return_exp=True)
        self.assertTrue(parser.errors_found)
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertTrue('TRIALS_CSS_TRIALTYPE_MISMATCH' in parser.logger.err_codes, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))

    def test_css_empty_formatting_for_unused_control_is_valid(self):
        parser, exp = test_parse(trial_types=[TType('f1')], layout=[Text('f1', ''), Text('f2', '')],
                                 trials=[{'format:f2.font-size': ''}],
                                 return_exp=True)
        self.assertFalse(parser.errors_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertFalse(parser.warnings_found, 'error codes: ' + ','.join(parser.logger.err_codes.keys()))
        self.assertEqual(0, len(exp.trials[0].css))


#todo instructions - with trial flow potentially

if __name__ == '__main__':
    unittest.main()
