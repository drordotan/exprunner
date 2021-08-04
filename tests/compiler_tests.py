
import unittest

from testutils import *


#-----------------------------------------------------------------------------
def test_compile(general=None, layout=None, trial_types=None, responses=None, trials=None):
    parser = ParserForTests(general=general, layout=layout, trial_types=trial_types, respones=responses, trials=trials)
    compiler = CompilerForTests(parser)
    rc = compiler.compile()
    return rc, compiler


#-----------------------------------------------------------------------------
def G(param_name, param_value):
    return dict(param=param_name, value=param_value)

#-----------------------------------------------------------------------------
def Text(field_name, text='', **kwargs):
    kwargs['field_name'] = field_name
    kwargs['type'] = 'text'
    kwargs['text'] = text
    return kwargs

#-----------------------------------------------------------------------------
def KbResponse(id, value, key, **kwargs):
    kwargs['id'] = id
    kwargs['type'] = 'key'
    kwargs['value'] = value
    kwargs['key'] = key
    return kwargs

#-----------------------------------------------------------------------------
def BtnResponse(id, value, text, **kwargs):
    kwargs['id'] = id
    kwargs['type'] = 'button'
    kwargs['value'] = value
    kwargs['text'] = text
    return kwargs



#=============================================================================================
class GeneralWsTests(unittest.TestCase):

    #--------------------------------------------------------
    # Specify subj ID
    #--------------------------------------------------------

    def test_specify_results_filename_subj_id_y(self):
        rc, compiler = test_compile(general=[ G('get_subj_id', 'Y')])
        self.assertEqual(0, rc)

    def test_specify_results_filename_subj_id_n(self):
        rc, compiler = test_compile(general=[ G('get_subj_id', 'Y')])
        self.assertEqual(0, rc)

    def test_specify_results_filename_subj_id_none(self):
        rc, compiler = test_compile(general=[ G('get_subj_id', None)])
        self.assertEqual(0, rc)

    def test_specify_results_filename_subj_id_empty(self):
        rc, compiler = test_compile(general=[ G('get_subj_id', '')])
        self.assertEqual(2, rc)

    def test_specify_results_filename_subj_id_invalid(self):
        rc, compiler = test_compile(general=[ G('get_subj_id', 'xyz')])
        self.assertEqual(2, rc)


    #--------------------------------------------------------
    # Specify session ID
    #--------------------------------------------------------

    def test_specify_results_filename_session_id_y(self):
        rc, compiler = test_compile(general=[ G('get_session_id', 'Y')])
        self.assertEqual(0, rc)

    def test_specify_results_filename_session_id_n(self):
        rc, compiler = test_compile(general=[ G('get_session_id', 'Y')])
        self.assertEqual(0, rc)

    def test_specify_results_filename_session_id_none(self):
        rc, compiler = test_compile(general=[ G('get_session_id', None)])
        self.assertEqual(0, rc)

    def test_specify_results_filename_session_id_empty(self):
        rc, compiler = test_compile(general=[ G('get_session_id', '')])
        self.assertEqual(2, rc)

    def test_specify_results_filename_session_id_invalid(self):
        rc, compiler = test_compile(general=[ G('get_session_id', 'xyz')])
        self.assertEqual(2, rc)


    #--------------------------------------------------------
    # Specify results filename
    #--------------------------------------------------------

    def test_specify_results_filename_without_keywords(self):
        rc, compiler = test_compile(general=[G('results_filename', 'stam.pdf')])
        self.assertEqual(0, rc)

    def test_specify_results_filename_with_date(self):
        rc, compiler = test_compile(general=[G('results_filename', 'a${date}.pdf')])
        self.assertEqual(0, rc)

    def test_specify_results_filename_with_valid_subj_id(self):
        rc, compiler = test_compile(general=[G('results_filename', 'a${subj_id}.pdf'), G('get_subj_id', 'Y')])
        self.assertEqual(0, rc)

    def test_specify_results_filename_with_invalid_subj_id(self):
        rc, compiler = test_compile(general=[G('results_filename', 'a${subj_id}.pdf')])
        self.assertEqual(2, rc)
        self.assertTrue('INVALID_FILENAME(SUBJ_ID)' in compiler.logger.err_codes, 'error codes: ' + ','.join(compiler.logger.err_codes.keys()))

    def test_specify_results_filename_with_valid_session_id(self):
        rc, compiler = test_compile(general=[G('results_filename', 'a${session_id}.pdf'), G('get_session_id', 'Y')])
        self.assertEqual(0, rc)

    def test_specify_results_filename_with_invalid_session_id(self):
        rc, compiler = test_compile(general=[G('results_filename', 'a${session_id}.pdf')])
        self.assertEqual(2, rc)
        self.assertTrue('INVALID_FILENAME(SESSION_ID)' in compiler.logger.err_codes, 'error codes: ' + ','.join(compiler.logger.err_codes.keys()))

    def test_specify_results_filename_with_invalid_keyword(self):
        rc, compiler = test_compile(general=[G('results_filename', 'a${stam}.pdf')])
        self.assertEqual(2, rc)
        self.assertTrue('INVALID_FILENAME(UNKNOWN_KEYWORD)' in compiler.logger.err_codes, 'error codes: ' + ','.join(compiler.logger.err_codes.keys()))

    #--------------------------------------------------------
    # Specify background color
    #--------------------------------------------------------

    def test_specify_results_background_color_name(self):
        rc, compiler = test_compile(general=[G('background_color', 'white')])
        self.assertEqual(0, rc)

    def test_specify_results_background_color_invalid_name(self):
        rc, compiler = test_compile(general=[G('background_color', 'bullshit')])
        self.assertEqual(1, rc)

    def test_specify_results_background_color_hex(self):
        rc, compiler = test_compile(general=[G('background_color', '#FEFEFE')])
        self.assertEqual(0, rc)

    def test_specify_results_background_color_invalid_hex(self):
        rc, compiler = test_compile(general=[G('background_color', '#FFFFFG')])
        self.assertEqual(1, rc)



