import os
import re


class XMLLogger(object):
    """Simple logger used for xml"""
    PASSWORD_DISPLAY = "Password>*******</"

    def __init__(self, path):
        try:
            os.makedirs(os.path.dirname(path))
        except:
            pass
        self._descriptor = open(path, 'w+')

    def __del__(self):
        self._descriptor.close()

    def _write_data(self, data):
        self._descriptor.write(data + '\r\n')
        self._descriptor.flush()

    def info(self, data):
        self._write_data(self._prepare_output(data))

    def _prepare_output(self, data):
        return re.sub(r"Password>.*?</", self.PASSWORD_DISPLAY, data)
