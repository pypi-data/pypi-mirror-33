import logging

__author__ = 'Nordstrom Cloud Engineering'
__version__ = '0.1.3'

class NullHandler(logging.Handler):
    def emit(self, record):
        pass

logging.getLogger('toto9').addHandler(NullHandler())
                
