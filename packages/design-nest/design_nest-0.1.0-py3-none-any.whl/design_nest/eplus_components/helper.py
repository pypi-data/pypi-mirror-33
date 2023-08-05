""" Helper methods for design_nest """
import design_nest

class BaseObject(object):

    _schema = {}

    @property
    def schema(self):
        """ Get schema of class"""
        return self._schema

    def __init__(self):
        """ Init data dictionary object
        """
        self._model = {}
        for key in self.schema['patternProperties']['.*']['properties']:
            self._model[key] = None

    def __setitem__(self, key, value):
        self._model[key] = value

    def __getitem__(self, key):
        return self._model[key]