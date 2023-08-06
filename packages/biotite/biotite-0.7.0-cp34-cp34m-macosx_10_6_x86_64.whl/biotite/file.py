# This source code is part of the Biotite package and is distributed
# under the 3-Clause BSD License. Please see 'LICENSE.rst' for further
# information.

__author__ = "Patrick Kunzmann"
__all__ = ["File", "TextFile"]

import abc
from .copyable import Copyable
import copy


class File(Copyable, metaclass=abc.ABCMeta):
    """
    Base class for all file classes. Every file class is
    instantiated without arguments. In order to fill the instance
    with content, either a file is read using the `read()` method,
    or the instance is directly modified with class specific setter
    methods. In order to write the instance content into a file the
    `write()` method is used.
    """
    
    def __init__(self):
        pass
    
    @abc.abstractmethod
    def read(self, file_name):
        """
        Parse a file and store the content in this object.
        
        Parameters
        ----------
        file_name : str
            The path of the file to be read.
        """
        pass
    
    @abc.abstractmethod
    def write(self, file_name):
        """
        Write the contents of this object into a file.
        
        Parameters
        ----------
        file_name : str
            The path of the file to be written.
        """
        pass
        

class TextFile(File, metaclass=abc.ABCMeta):
    """
    Base class for all text file classes. When reading a file, the text
    content is saved as list of strings. When writing a file, the list
    is written into the file.
    
    Attributes
    ----------
    _lines : list
        List of string representing the lines in the text file.
    """
    
    def __init__(self):
        self._lines = []
    
    def read(self, file_name):
        """
        Read the lines of the given text file.
        
        Parameters
        ----------
        file_name : str
            The name of the file to be read.
        """
        with open(file_name, "r") as f:
            str_data = f.read()
        self._lines = str_data.split("\n")
        self.process_input()
    
    def read_from_string(self, string):
        """
        Read the lines from the given string.
        
        Parameters
        ----------
        file_name : str
            The string to be read.
        """
        self._lines = string.split("\n")
        self.process_input()
    
    def process_input(self):
        """
        Process the input read from file or string.

        PROTECTED: Optionally override when inheriting
        """
        pass
    
    def write(self, file_name):
        """
        Write the content to a given text file.
        
        Parameters
        ----------
        file_name : str
            The name of the file to be written to.
        """
        with open(file_name, "w") as f:
            f.writelines([line+"\n" for line in self._lines])
    
    def __copy_fill__(self, clone):
        super().__copy_fill__(clone)
        clone._lines = copy.copy(self._lines)
    
    def __str__(self):
        return("\n".join(self._lines))


class InvalidFileError(Exception):
    """
    Indicates that the file is not suitable for the requested action.
    """
    pass