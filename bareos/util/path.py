"""
Class to handle file paths.
"""

from copy import copy

class Path(object):

    def __init__(self, path=None):
        self.__set_defaults()
        self.set_path(path)

    def __str__(self):
        result = ""
        if self.is_root():
            result += "/"
        result += "/".join(self.path)
        if (not self.is_root()) or self.len() > 0:
            if self.is_directory():
                result += "/"
        return result

    def __set_defaults(self):
        self.path_orig = None
        self.root = False
        self.directory = False
        self.path = None

    def set_path(self, path):
        if path == None:
            self.__set_defaults()
        elif isinstance(path, str):
            self.path_orig = path
            components = self.path_orig.split('/')
            self.path = [i for i in components if i != '']
            if path == "":
                self.root = False
                self.directory = True
            else:
                self.root = False
                if self.path_orig[0] == '/':
                    self.root = True
                self.directory = False
                if components[-1] == '':
                    self.directory = True
        else:
            # exception
            pass


    def get(self, index=None):
        if index == None:
            return self.path
        else:
            return self.path[index]


    #def lstrip(self, path=[]):
        #"""
        #Creates a new Path instance with lstrip components removed from left.
        #"""
        #result = copy(self)
        #result.root = False
        #for i in path:
            #if result.get(0) == i:
                #result.remove(0)
            #else:
                ## TODO: exception?
                #pass
        #return result

    def shift(self):
        """
        Creates a new Path instance with lstrip components removed from left.
        """
        result = self.get(0)
        self.remove(0)
        return result

    def is_directory(self):
        return self.directory

    def is_root(self):
        return self.root


    def remove(self, index):
        del(self.path[index])

    def len(self):
        return len(self.path)
