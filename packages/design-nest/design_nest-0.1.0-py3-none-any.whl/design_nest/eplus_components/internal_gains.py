""" Data objects in group "internal_gains" """
from design_nest.eplus_components.helper import BaseObject



class People(BaseObject):
    """Corresponds to object `People`"""
    _schema = {
        'name': {
            'is_required': True,
            'type': 'string',
            'reference': ['PeopleNames']},
        'min_fields': 10.0,
        'patternProperties': {
            '.*': {
                'required': [
                    'zone_or_zonelist_name',
                    'number_of_people_schedule_name',
                    'activity_level_schedule_name'],
                'properties': {
                    'thermal_comfort_model_5_type': {
                        'enum': [
                            'AdaptiveASH55',
                            'AdaptiveCEN15251',
                            'Fanger',
                            'KSU',
                            'Pierce'],
                        'type': 'string'},
                    'thermal_comfort_model_4_type': {
                        'enum': [
                            'AdaptiveASH55',
                            'AdaptiveCEN15251',
                            'Fanger',
                            'KSU',
                            'Pierce'],
                        'type': 'string'},
                    'mean_radiant_temperature_calculation_type': {
                        'default': 'ZoneAveraged',
                        'enum': [
                            '',
                            'AngleFactor',
                            'SurfaceWeighted',
                            'ZoneAveraged'],
                        'type': 'string'},
                    'people_per_zone_floor_area': {
                        'units': 'person/m2',
                        'minimum': 0.0,
                        'type': 'number'},
                    'sensible_heat_fraction': {
                        'default': 'Autocalculate',
                        'anyOf': [
                            {
                                'minimum': 0.0,
                                'type': 'number',
                                'maximum': 1.0},
                            {
                                'enum': [
                                    '',
                                    'Autocalculate'],
                                'type': 'string'}]},
                    'clothing_insulation_calculation_method': {
                        'default': 'ClothingInsulationSchedule',
                        'enum': [
                            '',
                            'CalculationMethodSchedule',
                            'ClothingInsulationSchedule',
                            'DynamicClothingModelASHRAE55'],
                        'type': 'string'},
                    'surface_name_angle_factor_list_name': {
                        'object_list': ['AllHeatTranAngFacNames'],
                        'type': 'string',
                        'data_type': 'object_list'},
                    'zone_floor_area_per_person': {
                        'units': 'm2/person',
                        'minimum': 0.0,
                        'type': 'number'},
                    'fraction_radiant': {
                        'default': 0.3,
                        'minimum': 0.0,
                        'type': 'number',
                        'maximum': 1.0},
                    'thermal_comfort_model_2_type': {
                        'enum': [
                            'AdaptiveASH55',
                            'AdaptiveCEN15251',
                            'Fanger',
                            'KSU',
                            'Pierce'],
                        'type': 'string'},
                    'enable_ashrae_55_comfort_warnings': {
                        'default': 'No',
                        'enum': [
                            '',
                            'No',
                            'Yes'],
                        'type': 'string'},
                    'clothing_insulation_schedule_name': {
                        'object_list': ['ScheduleNames'],
                        'type': 'string',
                        'data_type': 'object_list'},
                    'zone_or_zonelist_name': {
                        'type': 'string',
                        'object_list': ['ZoneAndZoneListNames'],
                        'data_type': 'object_list'},
                    'clothing_insulation_calculation_method_schedule_name': {
                        'object_list': ['ScheduleNames'],
                        'type': 'string',
                        'data_type': 'object_list'},
                    'thermal_comfort_model_3_type': {
                        'enum': [
                            'AdaptiveASH55',
                            'AdaptiveCEN15251',
                            'Fanger',
                            'KSU',
                            'Pierce'],
                        'type': 'string'},
                    'work_efficiency_schedule_name': {
                        'object_list': ['ScheduleNames'],
                        'type': 'string',
                        'data_type': 'object_list'},
                    'number_of_people_schedule_name': {
                        'type': 'string',
                        'object_list': ['ScheduleNames'],
                        'data_type': 'object_list'},
                    'carbon_dioxide_generation_rate': {
                        'default': 3.82e-08,
                        'maximum': 3.82e-07,
                        'minimum': 0.0,
                        'units': 'm3/s-W',
                        'type': 'number'},
                    'thermal_comfort_model_1_type': {
                        'enum': [
                            'AdaptiveASH55',
                            'AdaptiveCEN15251',
                            'Fanger',
                            'KSU',
                            'Pierce'],
                        'type': 'string'},
                    'number_of_people': {
                        'minimum': 0.0,
                        'type': 'number'},
                    'number_of_people_calculation_method': {
                        'default': 'People',
                        'enum': [
                            '',
                            'Area/Person',
                            'People',
                            'People/Area'],
                        'type': 'string'},
                    'air_velocity_schedule_name': {
                        'object_list': ['ScheduleNames'],
                        'type': 'string',
                        'data_type': 'object_list'},
                    'activity_level_schedule_name': {
                        'type': 'string',
                        'object_list': ['ScheduleNames'],
                        'data_type': 'object_list'}},
                'type': 'object'}},
        'type': 'object'}

    @property
    def thermal_comfort_model_5_type(self):
        return self["thermal_comfort_model_5_type"]

    @thermal_comfort_model_5_type.setter
    def thermal_comfort_model_5_type(self, value=None):
        self["thermal_comfort_model_5_type"] = value

    @property
    def thermal_comfort_model_4_type(self):
        return self["thermal_comfort_model_4_type"]

    @thermal_comfort_model_4_type.setter
    def thermal_comfort_model_4_type(self, value=None):
        self["thermal_comfort_model_4_type"] = value

    @property
    def mean_radiant_temperature_calculation_type(self):
        return self["mean_radiant_temperature_calculation_type"]

    @mean_radiant_temperature_calculation_type.setter
    def mean_radiant_temperature_calculation_type(self, value=None):
        self["mean_radiant_temperature_calculation_type"] = value

    @property
    def people_per_zone_floor_area(self):
        return self["people_per_zone_floor_area"]

    @people_per_zone_floor_area.setter
    def people_per_zone_floor_area(self, value=None):
        self["people_per_zone_floor_area"] = value

    @property
    def sensible_heat_fraction(self):
        return self["sensible_heat_fraction"]

    @sensible_heat_fraction.setter
    def sensible_heat_fraction(self, value=None):
        self["sensible_heat_fraction"] = value

    @property
    def clothing_insulation_calculation_method(self):
        return self["clothing_insulation_calculation_method"]

    @clothing_insulation_calculation_method.setter
    def clothing_insulation_calculation_method(self, value=None):
        self["clothing_insulation_calculation_method"] = value

    @property
    def surface_name_angle_factor_list_name(self):
        return self["surface_name_angle_factor_list_name"]

    @surface_name_angle_factor_list_name.setter
    def surface_name_angle_factor_list_name(self, value=None):
        self["surface_name_angle_factor_list_name"] = value

    @property
    def zone_floor_area_per_person(self):
        return self["zone_floor_area_per_person"]

    @zone_floor_area_per_person.setter
    def zone_floor_area_per_person(self, value=None):
        self["zone_floor_area_per_person"] = value

    @property
    def fraction_radiant(self):
        return self["fraction_radiant"]

    @fraction_radiant.setter
    def fraction_radiant(self, value=None):
        self["fraction_radiant"] = value

    @property
    def thermal_comfort_model_2_type(self):
        return self["thermal_comfort_model_2_type"]

    @thermal_comfort_model_2_type.setter
    def thermal_comfort_model_2_type(self, value=None):
        self["thermal_comfort_model_2_type"] = value

    @property
    def enable_ashrae_55_comfort_warnings(self):
        return self["enable_ashrae_55_comfort_warnings"]

    @enable_ashrae_55_comfort_warnings.setter
    def enable_ashrae_55_comfort_warnings(self, value=None):
        self["enable_ashrae_55_comfort_warnings"] = value

    @property
    def clothing_insulation_schedule_name(self):
        return self["clothing_insulation_schedule_name"]

    @clothing_insulation_schedule_name.setter
    def clothing_insulation_schedule_name(self, value=None):
        self["clothing_insulation_schedule_name"] = value

    @property
    def zone_or_zonelist_name(self):
        return self["zone_or_zonelist_name"]

    @zone_or_zonelist_name.setter
    def zone_or_zonelist_name(self, value=None):
        self["zone_or_zonelist_name"] = value

    @property
    def clothing_insulation_calculation_method_schedule_name(self):
        return self["clothing_insulation_calculation_method_schedule_name"]

    @clothing_insulation_calculation_method_schedule_name.setter
    def clothing_insulation_calculation_method_schedule_name(self, value=None):
        self["clothing_insulation_calculation_method_schedule_name"] = value

    @property
    def thermal_comfort_model_3_type(self):
        return self["thermal_comfort_model_3_type"]

    @thermal_comfort_model_3_type.setter
    def thermal_comfort_model_3_type(self, value=None):
        self["thermal_comfort_model_3_type"] = value

    @property
    def work_efficiency_schedule_name(self):
        return self["work_efficiency_schedule_name"]

    @work_efficiency_schedule_name.setter
    def work_efficiency_schedule_name(self, value=None):
        self["work_efficiency_schedule_name"] = value

    @property
    def number_of_people_schedule_name(self):
        return self["number_of_people_schedule_name"]

    @number_of_people_schedule_name.setter
    def number_of_people_schedule_name(self, value=None):
        self["number_of_people_schedule_name"] = value

    @property
    def carbon_dioxide_generation_rate(self):
        return self["carbon_dioxide_generation_rate"]

    @carbon_dioxide_generation_rate.setter
    def carbon_dioxide_generation_rate(self, value=None):
        self["carbon_dioxide_generation_rate"] = value

    @property
    def thermal_comfort_model_1_type(self):
        return self["thermal_comfort_model_1_type"]

    @thermal_comfort_model_1_type.setter
    def thermal_comfort_model_1_type(self, value=None):
        self["thermal_comfort_model_1_type"] = value

    @property
    def number_of_people(self):
        return self["number_of_people"]

    @number_of_people.setter
    def number_of_people(self, value=None):
        self["number_of_people"] = value

    @property
    def number_of_people_calculation_method(self):
        return self["number_of_people_calculation_method"]

    @number_of_people_calculation_method.setter
    def number_of_people_calculation_method(self, value=None):
        self["number_of_people_calculation_method"] = value

    @property
    def air_velocity_schedule_name(self):
        return self["air_velocity_schedule_name"]

    @air_velocity_schedule_name.setter
    def air_velocity_schedule_name(self, value=None):
        self["air_velocity_schedule_name"] = value

    @property
    def activity_level_schedule_name(self):
        return self["activity_level_schedule_name"]

    @activity_level_schedule_name.setter
    def activity_level_schedule_name(self, value=None):
        self["activity_level_schedule_name"] = value




