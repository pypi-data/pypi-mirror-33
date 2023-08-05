# -*- coding: utf-8 -*-

"""Toolkit for everyday use.

Classes:
Logger: a wrapper around logging.loggerClass with boilerplate taken care of
XFile: a wrapper aroung File and gzip.GzipFile

Functions:
header, blue, green, yellow, orange, red, bold, underline: apply self explaining decoration to text (as interpreted by terminal)
xopen: similar to open but returns an XFile object
"""

import logging
import gzip


class Logger():
    """Use logging module to create a logger object with desired verbosity while taking care of the boilerplate.
    
    Class members:
    logger: object returned by logging.getLogger(__name__)
    handler: object returned by logging.StreamHandler()
    
    Class methods:
    setLevel: map verbosity to logging level then calls logger.setLevel
    debug: same as logger.debug
    info: same as logger.info
    warning: same as logger.warning
    error: calls self.logger.error then calls exit() with given code
    """
    def __init__(self, verbose):
        """Wrap around a logger object and set logger level according to verbose parameter.
        
        Positional argument:
        verbose (int): verbosity; translates to logging levels: 0 ==> WARNING, 1 ==> INFO, 2+ ==> DEBUG
        """
        self.logger = logging.getLogger(__name__)
        self.handler = logging.StreamHandler()
        self.logger.addHandler(self.handler)

        self.setLevel(verbose)
        
        self.debug = self.logger.debug
        self.info = self.logger.info
        self.warning = self.logger.warning

    def setLevel(self, verbose):
        if verbose==0: self.logger.setLevel(logging.WARNING)
        if verbose==1: self.logger.setLevel(logging.INFO)
        if verbose>=2: self.logger.setLevel(logging.DEBUG)


    def error(self, msg, code=1):
        """Log an error message and exit with given code (default: 1)."""
        self.logger.error(msg)
        exit(code)


class __TextDecoration___:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    ORANGE = '\033[38;5;214m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def header(text):
    """Take a string as input and returns the same string enclosed in markers for header decoration in terminal."""
    return __TextDecoration___.HEADER+text+__TextDecoration___.ENDC


def blue(text):
    """Take a string as input and returns the same string enclosed in markers for making it print blue in terminal."""
    return __TextDecoration___.BLUE+text+__TextDecoration___.ENDC


def green(text):
    """Take a string as input and returns the same string enclosed in markers for making it print green in terminal."""
    return __TextDecoration___.GREEN+text+__TextDecoration___.ENDC


def yellow(text):
    """Take a string as input and returns the same string enclosed in markers for making it print yellow in terminal."""
    return __TextDecoration___.YELLOW+text+__TextDecoration___.ENDC


def orange(text):
    """Take a string as input and returns the same string enclosed in markers for making it print orange in terminal."""
    return __TextDecoration___.ORANGE+text+__TextDecoration___.ENDC


def red(text):
    """Take a string as input and returns the same string enclosed in markers for making it print red in terminal."""
    return __TextDecoration___.RED+text+__TextDecoration___.ENDC


def bold(text):
    """Take a string as input and returns the same string enclosed in markers for making it print bold in terminal."""
    return __TextDecoration___.BOLD+text+__TextDecoration___.ENDC


def underline(text):
    """Take a string as input and returns the same string enclosed in markers for making it print underlined in terminal."""
    return __TextDecoration___.UNDERLINE+text+__TextDecoration___.ENDC


class XFile():
    """Wrap around File and gzip.GzipFile objects and transparently provide the same functionalities.
    
    Class members:
    encoding: file encoding (applicable in text mode)
    file: underlying File or gzip.GzipFile object
    mode: open mode
    
    Class methods:
    __init__: create an XFile instance
    close: close underlying file
    write: write data to file (bytes or text)
    read: read data from file
    readline: read one line of text from file
    readlines: read all lines from file
    """
    def __init__(self, f, mode="r", encoding="utf8"):
        """Wrap given file f into XFile object with given mode and encoding."""
        self.encoding = encoding
        self.file = f
        self.mode = mode
    
    def __iter__(self):
        return self
    
    def __next__(self):
        line = self.readline()
        if line=="":
            raise StopIteration
        else:
            return line
    
    def __enter__(self):
        return self
    
    def __exit__(self, arg1, arg2, arg3):
        return self.file.__exit__(arg1, arg2, arg3)
    
    def close(self):
        """Close file by calling underlying file's close() method."""
        self.file.close()
    
    def write(self, data):
        """Write data to file. Interpreted as text if data has an encode() method."""
        if isinstance(self.file, gzip.GzipFile) and hasattr(data, "encode"):
            return self.file.write(data.encode(self.encoding))
        else:
            return self.file.write(data)
    
    def read(self, size=-1):
        """Read data from file. Interpreted as text if file is open in text mode."""
        line = self.file.read(size)
        try:
            return line.decode(encoding=self.encoding) if type(line)==bytes and not self.mode.endswith("b") else line
        except:
            return line
    
    def readline(self, size=-1):
        """Read one line of data from file. Interpreted as text if file is open in text mode."""
        line = self.file.readline(size)
        try:
            return line.decode(self.encoding) if type(line)==bytes and not self.mode.endswith("b") else line
        except:
            return line
    
    def readlines(self, hint=-1):
        """Read all lines from file. Interpreted as text if file is open in text mode."""
        lines = self.file.readlines(hint)
        if isinstance(self.file, gzip.GzipFile) and not self.mode.endswith("b"):
            try:
                return [l.decode(self.encoding) for l in lines]
            except:
                return lines
        else:
            return lines


def xopen(fname, mode="r", encoding="utf8"):
    """Open a file with given mode and try to decode text data, if applicable. Wrap file into an XFile object.
    
    :param fname: file path and name
    :param mode: open mode
    :param encoding: explicit encoding
    :return: XFile object
    """
    if fname.endswith(".gz") or mode.endswith("b"):
        return XFile(gzip.open(fname, mode=mode), mode, encoding)
    else:
        return XFile(open(fname, mode, encoding=encoding), mode, encoding)
