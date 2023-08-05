""" Data objects in group "systems" """
from design_nest.eplus_components.helper import BaseObject



class HVACTemplateZoneIdealLoadsAirSystem(BaseObject):
    """Corresponds to object `HVACTemplate:Zone:IdealLoadsAirSystem`"""
    _schema = {
        'type': 'object',
        'patternProperties': {
            '.*': {
                'required': ['zone_name'],
                'type': 'object',
                'properties': {
                    'maximum_heating_supply_air_temperature': {
                        'exclusiveMaximum': True,
                        'default': 50.0,
                        'type': 'number',
                        'maximum': 100.0,
                        'minimum': 0.0,
                        'units': 'C',
                        'exclusiveMinimum': True},
                    'dehumidification_setpoint': {
                        'default': 60.0,
                        'maximum': 100.0,
                        'minimum': 0.0,
                        'units': 'percent',
                        'type': 'number'},
                    'design_specification_outdoor_air_object_name': {
                        'object_list': ['DesignSpecificationOutdoorAirNames'],
                        'type': 'string',
                        'data_type': 'object_list'},
                    'zone_name': {
                        'type': 'string',
                        'object_list': ['ZoneNames'],
                        'data_type': 'object_list'},
                    'minimum_cooling_supply_air_temperature': {
                        'exclusiveMaximum': True,
                        'default': 13.0,
                        'type': 'number',
                        'maximum': 50.0,
                        'minimum': -100.0,
                        'units': 'C',
                        'exclusiveMinimum': True},
                    'cooling_availability_schedule_name': {
                        'object_list': ['ScheduleNames'],
                        'type': 'string',
                        'data_type': 'object_list'},
                    'minimum_cooling_supply_air_humidity_ratio': {
                        'units': 'kgWater/kgDryAir',
                        'exclusiveMinimum': True,
                        'default': 0.0077,
                        'minimum': 0.0,
                        'type': 'number'},
                    'humidification_control_type': {
                        'default': 'None',
                        'enum': [
                            '',
                            'ConstantSupplyHumidityRatio',
                            'Humidistat',
                            'None'],
                        'type': 'string'},
                    'maximum_total_cooling_capacity': {
                        'units': 'W',
                        'anyOf': [
                            {
                                'minimum': 0.0,
                                'type': 'number'},
                            {
                                'enum': ['Autosize'],
                                'type': 'string'}]},
                    'template_thermostat_name': {
                        'object_list': ['CompactHVACThermostats'],
                        'type': 'string',
                        'data_type': 'object_list'},
                    'heat_recovery_type': {
                        'default': 'None',
                        'enum': [
                            '',
                            'Enthalpy',
                            'None',
                            'Sensible'],
                        'type': 'string'},
                    'outdoor_air_flow_rate_per_person': {
                        'units': 'm3/s',
                        'default': 0.00944,
                        'type': 'number'},
                    'maximum_heating_air_flow_rate': {
                        'units': 'm3/s',
                        'anyOf': [
                            {
                                'minimum': 0.0,
                                'type': 'number'},
                            {
                                'enum': ['Autosize'],
                                'type': 'string'}]},
                    'outdoor_air_economizer_type': {
                        'default': 'NoEconomizer',
                        'enum': [
                            '',
                            'DifferentialDryBulb',
                            'DifferentialEnthalpy',
                            'NoEconomizer'],
                        'type': 'string'},
                    'heating_availability_schedule_name': {
                        'object_list': ['ScheduleNames'],
                        'type': 'string',
                        'data_type': 'object_list'},
                    'cooling_sensible_heat_ratio': {
                        'default': 0.7,
                        'exclusiveMinimum': True,
                        'maximum': 1.0,
                        'minimum': 0.0,
                        'units': 'dimensionless',
                        'type': 'number'},
                    'latent_heat_recovery_effectiveness': {
                        'default': 0.65,
                        'maximum': 1.0,
                        'minimum': 0.0,
                        'units': 'dimensionless',
                        'type': 'number'},
                    'maximum_heating_supply_air_humidity_ratio': {
                        'units': 'kgWater/kgDryAir',
                        'exclusiveMinimum': True,
                        'default': 0.0156,
                        'minimum': 0.0,
                        'type': 'number'},
                    'outdoor_air_flow_rate_per_zone_floor_area': {
                        'units': 'm3/s-m2',
                        'default': 0.0,
                        'type': 'number'},
                    'humidification_setpoint': {
                        'default': 30.0,
                        'maximum': 100.0,
                        'minimum': 0.0,
                        'units': 'percent',
                        'type': 'number'},
                    'dehumidification_control_type': {
                        'default': 'ConstantSensibleHeatRatio',
                        'enum': [
                            '',
                            'ConstantSensibleHeatRatio',
                            'ConstantSupplyHumidityRatio',
                            'Humidistat',
                            'None'],
                        'type': 'string'},
                    'maximum_sensible_heating_capacity': {
                        'units': 'W',
                        'anyOf': [
                            {
                                'minimum': 0.0,
                                'type': 'number'},
                            {
                                'enum': ['Autosize'],
                                'type': 'string'}]},
                    'heating_limit': {
                        'default': 'NoLimit',
                        'enum': [
                            '',
                            'LimitCapacity',
                            'LimitFlowRate',
                            'LimitFlowRateAndCapacity',
                            'NoLimit'],
                        'type': 'string'},
                    'outdoor_air_flow_rate_per_zone': {
                        'units': 'm3/s',
                        'default': 0.0,
                        'type': 'number'},
                    'demand_controlled_ventilation_type': {
                        'default': 'None',
                        'enum': [
                            '',
                            'CO2Setpoint',
                            'None',
                            'OccupancySchedule'],
                        'type': 'string'},
                    'outdoor_air_method': {
                        'default': 'None',
                        'enum': [
                            '',
                            'DetailedSpecification',
                            'Flow/Area',
                            'Flow/Person',
                            'Flow/Zone',
                            'Maximum',
                            'None',
                            'Sum'],
                        'type': 'string'},
                    'maximum_cooling_air_flow_rate': {
                        'units': 'm3/s',
                        'anyOf': [
                            {
                                'minimum': 0.0,
                                'type': 'number'},
                            {
                                'enum': ['Autosize'],
                                'type': 'string'}]},
                    'system_availability_schedule_name': {
                        'object_list': ['ScheduleNames'],
                        'type': 'string',
                        'data_type': 'object_list'},
                    'sensible_heat_recovery_effectiveness': {
                        'units': 'dimensionless',
                        'default': 0.7,
                        'minimum': 0.0,
                        'type': 'number',
                        'maximum': 1.0},
                    'cooling_limit': {
                        'default': 'NoLimit',
                        'enum': [
                            '',
                            'LimitCapacity',
                            'LimitFlowRate',
                            'LimitFlowRateAndCapacity',
                            'NoLimit'],
                        'type': 'string'}}}},
        'min_fields': 26.0}

    @property
    def maximum_heating_supply_air_temperature(self):
        return self["maximum_heating_supply_air_temperature"]

    @maximum_heating_supply_air_temperature.setter
    def maximum_heating_supply_air_temperature(self, value=None):
        self["maximum_heating_supply_air_temperature"] = value

    @property
    def dehumidification_setpoint(self):
        return self["dehumidification_setpoint"]

    @dehumidification_setpoint.setter
    def dehumidification_setpoint(self, value=None):
        self["dehumidification_setpoint"] = value

    @property
    def design_specification_outdoor_air_object_name(self):
        return self["design_specification_outdoor_air_object_name"]

    @design_specification_outdoor_air_object_name.setter
    def design_specification_outdoor_air_object_name(self, value=None):
        self["design_specification_outdoor_air_object_name"] = value

    @property
    def zone_name(self):
        return self["zone_name"]

    @zone_name.setter
    def zone_name(self, value=None):
        self["zone_name"] = value

    @property
    def minimum_cooling_supply_air_temperature(self):
        return self["minimum_cooling_supply_air_temperature"]

    @minimum_cooling_supply_air_temperature.setter
    def minimum_cooling_supply_air_temperature(self, value=None):
        self["minimum_cooling_supply_air_temperature"] = value

    @property
    def cooling_availability_schedule_name(self):
        return self["cooling_availability_schedule_name"]

    @cooling_availability_schedule_name.setter
    def cooling_availability_schedule_name(self, value=None):
        self["cooling_availability_schedule_name"] = value

    @property
    def minimum_cooling_supply_air_humidity_ratio(self):
        return self["minimum_cooling_supply_air_humidity_ratio"]

    @minimum_cooling_supply_air_humidity_ratio.setter
    def minimum_cooling_supply_air_humidity_ratio(self, value=None):
        self["minimum_cooling_supply_air_humidity_ratio"] = value

    @property
    def humidification_control_type(self):
        return self["humidification_control_type"]

    @humidification_control_type.setter
    def humidification_control_type(self, value=None):
        self["humidification_control_type"] = value

    @property
    def maximum_total_cooling_capacity(self):
        return self["maximum_total_cooling_capacity"]

    @maximum_total_cooling_capacity.setter
    def maximum_total_cooling_capacity(self, value=None):
        self["maximum_total_cooling_capacity"] = value

    @property
    def template_thermostat_name(self):
        return self["template_thermostat_name"]

    @template_thermostat_name.setter
    def template_thermostat_name(self, value=None):
        self["template_thermostat_name"] = value

    @property
    def heat_recovery_type(self):
        return self["heat_recovery_type"]

    @heat_recovery_type.setter
    def heat_recovery_type(self, value=None):
        self["heat_recovery_type"] = value

    @property
    def outdoor_air_flow_rate_per_person(self):
        return self["outdoor_air_flow_rate_per_person"]

    @outdoor_air_flow_rate_per_person.setter
    def outdoor_air_flow_rate_per_person(self, value=None):
        self["outdoor_air_flow_rate_per_person"] = value

    @property
    def maximum_heating_air_flow_rate(self):
        return self["maximum_heating_air_flow_rate"]

    @maximum_heating_air_flow_rate.setter
    def maximum_heating_air_flow_rate(self, value=None):
        self["maximum_heating_air_flow_rate"] = value

    @property
    def outdoor_air_economizer_type(self):
        return self["outdoor_air_economizer_type"]

    @outdoor_air_economizer_type.setter
    def outdoor_air_economizer_type(self, value=None):
        self["outdoor_air_economizer_type"] = value

    @property
    def heating_availability_schedule_name(self):
        return self["heating_availability_schedule_name"]

    @heating_availability_schedule_name.setter
    def heating_availability_schedule_name(self, value=None):
        self["heating_availability_schedule_name"] = value

    @property
    def cooling_sensible_heat_ratio(self):
        return self["cooling_sensible_heat_ratio"]

    @cooling_sensible_heat_ratio.setter
    def cooling_sensible_heat_ratio(self, value=None):
        self["cooling_sensible_heat_ratio"] = value

    @property
    def latent_heat_recovery_effectiveness(self):
        return self["latent_heat_recovery_effectiveness"]

    @latent_heat_recovery_effectiveness.setter
    def latent_heat_recovery_effectiveness(self, value=None):
        self["latent_heat_recovery_effectiveness"] = value

    @property
    def maximum_heating_supply_air_humidity_ratio(self):
        return self["maximum_heating_supply_air_humidity_ratio"]

    @maximum_heating_supply_air_humidity_ratio.setter
    def maximum_heating_supply_air_humidity_ratio(self, value=None):
        self["maximum_heating_supply_air_humidity_ratio"] = value

    @property
    def outdoor_air_flow_rate_per_zone_floor_area(self):
        return self["outdoor_air_flow_rate_per_zone_floor_area"]

    @outdoor_air_flow_rate_per_zone_floor_area.setter
    def outdoor_air_flow_rate_per_zone_floor_area(self, value=None):
        self["outdoor_air_flow_rate_per_zone_floor_area"] = value

    @property
    def humidification_setpoint(self):
        return self["humidification_setpoint"]

    @humidification_setpoint.setter
    def humidification_setpoint(self, value=None):
        self["humidification_setpoint"] = value

    @property
    def dehumidification_control_type(self):
        return self["dehumidification_control_type"]

    @dehumidification_control_type.setter
    def dehumidification_control_type(self, value=None):
        self["dehumidification_control_type"] = value

    @property
    def maximum_sensible_heating_capacity(self):
        return self["maximum_sensible_heating_capacity"]

    @maximum_sensible_heating_capacity.setter
    def maximum_sensible_heating_capacity(self, value=None):
        self["maximum_sensible_heating_capacity"] = value

    @property
    def heating_limit(self):
        return self["heating_limit"]

    @heating_limit.setter
    def heating_limit(self, value=None):
        self["heating_limit"] = value

    @property
    def outdoor_air_flow_rate_per_zone(self):
        return self["outdoor_air_flow_rate_per_zone"]

    @outdoor_air_flow_rate_per_zone.setter
    def outdoor_air_flow_rate_per_zone(self, value=None):
        self["outdoor_air_flow_rate_per_zone"] = value

    @property
    def demand_controlled_ventilation_type(self):
        return self["demand_controlled_ventilation_type"]

    @demand_controlled_ventilation_type.setter
    def demand_controlled_ventilation_type(self, value=None):
        self["demand_controlled_ventilation_type"] = value

    @property
    def outdoor_air_method(self):
        return self["outdoor_air_method"]

    @outdoor_air_method.setter
    def outdoor_air_method(self, value=None):
        self["outdoor_air_method"] = value

    @property
    def maximum_cooling_air_flow_rate(self):
        return self["maximum_cooling_air_flow_rate"]

    @maximum_cooling_air_flow_rate.setter
    def maximum_cooling_air_flow_rate(self, value=None):
        self["maximum_cooling_air_flow_rate"] = value

    @property
    def system_availability_schedule_name(self):
        return self["system_availability_schedule_name"]

    @system_availability_schedule_name.setter
    def system_availability_schedule_name(self, value=None):
        self["system_availability_schedule_name"] = value

    @property
    def sensible_heat_recovery_effectiveness(self):
        return self["sensible_heat_recovery_effectiveness"]

    @sensible_heat_recovery_effectiveness.setter
    def sensible_heat_recovery_effectiveness(self, value=None):
        self["sensible_heat_recovery_effectiveness"] = value

    @property
    def cooling_limit(self):
        return self["cooling_limit"]

    @cooling_limit.setter
    def cooling_limit(self, value=None):
        self["cooling_limit"] = value


