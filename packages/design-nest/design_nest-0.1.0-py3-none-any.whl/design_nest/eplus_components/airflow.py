""" Data objects in group "airflow" """
from design_nest.eplus_components.helper import BaseObject



class ZoneInfiltrationDesignFlowRate(BaseObject):
    """Corresponds to object `ZoneInfiltration:DesignFlowRate`"""
    _schema = {
        'name': {
            'is_required': True,
            'type': 'string'},
        'min_fields': 12.0,
        'patternProperties': {
            '.*': {
                'required': [
                    'zone_or_zonelist_name',
                    'schedule_name'],
                'properties': {
                    'velocity_squared_term_coefficient': {
                        'default': 0.0,
                        'type': 'number'},
                    'constant_term_coefficient': {
                        'default': 1.0,
                        'type': 'number'},
                    'schedule_name': {
                        'type': 'string',
                        'object_list': ['ScheduleNames'],
                        'data_type': 'object_list'},
                    'air_changes_per_hour': {
                        'units': '1/hr',
                        'minimum': 0.0,
                        'type': 'number'},
                    'velocity_term_coefficient': {
                        'default': 0.0,
                        'type': 'number'},
                    'flow_per_exterior_surface_area': {
                        'units': 'm3/s-m2',
                        'minimum': 0.0,
                        'type': 'number'},
                    'design_flow_rate': {
                        'units': 'm3/s',
                        'ip-units': 'ft3/min',
                        'minimum': 0.0,
                        'type': 'number'},
                    'zone_or_zonelist_name': {
                        'type': 'string',
                        'object_list': ['ZoneAndZoneListNames'],
                        'data_type': 'object_list'},
                    'design_flow_rate_calculation_method': {
                        'default': 'Flow/Zone',
                        'enum': [
                            '',
                            'AirChanges/Hour',
                            'Flow/Area',
                            'Flow/ExteriorArea',
                            'Flow/ExteriorWallArea',
                            'Flow/Zone'],
                        'type': 'string'},
                    'flow_per_zone_floor_area': {
                        'units': 'm3/s-m2',
                        'minimum': 0.0,
                        'type': 'number'},
                    'temperature_term_coefficient': {
                        'default': 0.0,
                        'type': 'number'}},
                'type': 'object'}},
        'type': 'object'}

    @property
    def velocity_squared_term_coefficient(self):
        return self["velocity_squared_term_coefficient"]

    @velocity_squared_term_coefficient.setter
    def velocity_squared_term_coefficient(self, value=None):
        self["velocity_squared_term_coefficient"] = value

    @property
    def constant_term_coefficient(self):
        return self["constant_term_coefficient"]

    @constant_term_coefficient.setter
    def constant_term_coefficient(self, value=None):
        self["constant_term_coefficient"] = value

    @property
    def schedule_name(self):
        return self["schedule_name"]

    @schedule_name.setter
    def schedule_name(self, value=None):
        self["schedule_name"] = value

    @property
    def air_changes_per_hour(self):
        return self["air_changes_per_hour"]

    @air_changes_per_hour.setter
    def air_changes_per_hour(self, value=None):
        self["air_changes_per_hour"] = value

    @property
    def velocity_term_coefficient(self):
        return self["velocity_term_coefficient"]

    @velocity_term_coefficient.setter
    def velocity_term_coefficient(self, value=None):
        self["velocity_term_coefficient"] = value

    @property
    def flow_per_exterior_surface_area(self):
        return self["flow_per_exterior_surface_area"]

    @flow_per_exterior_surface_area.setter
    def flow_per_exterior_surface_area(self, value=None):
        self["flow_per_exterior_surface_area"] = value

    @property
    def design_flow_rate(self):
        return self["design_flow_rate"]

    @design_flow_rate.setter
    def design_flow_rate(self, value=None):
        self["design_flow_rate"] = value

    @property
    def zone_or_zonelist_name(self):
        return self["zone_or_zonelist_name"]

    @zone_or_zonelist_name.setter
    def zone_or_zonelist_name(self, value=None):
        self["zone_or_zonelist_name"] = value

    @property
    def design_flow_rate_calculation_method(self):
        return self["design_flow_rate_calculation_method"]

    @design_flow_rate_calculation_method.setter
    def design_flow_rate_calculation_method(self, value=None):
        self["design_flow_rate_calculation_method"] = value

    @property
    def flow_per_zone_floor_area(self):
        return self["flow_per_zone_floor_area"]

    @flow_per_zone_floor_area.setter
    def flow_per_zone_floor_area(self, value=None):
        self["flow_per_zone_floor_area"] = value

    @property
    def temperature_term_coefficient(self):
        return self["temperature_term_coefficient"]

    @temperature_term_coefficient.setter
    def temperature_term_coefficient(self, value=None):
        self["temperature_term_coefficient"] = value




