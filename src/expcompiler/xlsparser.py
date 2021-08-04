
import os
import openpyxl
import pandas as pd
import math
from numbers import Number

import expcompiler.logger


class XlsParser(object):
    """
    Parse an excel file with experiment config
    """

    #-- Worksheet names
    ws_general = 'general'
    ws_trial_type = 'trial_type'
    ws_layout = 'layout'
    ws_response = 'response'
    ws_trials = 'trials'


    #--------------------------------------------------
    def __init__(self, filename, logger=None):
        self._filename = filename
        self.worksheets = None
        self.logger = logger or expcompiler.logger.Logger()


    #--------------------------------------------------
    def open(self):
        """
        Open the config file
        """

        if not os.path.exists(self._filename):
            raise ValueError("Config file does not exist ({})".format(self._filename))

        wb = openpyxl.open(self._filename, read_only=True)
        self.worksheets = {ws.title for ws in wb.worksheets}
        wb.close()

        expected_ws_names = XlsParser.ws_general, XlsParser.ws_trial_type, XlsParser.ws_layout, XlsParser.ws_response, \
                            XlsParser.ws_trials
        ok = True
        for wsn in expected_ws_names:
            if wsn not in self.worksheets:
                self.logger.error("Invalid configuration file {}: Worksheet '{}' is missing".format(os.path.basename(self._filename), wsn),
                                  'MISSING_WORKSHEET_IN_CONFIG')
                ok = False

        return ok


    #--------------------------------------------------
    def general_config(self):
        """
        Return general config parameters, as a dictionary with several entries
        :return:
        """
        if XlsParser.ws_general not in self.worksheets:
            return None

        return self._load_worksheet_as_data_frame(XlsParser.ws_general, ('param', 'value'), converters=dict(value=_parse_str))


    #--------------------------------------------------
    def _load_worksheet_as_data_frame(self, ws_name, expected_col_names=(), converters=None):
        df = pd.read_excel(self._filename, ws_name, converters=converters)
        ok = True
        for col_name in expected_col_names:
            if col_name not in df:
                self.logger.error('Invalid format in worksheet "{}": Column "{}" is missing'.format(ws_name, col_name),
                                  'MISSING_COL(sheet={})'.format(XlsParser.ws_general))
        return df if ok else None


    #--------------------------------------------------
    def layout(self):
        if XlsParser.ws_layout not in self.worksheets:
            return None

        return self._load_worksheet_as_data_frame(XlsParser.ws_layout, ('field_name', 'type'))


    #--------------------------------------------------
    def trial_types(self):
        if XlsParser.ws_trial_type not in self.worksheets:
            return None

        return self._load_worksheet_as_data_frame(XlsParser.ws_trial_type, ('fields'))


    #--------------------------------------------------
    def response_modes(self):
        if XlsParser.ws_response not in self.worksheets:
            return None

        return self._load_worksheet_as_data_frame(XlsParser.ws_response, ('id', 'type', 'value'))


    #--------------------------------------------------
    def trials(self):
        if XlsParser.ws_trials not in self.worksheets:
            return None

        return self._load_worksheet_as_data_frame(XlsParser.ws_response)


#---------------------------------------------------------------
def _isnan(value):
    return isinstance(value, Number) and math.isnan(value)

def _nan_to_none(value):
    return None if _isnan(value) else value

def _parse_str(value):
    return None if _isnan(value) else str(value)
