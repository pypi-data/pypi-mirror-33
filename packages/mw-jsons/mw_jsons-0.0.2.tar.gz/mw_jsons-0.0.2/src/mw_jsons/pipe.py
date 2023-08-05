from abc import ABCMeta, abstractmethod

class Pipe(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def read(url,departament):

        pass

    @abstractmethod
    def write(object,type):

        pass