class ZoneVentilationDesignFlowRate(BaseObject):
    """Corresponds to object `ZoneVentilation:DesignFlowRate`"""
    _schema = {
        'name': {
            'is_required': True,
            'type': 'string',
            'reference': ['VentilationNames']},
        'min_fields': 15.0,
        'patternProperties': {
            '.*': {
                'required': [
                    'zone_or_zonelist_name',
                    'schedule_name'],
                'properties': {
                    'delta_temperature_schedule_name': {
                        'object_list': ['ScheduleNames'],
                        'type': 'string',
                        'data_type': 'object_list'},
                    'fan_pressure_rise': {
                        'units': 'Pa',
                        'default': 0.0,
                        'minimum': 0.0,
                        'type': 'number'},
                    'schedule_name': {
                        'type': 'string',
                        'object_list': ['ScheduleNames'],
                        'data_type': 'object_list'},
                    'minimum_outdoor_temperature': {
                        'default': -100.0,
                        'maximum': 100.0,
                        'minimum': -100.0,
                        'units': 'C',
                        'type': 'number'},
                    'flow_rate_per_person': {
                        'units': 'm3/s-person',
                        'minimum': 0.0,
                        'type': 'number'},
                    'air_changes_per_hour': {
                        'units': '1/hr',
                        'minimum': 0.0,
                        'type': 'number'},
                    'maximum_indoor_temperature_schedule_name': {
                        'object_list': ['ScheduleNames'],
                        'type': 'string',
                        'data_type': 'object_list'},
                    'maximum_outdoor_temperature_schedule_name': {
                        'object_list': ['ScheduleNames'],
                        'type': 'string',
                        'data_type': 'object_list'},
                    'flow_rate_per_zone_floor_area': {
                        'units': 'm3/s-m2',
                        'minimum': 0.0,
                        'type': 'number'},
                    'ventilation_type': {
                        'default': 'Natural',
                        'enum': [
                            '',
                            'Balanced',
                            'Exhaust',
                            'Intake',
                            'Natural'],
                        'type': 'string'},
                    'design_flow_rate_calculation_method': {
                        'default': 'Flow/Zone',
                        'enum': [
                            '',
                            'AirChanges/Hour',
                            'Flow/Area',
                            'Flow/Person',
                            'Flow/Zone'],
                        'type': 'string'},
                    'velocity_squared_term_coefficient': {
                        'default': 0.0,
                        'type': 'number'},
                    'zone_or_zonelist_name': {
                        'type': 'string',
                        'object_list': ['ZoneAndZoneListNames'],
                        'data_type': 'object_list'},
                    'minimum_indoor_temperature': {
                        'default': -100.0,
                        'maximum': 100.0,
                        'minimum': -100.0,
                        'units': 'C',
                        'type': 'number'},
                    'velocity_term_coefficient': {
                        'default': 0.0,
                        'type': 'number'},
                    'fan_total_efficiency': {
                        'default': 1.0,
                        'exclusiveMinimum': True,
                        'minimum': 0.0,
                        'type': 'number'},
                    'temperature_term_coefficient': {
                        'default': 0.0,
                        'type': 'number'},
                    'minimum_indoor_temperature_schedule_name': {
                        'object_list': ['ScheduleNames'],
                        'type': 'string',
                        'data_type': 'object_list'},
                    'delta_temperature': {
                        'units': 'deltaC',
                        'default': -100.0,
                        'minimum': -100.0,
                        'type': 'number'},
                    'minimum_outdoor_temperature_schedule_name': {
                        'object_list': ['ScheduleNames'],
                        'type': 'string',
                        'data_type': 'object_list'},
                    'maximum_indoor_temperature': {
                        'default': 100.0,
                        'maximum': 100.0,
                        'minimum': -100.0,
                        'units': 'C',
                        'type': 'number'},
                    'maximum_wind_speed': {
                        'default': 40.0,
                        'maximum': 40.0,
                        'minimum': 0.0,
                        'units': 'm/s',
                        'type': 'number'},
                    'maximum_outdoor_temperature': {
                        'default': 100.0,
                        'maximum': 100.0,
                        'minimum': -100.0,
                        'units': 'C',
                        'type': 'number'},
                    'constant_term_coefficient': {
                        'default': 1.0,
                        'type': 'number'},
                    'design_flow_rate': {
                        'units': 'm3/s',
                        'minimum': 0.0,
                        'type': 'number'}},
                'type': 'object'}},
        'type': 'object'}

    @property
    def delta_temperature_schedule_name(self):
        return self["delta_temperature_schedule_name"]

    @delta_temperature_schedule_name.setter
    def delta_temperature_schedule_name(self, value=None):
        self["delta_temperature_schedule_name"] = value

    @property
    def fan_pressure_rise(self):
        return self["fan_pressure_rise"]

    @fan_pressure_rise.setter
    def fan_pressure_rise(self, value=None):
        self["fan_pressure_rise"] = value

    @property
    def schedule_name(self):
        return self["schedule_name"]

    @schedule_name.setter
    def schedule_name(self, value=None):
        self["schedule_name"] = value

    @property
    def minimum_outdoor_temperature(self):
        return self["minimum_outdoor_temperature"]

    @minimum_outdoor_temperature.setter
    def minimum_outdoor_temperature(self, value=None):
        self["minimum_outdoor_temperature"] = value

    @property
    def flow_rate_per_person(self):
        return self["flow_rate_per_person"]

    @flow_rate_per_person.setter
    def flow_rate_per_person(self, value=None):
        self["flow_rate_per_person"] = value

    @property
    def air_changes_per_hour(self):
        return self["air_changes_per_hour"]

    @air_changes_per_hour.setter
    def air_changes_per_hour(self, value=None):
        self["air_changes_per_hour"] = value

    @property
    def maximum_indoor_temperature_schedule_name(self):
        return self["maximum_indoor_temperature_schedule_name"]

    @maximum_indoor_temperature_schedule_name.setter
    def maximum_indoor_temperature_schedule_name(self, value=None):
        self["maximum_indoor_temperature_schedule_name"] = value

    @property
    def maximum_outdoor_temperature_schedule_name(self):
        return self["maximum_outdoor_temperature_schedule_name"]

    @maximum_outdoor_temperature_schedule_name.setter
    def maximum_outdoor_temperature_schedule_name(self, value=None):
        self["maximum_outdoor_temperature_schedule_name"] = value

    @property
    def flow_rate_per_zone_floor_area(self):
        return self["flow_rate_per_zone_floor_area"]

    @flow_rate_per_zone_floor_area.setter
    def flow_rate_per_zone_floor_area(self, value=None):
        self["flow_rate_per_zone_floor_area"] = value

    @property
    def ventilation_type(self):
        return self["ventilation_type"]

    @ventilation_type.setter
    def ventilation_type(self, value=None):
        self["ventilation_type"] = value

    @property
    def design_flow_rate_calculation_method(self):
        return self["design_flow_rate_calculation_method"]

    @design_flow_rate_calculation_method.setter
    def design_flow_rate_calculation_method(self, value=None):
        self["design_flow_rate_calculation_method"] = value

    @property
    def velocity_squared_term_coefficient(self):
        return self["velocity_squared_term_coefficient"]

    @velocity_squared_term_coefficient.setter
    def velocity_squared_term_coefficient(self, value=None):
        self["velocity_squared_term_coefficient"] = value

    @property
    def zone_or_zonelist_name(self):
        return self["zone_or_zonelist_name"]

    @zone_or_zonelist_name.setter
    def zone_or_zonelist_name(self, value=None):
        self["zone_or_zonelist_name"] = value

    @property
    def minimum_indoor_temperature(self):
        return self["minimum_indoor_temperature"]

    @minimum_indoor_temperature.setter
    def minimum_indoor_temperature(self, value=None):
        self["minimum_indoor_temperature"] = value

    @property
    def velocity_term_coefficient(self):
        return self["velocity_term_coefficient"]

    @velocity_term_coefficient.setter
    def velocity_term_coefficient(self, value=None):
        self["velocity_term_coefficient"] = value

    @property
    def fan_total_efficiency(self):
        return self["fan_total_efficiency"]

    @fan_total_efficiency.setter
    def fan_total_efficiency(self, value=None):
        self["fan_total_efficiency"] = value

    @property
    def temperature_term_coefficient(self):
        return self["temperature_term_coefficient"]

    @temperature_term_coefficient.setter
    def temperature_term_coefficient(self, value=None):
        self["temperature_term_coefficient"] = value

    @property
    def minimum_indoor_temperature_schedule_name(self):
        return self["minimum_indoor_temperature_schedule_name"]

    @minimum_indoor_temperature_schedule_name.setter
    def minimum_indoor_temperature_schedule_name(self, value=None):
        self["minimum_indoor_temperature_schedule_name"] = value

    @property
    def delta_temperature(self):
        return self["delta_temperature"]

    @delta_temperature.setter
    def delta_temperature(self, value=None):
        self["delta_temperature"] = value

    @property
    def minimum_outdoor_temperature_schedule_name(self):
        return self["minimum_outdoor_temperature_schedule_name"]

    @minimum_outdoor_temperature_schedule_name.setter
    def minimum_outdoor_temperature_schedule_name(self, value=None):
        self["minimum_outdoor_temperature_schedule_name"] = value

    @property
    def maximum_indoor_temperature(self):
        return self["maximum_indoor_temperature"]

    @maximum_indoor_temperature.setter
    def maximum_indoor_temperature(self, value=None):
        self["maximum_indoor_temperature"] = value

    @property
    def maximum_wind_speed(self):
        return self["maximum_wind_speed"]

    @maximum_wind_speed.setter
    def maximum_wind_speed(self, value=None):
        self["maximum_wind_speed"] = value

    @property
    def maximum_outdoor_temperature(self):
        return self["maximum_outdoor_temperature"]

    @maximum_outdoor_temperature.setter
    def maximum_outdoor_temperature(self, value=None):
        self["maximum_outdoor_temperature"] = value

    @property
    def constant_term_coefficient(self):
        return self["constant_term_coefficient"]

    @constant_term_coefficient.setter
    def constant_term_coefficient(self, value=None):
        self["constant_term_coefficient"] = value

    @property
    def design_flow_rate(self):
        return self["design_flow_rate"]

    @design_flow_rate.setter
    def design_flow_rate(self, value=None):
        self["design_flow_rate"] = value


