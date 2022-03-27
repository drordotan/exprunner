
import os
import numpy as np
import openpyxl
import pandas as pd
import math
from numbers import Number

import expcompiler.logger


class XlsReader(object):
    """
    Parse an excel file with experiment config
    """

    #-- Worksheet names
    ws_general = 'general'
    ws_instructions = 'instructions'
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

        all_ws_names = XlsReader.ws_general, XlsReader.ws_trial_type, XlsReader.ws_layout, XlsReader.ws_response, XlsReader.ws_trials
        mandatory_ws_names = XlsReader.ws_general, XlsReader.ws_layout, XlsReader.ws_trials

        errors = False
        for wsn in mandatory_ws_names:
            if wsn not in self.worksheets:
                self.logger.error("Invalid configuration file {}: Worksheet '{}' is missing".format(os.path.basename(self._filename), wsn),
                                  'MISSING_WORKSHEET_IN_CONFIG')
                errors = True

        for ws in wb.worksheets:
            if ws.title in all_ws_names:
                if self._duplicate_col_names(ws):
                    errors = True

        wb.close()

        return not errors


    #--------------------------------------------------
    def general_config(self):
        """
        Return general config parameters, as a dictionary with several entries
        :return:
        """
        if XlsReader.ws_general not in self.worksheets:
            return None

        return self._load_worksheet_as_data_frame(XlsReader.ws_general, ('param', 'value'), converters=dict(value=_parse_str))

    #--------------------------------------------------
    def instructions_config(self):
        """
        Return instructions config parameters, as a dictionary with several entries
        :return:
        """
        if XlsReader.ws_instructions not in self.worksheets:
            return None

        return self._load_worksheet_as_data_frame(XlsReader.ws_instructions, ('text', 'responses'), converters=dict(value=_parse_str))

    #--------------------------------------------------
    def _load_worksheet_as_data_frame(self, ws_name, expected_col_names=(), converters=None):
        df = pd.read_excel(self._filename, ws_name, converters=converters)
        ok = True
        for col_name in expected_col_names:
            if col_name not in df:
                self.logger.error('Invalid format in worksheet "{}": Column "{}" is missing'.format(ws_name, col_name),
                                  'MISSING_COL(sheet={})'.format(XlsReader.ws_general))
        return df if ok else None


    #--------------------------------------------------
    def layout(self):
        if XlsReader.ws_layout not in self.worksheets:
            return None

        return self._load_worksheet_as_data_frame(XlsReader.ws_layout, ('layout_name', 'type'))


    #--------------------------------------------------
    def trial_types(self):
        if XlsReader.ws_trial_type not in self.worksheets:
            return None

        return self._load_worksheet_as_data_frame(XlsReader.ws_trial_type, ('layout items', ))


    #--------------------------------------------------
    def response_modes(self):
        if XlsReader.ws_response not in self.worksheets:
            return None

        return self._load_worksheet_as_data_frame(XlsReader.ws_response, ('response_name', 'type', 'value'))


    #--------------------------------------------------
    def trials(self):
        if XlsReader.ws_trials not in self.worksheets:
            return None

        return self._load_worksheet_as_data_frame(XlsReader.ws_trials)


    #--------------------------------------------------
    def _duplicate_col_names(self, sheet):
        col_titles = np.array([str(sheet.cell(1, c+1).value).lower() for c in range(sheet.max_column)])
        uniq_titles = set(col_titles)
        if len(col_titles) != len(uniq_titles):
            duplicates = [t for t in uniq_titles if sum(col_titles == t) > 1]
            self.logger.error('Error in worksheet "{}": some columns appear twice ({}).'.format(sheet.title, ",".join(duplicates)),
                              'DUPLICATE_COL_NAMES')
            return True

        return False


#---------------------------------------------------------------
def _isnan(value):
    return isinstance(value, Number) and math.isnan(value)

def _nan_to_none(value):
    return None if _isnan(value) else value

def _parse_str(value):
    return None if _isnan(value) else str(value)