class Lights(BaseObject):
    """Corresponds to object `Lights`"""
    _schema = {
        'name': {
            'is_required': True,
            'type': 'string',
            'reference': ['LightsNames']},
        'min_fields': 11.0,
        'patternProperties': {
            '.*': {
                'required': [
                    'zone_or_zonelist_name',
                    'schedule_name'],
                'properties': {
                    'return_air_heat_gain_node_name': {
                        'type': 'string'},
                    'zone_or_zonelist_name': {
                        'type': 'string',
                        'object_list': ['ZoneAndZoneListNames'],
                                'data_type': 'object_list'},
                    'fraction_replaceable': {
                        'default': 1.0,
                        'minimum': 0.0,
                        'type': 'number',
                        'maximum': 1.0},
                    'watts_per_zone_floor_area': {
                        'units': 'W/m2',
                        'ip-units': 'W/ft2',
                        'minimum': 0.0,
                        'type': 'number'},
                    'watts_per_person': {
                        'units': 'W/person',
                        'ip-units': 'W/person',
                        'minimum': 0.0,
                        'type': 'number'},
                    'schedule_name': {
                        'type': 'string',
                        'object_list': ['ScheduleNames'],
                        'data_type': 'object_list'},
                    'return_air_fraction_function_of_plenum_temperature_coefficient_2': {
                        'units': '1/K',
                        'default': 0.0,
                        'minimum': 0.0,
                        'type': 'number'},
                    'return_air_fraction': {
                        'default': 0.0,
                        'minimum': 0.0,
                        'type': 'number',
                        'maximum': 1.0},
                    'fraction_visible': {
                        'default': 0.0,
                        'minimum': 0.0,
                        'type': 'number',
                        'maximum': 1.0},
                    'return_air_fraction_function_of_plenum_temperature_coefficient_1': {
                        'default': 0.0,
                        'minimum': 0.0,
                        'type': 'number'},
                    'design_level_calculation_method': {
                        'default': 'LightingLevel',
                        'enum': [
                            '',
                            'LightingLevel',
                            'Watts/Area',
                            'Watts/Person'],
                        'type': 'string'},
                    'return_air_fraction_calculated_from_plenum_temperature': {
                        'default': 'No',
                        'enum': [
                            '',
                            'No',
                            'Yes'],
                        'type': 'string'},
                    'end_use_subcategory': {
                        'retaincase': True,
                        'default': 'General',
                        'type': 'string'},
                    'lighting_level': {
                        'units': 'W',
                        'ip-units': 'W',
                        'minimum': 0.0,
                        'type': 'number'},
                    'fraction_radiant': {
                        'default': 0.0,
                        'minimum': 0.0,
                        'type': 'number',
                        'maximum': 1.0}},
                'type': 'object'}},
        'type': 'object'}

    @property
    def return_air_heat_gain_node_name(self):
        return self["return_air_heat_gain_node_name"]

    @return_air_heat_gain_node_name.setter
    def return_air_heat_gain_node_name(self, value=None):
        self["return_air_heat_gain_node_name"] = value

    @property
    def zone_or_zonelist_name(self):
        return self["zone_or_zonelist_name"]

    @zone_or_zonelist_name.setter
    def zone_or_zonelist_name(self, value=None):
        self["zone_or_zonelist_name"] = value

    @property
    def fraction_replaceable(self):
        return self["fraction_replaceable"]

    @fraction_replaceable.setter
    def fraction_replaceable(self, value=None):
        self["fraction_replaceable"] = value

    @property
    def watts_per_zone_floor_area(self):
        return self["watts_per_zone_floor_area"]

    @watts_per_zone_floor_area.setter
    def watts_per_zone_floor_area(self, value=None):
        self["watts_per_zone_floor_area"] = value

    @property
    def watts_per_person(self):
        return self["watts_per_person"]

    @watts_per_person.setter
    def watts_per_person(self, value=None):
        self["watts_per_person"] = value

    @property
    def schedule_name(self):
        return self["schedule_name"]

    @schedule_name.setter
    def schedule_name(self, value=None):
        self["schedule_name"] = value

    @property
    def return_air_fraction_function_of_plenum_temperature_coefficient_2(self):
        return self["return_air_fraction_function_of_plenum_temperature_coefficient_2"]

    @return_air_fraction_function_of_plenum_temperature_coefficient_2.setter
    def return_air_fraction_function_of_plenum_temperature_coefficient_2(
            self, value=None):
        self["return_air_fraction_function_of_plenum_temperature_coefficient_2"] = value

    @property
    def return_air_fraction(self):
        return self["return_air_fraction"]

    @return_air_fraction.setter
    def return_air_fraction(self, value=None):
        self["return_air_fraction"] = value

    @property
    def fraction_visible(self):
        return self["fraction_visible"]

    @fraction_visible.setter
    def fraction_visible(self, value=None):
        self["fraction_visible"] = value

    @property
    def return_air_fraction_function_of_plenum_temperature_coefficient_1(self):
        return self["return_air_fraction_function_of_plenum_temperature_coefficient_1"]

    @return_air_fraction_function_of_plenum_temperature_coefficient_1.setter
    def return_air_fraction_function_of_plenum_temperature_coefficient_1(
            self, value=None):
        self["return_air_fraction_function_of_plenum_temperature_coefficient_1"] = value

    @property
    def design_level_calculation_method(self):
        return self["design_level_calculation_method"]

    @design_level_calculation_method.setter
    def design_level_calculation_method(self, value=None):
        self["design_level_calculation_method"] = value

    @property
    def return_air_fraction_calculated_from_plenum_temperature(self):
        return self["return_air_fraction_calculated_from_plenum_temperature"]

    @return_air_fraction_calculated_from_plenum_temperature.setter
    def return_air_fraction_calculated_from_plenum_temperature(
            self, value=None):
        self["return_air_fraction_calculated_from_plenum_temperature"] = value

    @property
    def end_use_subcategory(self):
        return self["end_use_subcategory"]

    @end_use_subcategory.setter
    def end_use_subcategory(self, value=None):
        self["end_use_subcategory"] = value

    @property
    def lighting_level(self):
        return self["lighting_level"]

    @lighting_level.setter
    def lighting_level(self, value=None):
        self["lighting_level"] = value

    @property
    def fraction_radiant(self):
        return self["fraction_radiant"]

    @fraction_radiant.setter
    def fraction_radiant(self, value=None):
        self["fraction_radiant"] = value