#=============================================================================================
class LayoutTests(unittest.TestCase):

    #--------------------------------------------------------
    def test_minimal_valid_definitions(self):
        rc, compiler = test_compile(layout=[Text('field1'), Text('field2')])
        self.assertEqual(0, rc)
        self.assertFalse(compiler.errors_found)

    def test_minimal_valid_definitions_with_text(self):
        rc, compiler = test_compile(layout=[Text('field1', text='hello')])
        self.assertEqual(0, rc)
        self.assertFalse(compiler.errors_found)

    #--------------------------------------------------------
    # Specify position
    #--------------------------------------------------------

    def test_specify_x_as_pcnt(self):
        rc, compiler = test_compile(layout=[Text('field1', x='50%')])
        self.assertEqual(0, rc)

    def test_specify_y_as_pcnt(self):
        rc, compiler = test_compile(layout=[Text('field1', y='-50%')])
        self.assertEqual(0, rc)

    def test_specify_x_as_px(self):
        rc, compiler = test_compile(layout=[Text('field1', x='-50px')])
        self.assertEqual(0, rc)

    def test_specify_y_as_px(self):
        rc, compiler = test_compile(layout=[Text('field1', y='5000px')])
        self.assertEqual(0, rc)

    def test_specify_x_in_invalid_format(self):
        rc, compiler = test_compile(layout=[Text('field1', x='5000')])
        self.assertEqual(2, rc)
        self.assertTrue('INVALID_COORD' in compiler.logger.err_codes, 'error codes: ' + ','.join(compiler.logger.err_codes.keys()))

    def test_specify_y_in_invalid_format(self):
        rc, compiler = test_compile(layout=[Text('field1', y='--500')])
        self.assertEqual(2, rc)
        self.assertTrue('INVALID_COORD' in compiler.logger.err_codes, 'error codes: ' + ','.join(compiler.logger.err_codes.keys()))

    def test_missing_x(self):
        rc, compiler = test_compile(layout=[Text('field1', x=None)])
        self.assertEqual(2, rc)
        self.assertTrue('EMPTY_COORD' in compiler.logger.err_codes, 'error codes: ' + ','.join(compiler.logger.err_codes.keys()))


    #--------------------------------------------------------
    # Errors
    #--------------------------------------------------------

    def test_invalid_control_type(self):
        rc, compiler = test_compile(layout=[dict(field_name='fld', type='magic')])
        self.assertEqual(2, rc)
        self.assertTrue(compiler.errors_found)
        self.assertTrue('INVALID_CONTROL_TYPE' in compiler.logger.err_codes, 'error codes: ' + ','.join(compiler.logger.err_codes.keys()))

    def test_duplicate_field_names_are_invalid(self):
        rc, compiler = test_compile(layout=[Text('field1'), Text('field2'), Text('field1')])
        self.assertEqual(2, rc)
        self.assertTrue(compiler.errors_found)
        self.assertTrue('DUPLICATE_FIELD' in compiler.logger.err_codes, 'error codes: ' + ','.join(compiler.logger.err_codes.keys()))

    def test_excessive_column_yield_warning(self):
        rc, compiler = test_compile(layout=[Text('field1', stam=1)])
        self.assertEqual(1, rc)
        self.assertFalse(compiler.errors_found)
        self.assertTrue(compiler.warnings_found)
        self.assertTrue('EXCESSIVE_COLUMN' in compiler.logger.err_codes, 'error codes: ' + ','.join(compiler.logger.err_codes.keys()))


