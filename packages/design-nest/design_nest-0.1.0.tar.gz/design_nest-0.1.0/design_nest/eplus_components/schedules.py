""" Data objects in group "schedules" """
from design_nest.eplus_components.helper import BaseObject



class ScheduleTypeLimits(BaseObject):
    """Corresponds to object `ScheduleTypeLimits`"""
    _schema = {
        'type': 'object',
        'patternProperties': {
            '.*': {
                'type': 'object',
                'properties': {
                    'numeric_type': {
                        'enum': [
                            'Continuous',
                            'Discrete'],
                        'type': 'string'},
                    'unit_type': {
                        'default': 'Dimensionless',
                        'enum': [
                            '',
                            'ActivityLevel',
                            'Angle',
                            'Availability',
                            'Capacity',
                            'Control',
                            'ConvectionCoefficient',
                            'DeltaTemperature',
                            'Dimensionless',
                            'Mode',
                            'Percent',
                            'Power',
                            'PrecipitationRate',
                            'Temperature',
                            'Velocity'],
                        'type': 'string'},
                    'lower_limit_value': {
                        'type': 'number',
                        'unitsBasedOnField': 'unit_type'},
                    'upper_limit_value': {
                        'type': 'number',
                        'unitsBasedOnField': 'unit_type'}}}},
        'name': {
            'is_required': True,
            'type': 'string',
            'reference': ['ScheduleTypeLimitsNames']}}

    @property
    def numeric_type(self):
        return self["numeric_type"]

    @numeric_type.setter
    def numeric_type(self, value=None):
        self["numeric_type"] = value

    @property
    def unit_type(self):
        return self["unit_type"]

    @unit_type.setter
    def unit_type(self, value=None):
        self["unit_type"] = value

    @property
    def lower_limit_value(self):
        return self["lower_limit_value"]

    @lower_limit_value.setter
    def lower_limit_value(self, value=None):
        self["lower_limit_value"] = value

    @property
    def upper_limit_value(self):
        return self["upper_limit_value"]

    @upper_limit_value.setter
    def upper_limit_value(self, value=None):
        self["upper_limit_value"] = value