class ElectricEquipment(BaseObject):
    """Corresponds to object `ElectricEquipment`"""
    _schema = {
        'name': {
            'is_required': True,
            'type': 'string',
            'reference': ['ElectricEquipmentNames']},
        'min_fields': 10.0,
        'patternProperties': {
            '.*': {
                'required': [
                    'zone_or_zonelist_name',
                    'schedule_name'],
                'properties': {
                    'zone_or_zonelist_name': {
                        'type': 'string',
                        'object_list': ['ZoneAndZoneListNames'],
                        'data_type': 'object_list'},
                    'watts_per_zone_floor_area': {
                        'units': 'W/m2',
                        'ip-units': 'W/ft2',
                        'minimum': 0.0,
                        'type': 'number'},
                    'watts_per_person': {
                        'units': 'W/person',
                        'ip-units': 'W/person',
                                    'minimum': 0.0,
                                    'type': 'number'},
                    'schedule_name': {
                        'type': 'string',
                        'object_list': ['ScheduleNames'],
                        'data_type': 'object_list'},
                    'design_level': {
                        'units': 'W',
                        'ip-units': 'W',
                        'minimum': 0.0,
                        'type': 'number'},
                    'design_level_calculation_method': {
                        'default': 'EquipmentLevel',
                        'enum': [
                            '',
                            'EquipmentLevel',
                            'Watts/Area',
                            'Watts/Person'],
                        'type': 'string'},
                    'fraction_lost': {
                        'default': 0.0,
                        'minimum': 0.0,
                        'type': 'number',
                        'maximum': 1.0},
                    'end_use_subcategory': {
                        'retaincase': True,
                        'default': 'General',
                        'type': 'string'},
                    'fraction_latent': {
                        'default': 0.0,
                        'minimum': 0.0,
                        'type': 'number',
                        'maximum': 1.0},
                    'fraction_radiant': {
                        'default': 0.0,
                        'minimum': 0.0,
                        'type': 'number',
                        'maximum': 1.0}},
                'type': 'object'}},
        'type': 'object'}

    @property
    def zone_or_zonelist_name(self):
        return self["zone_or_zonelist_name"]

    @zone_or_zonelist_name.setter
    def zone_or_zonelist_name(self, value=None):
        self["zone_or_zonelist_name"] = value

    @property
    def watts_per_zone_floor_area(self):
        return self["watts_per_zone_floor_area"]

    @watts_per_zone_floor_area.setter
    def watts_per_zone_floor_area(self, value=None):
        self["watts_per_zone_floor_area"] = value

    @property
    def watts_per_person(self):
        return self["watts_per_person"]

    @watts_per_person.setter
    def watts_per_person(self, value=None):
        self["watts_per_person"] = value

    @property
    def schedule_name(self):
        return self["schedule_name"]

    @schedule_name.setter
    def schedule_name(self, value=None):
        self["schedule_name"] = value

    @property
    def design_level(self):
        return self["design_level"]

    @design_level.setter
    def design_level(self, value=None):
        self["design_level"] = value

    @property
    def design_level_calculation_method(self):
        return self["design_level_calculation_method"]

    @design_level_calculation_method.setter
    def design_level_calculation_method(self, value=None):
        self["design_level_calculation_method"] = value

    @property
    def fraction_lost(self):
        return self["fraction_lost"]

    @fraction_lost.setter
    def fraction_lost(self, value=None):
        self["fraction_lost"] = value

    @property
    def end_use_subcategory(self):
        return self["end_use_subcategory"]

    @end_use_subcategory.setter
    def end_use_subcategory(self, value=None):
        self["end_use_subcategory"] = value

    @property
    def fraction_latent(self):
        return self["fraction_latent"]

    @fraction_latent.setter
    def fraction_latent(self, value=None):
        self["fraction_latent"] = value

    @property
    def fraction_radiant(self):
        return self["fraction_radiant"]

    @fraction_radiant.setter
    def fraction_radiant(self, value=None):
        self["fraction_radiant"] = value


