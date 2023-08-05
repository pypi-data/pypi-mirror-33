""" Data objects in group "building" """
from design_nest.eplus_components.helper import BaseObject



class SiteLocation(BaseObject):
    """Corresponds to object `Site:Location`"""
    _schema = {
        'name': {
            'is_required': True,
            'type': 'string'},
        'patternProperties': {
            '.*': {
                'properties': {
                    'latitude': {
                        'default': 0.0,
                        'maximum': 90.0,
                        'minimum': -90.0,
                        'units': 'deg',
                        'type': 'number'},
                    'elevation': {
                        'exclusiveMaximum': True,
                        'default': 0.0,
                        'maximum': 8900.0,
                        'minimum': -300.0,
                        'units': 'm',
                        'type': 'number'},
                    'time_zone': {
                        'default': 0.0,
                        'maximum': 14.0,
                        'minimum': -12.0,
                        'units': 'hr',
                        'type': 'number'},
                    'longitude': {
                        'default': 0.0,
                        'maximum': 180.0,
                        'minimum': -180.0,
                        'units': 'deg',
                        'type': 'number'}},
                'type': 'object'}},
        'maxProperties': 1,
        'type': 'object',
        'min_fields': 5.0}

    @property
    def latitude(self):
        return self["latitude"]

    @latitude.setter
    def latitude(self, value=None):
        self["latitude"] = value

    @property
    def elevation(self):
        return self["elevation"]

    @elevation.setter
    def elevation(self, value=None):
        self["elevation"] = value

    @property
    def time_zone(self):
        return self["time_zone"]

    @time_zone.setter
    def time_zone(self, value=None):
        self["time_zone"] = value

    @property
    def longitude(self):
        return self["longitude"]

    @longitude.setter
    def longitude(self, value=None):
        self["longitude"] = value




class Building(BaseObject):
    """Corresponds to object `Building`"""
    _schema = {
        'name': {
            'default': 'NONE',
            'retaincase': True,
            'type': 'string'},
        'patternProperties': {
            '.*': {
                'type': 'object',
                'properties': {
                    'solar_distribution': {
                        'default': 'FullExterior',
                        'enum': [
                            '',
                            'FullExterior',
                            'FullExteriorWithReflections',
                            'FullInteriorAndExterior',
                            'FullInteriorAndExteriorWithReflections',
                            'MinimalShadowing'],
                        'type': 'string'},
                    'terrain': {
                        'default': 'Suburbs',
                        'enum': [
                            '',
                            'City',
                            'Country',
                            'Ocean',
                            'Suburbs',
                            'Urban'],
                        'type': 'string'},
                    'north_axis': {
                        'units': 'deg',
                        'default': 0.0,
                        'type': 'number'},
                    'maximum_number_of_warmup_days': {
                        'exclusiveMinimum': True,
                        'default': 25.0,
                        'minimum': 0.0,
                        'type': 'number'},
                    'loads_convergence_tolerance_value': {
                        'default': 0.04,
                        'type': 'number',
                        'maximum': 0.5,
                        'minimum': 0.0,
                        'exclusiveMinimum': True},
                    'temperature_convergence_tolerance_value': {
                        'default': 0.4,
                        'type': 'number',
                        'maximum': 0.5,
                        'minimum': 0.0,
                        'units': 'deltaC',
                        'exclusiveMinimum': True},
                    'minimum_number_of_warmup_days': {
                        'exclusiveMinimum': True,
                        'default': 6.0,
                        'minimum': 0.0,
                        'type': 'number'}}}},
        'maxProperties': 1,
        'minProperties': 1,
        'type': 'object',
        'min_fields': 8.0}

    @property
    def solar_distribution(self):
        return self["solar_distribution"]

    @solar_distribution.setter
    def solar_distribution(self, value=None):
        self["solar_distribution"] = value

    @property
    def terrain(self):
        return self["terrain"]

    @terrain.setter
    def terrain(self, value=None):
        self["terrain"] = value

    @property
    def north_axis(self):
        return self["north_axis"]

    @north_axis.setter
    def north_axis(self, value=None):
        self["north_axis"] = value

    @property
    def maximum_number_of_warmup_days(self):
        return self["maximum_number_of_warmup_days"]

    @maximum_number_of_warmup_days.setter
    def maximum_number_of_warmup_days(self, value=None):
        self["maximum_number_of_warmup_days"] = value

    @property
    def loads_convergence_tolerance_value(self):
        return self["loads_convergence_tolerance_value"]

    @loads_convergence_tolerance_value.setter
    def loads_convergence_tolerance_value(self, value=None):
        self["loads_convergence_tolerance_value"] = value

    @property
    def temperature_convergence_tolerance_value(self):
        return self["temperature_convergence_tolerance_value"]

    @temperature_convergence_tolerance_value.setter
    def temperature_convergence_tolerance_value(self, value=None):
        self["temperature_convergence_tolerance_value"] = value

    @property
    def minimum_number_of_warmup_days(self):
        return self["minimum_number_of_warmup_days"]

    @minimum_number_of_warmup_days.setter
    def minimum_number_of_warmup_days(self, value=None):
        self["minimum_number_of_warmup_days"] = value


