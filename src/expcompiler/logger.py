


class Logger(object):

    def __init__(self):
        self.err_codes = {}


    def error(self, msg, err_code):
        print(msg)
        self.err_codes[err_code] = msg
