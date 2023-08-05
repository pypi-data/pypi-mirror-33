""" Data objects in group "outputs" """
from design_nest.eplus_components.helper import BaseObject



class OutputSQLite(BaseObject):
    """Corresponds to object `Output:SQLite`"""
    _schema = {
        'type': 'object',
        'patternProperties': {
            '.*': {
                'type': 'object',
                'properties': {
                    'option_type': {
                        'enum': [
                            'Simple',
                            'SimpleAndTabular'],
                        'type': 'string'}}}},
        'maxProperties': 1}

    @property
    def option_type(self):
        return self["option_type"]

    @option_type.setter
    def option_type(self, value=None):
        self["option_type"] = value




class OutputTableSummaryReports(BaseObject):
    """Corresponds to object `Output:Table:SummaryReports`"""
    _schema = {
        'extensible_size': 1.0,
        'patternProperties': {
            '.*': {
                'type': 'object',
                'properties': {
                    'reports': {
                        'items': {
                            'type': 'object',
                            'properties': {
                                'report_name': {
                                    'type': 'string'}}},
                        'type': 'array'}}}},
        'maxProperties': 1,
        'type': 'object'}

    @property
    def reports(self):
        return self["reports"]

    @reports.setter
    def reports(self, value=None):
        self["reports"] = value