#=============================================================================================
class ResponsesTests(unittest.TestCase):

    def test_resp_id_none(self):
        rc, compiler = test_compile(responses=[KbResponse(None, 1, '/')])
        self.assertEqual(2, rc)
        self.assertTrue(compiler.errors_found)
        self.assertTrue('MISSING_RESPONSE_ID' in compiler.logger.err_codes, 'error codes: ' + ','.join(compiler.logger.err_codes.keys()))

    def test_resp_id_empty(self):
        rc, compiler = test_compile(responses=[KbResponse('', 1, '/')])
        self.assertEqual(2, rc)
        self.assertTrue(compiler.errors_found)
        self.assertTrue('MISSING_RESPONSE_ID' in compiler.logger.err_codes, 'error codes: ' + ','.join(compiler.logger.err_codes.keys()))

    def test_resp_value_none(self):
        rc, compiler = test_compile(responses=[KbResponse('id1', None, '/')])
        self.assertEqual(2, rc)
        self.assertTrue(compiler.errors_found)
        self.assertTrue('MISSING_RESPONSE_VALUE' in compiler.logger.err_codes, 'error codes: ' + ','.join(compiler.logger.err_codes.keys()))

    def test_resp_value_empty(self):
        rc, compiler = test_compile(responses=[KbResponse('id1', '', '/')])
        self.assertEqual(2, rc)
        self.assertTrue(compiler.errors_found)
        self.assertTrue('MISSING_RESPONSE_VALUE' in compiler.logger.err_codes, 'error codes: ' + ','.join(compiler.logger.err_codes.keys()))

    def test_invalid_response_type(self):
        rc, compiler = test_compile(responses=[dict(id='r1', type='badtype', value=1)])
        self.assertEqual(2, rc)
        self.assertTrue(compiler.errors_found)
        self.assertTrue('INVALID_RESPONSE_TYPE' in compiler.logger.err_codes, 'error codes: ' + ','.join(compiler.logger.err_codes.keys()))


    #--------------------------------------------------------
    # Keyboard responses
    #--------------------------------------------------------

    def test_kbresp_valid(self):
        rc, compiler = test_compile(responses=[KbResponse('r1', 1, '/')])
        self.assertEqual(0, rc)
        self.assertFalse(compiler.errors_found)

    def test_kbresp_key_missing_col(self):
        rc, compiler = test_compile(responses=[dict(id='r1', type='key', value=1)])
        self.assertEqual(2, rc)
        self.assertTrue(compiler.errors_found)
        self.assertTrue('MISSING_KB_RESPONSE_KEY_COL' in compiler.logger.err_codes, 'error codes: ' + ','.join(compiler.logger.err_codes.keys()))

    def test_kbresp_key_empty(self):
        rc, compiler = test_compile(responses=[KbResponse('r1', 1, '')])
        self.assertEqual(2, rc)
        self.assertTrue(compiler.errors_found)
        self.assertTrue('MISSING_KB_RESPONSE_KEY' in compiler.logger.err_codes, 'error codes: ' + ','.join(compiler.logger.err_codes.keys()))

    def test_kbresp_key_none(self):
        rc, compiler = test_compile(responses=[KbResponse('r1', 1, None)])
        self.assertEqual(2, rc)
        self.assertTrue(compiler.errors_found)
        self.assertTrue('MISSING_KB_RESPONSE_KEY' in compiler.logger.err_codes, 'error codes: ' + ','.join(compiler.logger.err_codes.keys()))

    def test_kbresp_duplicate_keys_are_invalid(self):
        rc, compiler = test_compile(responses=[KbResponse('r1', 1, '/'), KbResponse('r2', 2, '/')])
        self.assertEqual(2, rc)
        self.assertTrue(compiler.errors_found)
        self.assertTrue('DUPLICATE_RESPONSE_KEY' in compiler.logger.err_codes, 'error codes: ' + ','.join(compiler.logger.err_codes.keys()))

    def test_kbresp_duplicate_response_ids_are_invalid(self):
        rc, compiler = test_compile(responses=[KbResponse('r1', 1, '/'), KbResponse('r1', 2, '.')])
        self.assertEqual(2, rc)
        self.assertTrue(compiler.errors_found)
        self.assertTrue('DUPLICATE_RESPONSE_ID' in compiler.logger.err_codes, 'error codes: ' + ','.join(compiler.logger.err_codes.keys()))

    #--------------------------------------------------------
    # Button responses
    #--------------------------------------------------------

    def test_btnresp_valid(self):
        rc, compiler = test_compile(responses=[BtnResponse('r1', 1, 'Click me')])
        self.assertEqual(0, rc)
        self.assertFalse(compiler.errors_found)

    def test_btnresp_text_missing(self):
        rc, compiler = test_compile(responses=[dict(id='r1', type='button', value=1)])
        self.assertEqual(2, rc)
        self.assertTrue(compiler.errors_found)
        self.assertTrue('MISSING_BUTTON_RESPONSE_TEXT_COL' in compiler.logger.err_codes, 'error codes: ' + ','.join(compiler.logger.err_codes.keys()))



if __name__ == '__main__':
    unittest.main()
