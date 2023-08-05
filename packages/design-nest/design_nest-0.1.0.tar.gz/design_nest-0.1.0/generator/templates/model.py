import json


class Model:
    """ Represents an E+ epJSON file """

    required_objects = [{{required_objects}}]
    unique_objects = [{{unique_objects}}]

    def __init__(self, path=None):
        """ Inits epJSON object."""
        self._model = {}

        if path is not None:
            self.load(path)

    def add(self, obj):
        group = obj.schema['group']
        name = obj.schema['name']
        if name not in self._model[group]:
            self._model[group][name] = []
        if name in self.unique_objects:
            self._model[group][name] = [obj]
        else:
            self._model[group][name].append(obj)

    def save(self, path):
        """ Save epJSON to path.
        Args:
            path (str): path where data should be save
        """

        with open(path, 'w') as out_file:
            json.dump(self._model, out_file)
    
    def load(self, path):
        """ Loads epJSON data from path.
        Args:
            path (str): path to read data from
        """

        with open(path) as in_file:
            self._model = json.load(in_file)