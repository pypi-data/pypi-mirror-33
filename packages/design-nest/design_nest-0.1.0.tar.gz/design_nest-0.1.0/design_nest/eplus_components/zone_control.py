""" Data objects in group "zone_control" """
from design_nest.eplus_components.helper import BaseObject



class ZoneControlThermostat(BaseObject):
    """Corresponds to object `ZoneControl:Thermostat`"""
    _schema = {
        'type': 'object',
        'patternProperties': {
            '.*': {
                'required': [
                    'zone_or_zonelist_name',
                    'control_type_schedule_name',
                    'control_1_object_type',
                    'control_1_name'],
                'type': 'object',
                'properties': {
                    'control_2_name': {
                        'object_list': ['ControlTypeNames'],
                        'type': 'string',
                        'data_type': 'object_list'},
                    'control_4_name': {
                        'object_list': ['ControlTypeNames'],
                        'type': 'string',
                        'data_type': 'object_list'},
                    'control_1_name': {
                        'type': 'string',
                                'object_list': ['ControlTypeNames'],
                                'data_type': 'object_list'},
                    'control_type_schedule_name': {
                        'type': 'string',
                        'object_list': ['ScheduleNames'],
                        'data_type': 'object_list'},
                    'control_1_object_type': {
                        'type': 'string',
                        'enum': [
                            'ThermostatSetpoint:DualSetpoint',
                            'ThermostatSetpoint:SingleCooling',
                            'ThermostatSetpoint:SingleHeating',
                            'ThermostatSetpoint:SingleHeatingOrCooling']},
                    'temperature_difference_between_cutout_and_setpoint': {
                        'units': 'deltaC',
                        'default': 0.0,
                        'minimum': 0.0,
                        'type': 'number'},
                    'zone_or_zonelist_name': {
                        'type': 'string',
                        'object_list': ['ZoneAndZoneListNames'],
                        'data_type': 'object_list'},
                    'control_3_name': {
                        'object_list': ['ControlTypeNames'],
                        'type': 'string',
                        'data_type': 'object_list'},
                    'control_4_object_type': {
                        'enum': [
                            'ThermostatSetpoint:DualSetpoint',
                            'ThermostatSetpoint:SingleCooling',
                            'ThermostatSetpoint:SingleHeating',
                            'ThermostatSetpoint:SingleHeatingOrCooling'],
                        'type': 'string'},
                    'control_2_object_type': {
                        'enum': [
                            'ThermostatSetpoint:DualSetpoint',
                            'ThermostatSetpoint:SingleCooling',
                            'ThermostatSetpoint:SingleHeating',
                            'ThermostatSetpoint:SingleHeatingOrCooling'],
                        'type': 'string'},
                    'control_3_object_type': {
                        'enum': [
                            'ThermostatSetpoint:DualSetpoint',
                            'ThermostatSetpoint:SingleCooling',
                            'ThermostatSetpoint:SingleHeating',
                            'ThermostatSetpoint:SingleHeatingOrCooling'],
                        'type': 'string'}}}},
        'name': {
            'is_required': True,
            'type': 'string',
            'reference': ['ZoneControlThermostaticNames']}}

    @property
    def control_2_name(self):
        return self["control_2_name"]

    @control_2_name.setter
    def control_2_name(self, value=None):
        self["control_2_name"] = value

    @property
    def control_4_name(self):
        return self["control_4_name"]

    @control_4_name.setter
    def control_4_name(self, value=None):
        self["control_4_name"] = value

    @property
    def control_1_name(self):
        return self["control_1_name"]

    @control_1_name.setter
    def control_1_name(self, value=None):
        self["control_1_name"] = value

    @property
    def control_type_schedule_name(self):
        return self["control_type_schedule_name"]

    @control_type_schedule_name.setter
    def control_type_schedule_name(self, value=None):
        self["control_type_schedule_name"] = value

    @property
    def control_1_object_type(self):
        return self["control_1_object_type"]

    @control_1_object_type.setter
    def control_1_object_type(self, value=None):
        self["control_1_object_type"] = value

    @property
    def temperature_difference_between_cutout_and_setpoint(self):
        return self["temperature_difference_between_cutout_and_setpoint"]

    @temperature_difference_between_cutout_and_setpoint.setter
    def temperature_difference_between_cutout_and_setpoint(self, value=None):
        self["temperature_difference_between_cutout_and_setpoint"] = value

    @property
    def zone_or_zonelist_name(self):
        return self["zone_or_zonelist_name"]

    @zone_or_zonelist_name.setter
    def zone_or_zonelist_name(self, value=None):
        self["zone_or_zonelist_name"] = value

    @property
    def control_3_name(self):
        return self["control_3_name"]

    @control_3_name.setter
    def control_3_name(self, value=None):
        self["control_3_name"] = value

    @property
    def control_4_object_type(self):
        return self["control_4_object_type"]

    @control_4_object_type.setter
    def control_4_object_type(self, value=None):
        self["control_4_object_type"] = value

    @property
    def control_2_object_type(self):
        return self["control_2_object_type"]

    @control_2_object_type.setter
    def control_2_object_type(self, value=None):
        self["control_2_object_type"] = value

    @property
    def control_3_object_type(self):
        return self["control_3_object_type"]

    @control_3_object_type.setter
    def control_3_object_type(self, value=None):
        self["control_3_object_type"] = value




