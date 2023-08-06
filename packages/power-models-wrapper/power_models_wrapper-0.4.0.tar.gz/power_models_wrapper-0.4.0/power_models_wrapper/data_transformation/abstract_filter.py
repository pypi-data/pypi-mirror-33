# In order to make this class AbstractBaseClass:
from abc import ABCMeta, abstractmethod

class AbstractFilter(object):

    # Return value: Dictionary
    @abstractmethod
    def filter(self, data_dictionary):
      pass