class ThermostatSetpointSingleHeating(BaseObject):
    """Corresponds to object `ThermostatSetpoint:SingleHeating`"""
    _schema = {
        'type': 'object',
        'patternProperties': {
            '.*': {
                'type': 'object',
                'properties': {
                    'setpoint_temperature_schedule_name': {
                        'object_list': ['ScheduleNames'],
                        'type': 'string',
                        'data_type': 'object_list'}}}},
        'name': {
            'is_required': True,
            'type': 'string',
            'reference': ['ControlTypeNames']}}

    @property
    def setpoint_temperature_schedule_name(self):
        return self["setpoint_temperature_schedule_name"]

    @setpoint_temperature_schedule_name.setter
    def setpoint_temperature_schedule_name(self, value=None):
        self["setpoint_temperature_schedule_name"] = value




class ThermostatSetpointSingleCooling(BaseObject):
    """Corresponds to object `ThermostatSetpoint:SingleCooling`"""
    _schema = {
        'type': 'object',
        'patternProperties': {
            '.*': {
                'type': 'object',
                'properties': {
                    'setpoint_temperature_schedule_name': {
                        'object_list': ['ScheduleNames'],
                        'type': 'string',
                        'data_type': 'object_list'}}}},
        'name': {
            'is_required': True,
            'type': 'string',
            'reference': ['ControlTypeNames']}}

    @property
    def setpoint_temperature_schedule_name(self):
        return self["setpoint_temperature_schedule_name"]

    @setpoint_temperature_schedule_name.setter
    def setpoint_temperature_schedule_name(self, value=None):
        self["setpoint_temperature_schedule_name"] = value




class ThermostatSetpointSingleHeatingOrCooling(BaseObject):
    """Corresponds to object `ThermostatSetpoint:SingleHeatingOrCooling`"""
    _schema = {
        'type': 'object',
        'patternProperties': {
            '.*': {
                'type': 'object',
                'properties': {
                    'setpoint_temperature_schedule_name': {
                        'object_list': ['ScheduleNames'],
                        'type': 'string',
                        'data_type': 'object_list'}}}},
        'name': {
            'is_required': True,
            'type': 'string',
            'reference': ['ControlTypeNames']}}

    @property
    def setpoint_temperature_schedule_name(self):
        return self["setpoint_temperature_schedule_name"]

    @setpoint_temperature_schedule_name.setter
    def setpoint_temperature_schedule_name(self, value=None):
        self["setpoint_temperature_schedule_name"] = value




class ThermostatSetpointDualSetpoint(BaseObject):
    """Corresponds to object `ThermostatSetpoint:DualSetpoint`"""
    _schema = {
        'type': 'object',
        'patternProperties': {
            '.*': {
                'type': 'object',
                'properties': {
                    'heating_setpoint_temperature_schedule_name': {
                        'object_list': ['ScheduleNames'],
                        'type': 'string',
                        'data_type': 'object_list'},
                    'cooling_setpoint_temperature_schedule_name': {
                        'object_list': ['ScheduleNames'],
                        'type': 'string',
                        'data_type': 'object_list'}}}},
        'name': {
            'is_required': True,
            'type': 'string',
            'reference': ['ControlTypeNames']}}

    @property
    def heating_setpoint_temperature_schedule_name(self):
        return self["heating_setpoint_temperature_schedule_name"]

    @heating_setpoint_temperature_schedule_name.setter
    def heating_setpoint_temperature_schedule_name(self, value=None):
        self["heating_setpoint_temperature_schedule_name"] = value

    @property
    def cooling_setpoint_temperature_schedule_name(self):
        return self["cooling_setpoint_temperature_schedule_name"]

    @cooling_setpoint_temperature_schedule_name.setter
    def cooling_setpoint_temperature_schedule_name(self, value=None):
        self["cooling_setpoint_temperature_schedule_name"] = value


