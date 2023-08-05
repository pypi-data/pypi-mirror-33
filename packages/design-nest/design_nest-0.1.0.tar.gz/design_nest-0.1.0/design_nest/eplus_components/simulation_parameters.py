""" Data objects in group "simulation_parameters" """
from design_nest.eplus_components.helper import BaseObject



class Version(BaseObject):
    """Corresponds to object `Version`"""
    _schema = {
        'format': 'singleLine',
        'patternProperties': {
            '.*': {
                'type': 'object',
                'properties': {
                    'version_identifier': {
                        'default': '8.9',
                        'type': 'string'}}}},
        'maxProperties': 1,
        'type': 'object'}

    @property
    def version_identifier(self):
        return self["version_identifier"]

    @version_identifier.setter
    def version_identifier(self, value=None):
        self["version_identifier"] = value




class SimulationControl(BaseObject):
    """Corresponds to object `SimulationControl`"""
    _schema = {
        'min_fields': 5.0, 'patternProperties': {
            '.*': {
                'properties': {
                    'run_simulation_for_sizing_periods': {
                        'default': 'Yes', 'enum': [
                            '', 'No', 'Yes'], 'type': 'string'}, 'run_simulation_for_weather_file_run_periods': {
                        'default': 'Yes', 'enum': [
                            '', 'No', 'Yes'], 'type': 'string'}, 'maximum_number_of_hvac_sizing_simulation_passes': {
                        'default': 1.0, 'minimum': 1.0, 'type': 'number'}, 'do_system_sizing_calculation': {
                        'default': 'No', 'enum': [
                            '', 'No', 'Yes'], 'type': 'string'}, 'do_hvac_sizing_simulation_for_sizing_periods': {
                        'default': 'No', 'enum': [
                            '', 'No', 'Yes'], 'type': 'string'}, 'do_zone_sizing_calculation': {
                        'default': 'No', 'enum': [
                            '', 'No', 'Yes'], 'type': 'string'}, 'do_plant_sizing_calculation': {
                        'default': 'No', 'enum': [
                            '', 'No', 'Yes'], 'type': 'string'}}, 'type': 'object'}}, 'maxProperties': 1, 'type': 'object'}

    @property
    def run_simulation_for_sizing_periods(self):
        return self["run_simulation_for_sizing_periods"]

    @run_simulation_for_sizing_periods.setter
    def run_simulation_for_sizing_periods(self, value=None):
        self["run_simulation_for_sizing_periods"] = value

    @property
    def run_simulation_for_weather_file_run_periods(self):
        return self["run_simulation_for_weather_file_run_periods"]

    @run_simulation_for_weather_file_run_periods.setter
    def run_simulation_for_weather_file_run_periods(self, value=None):
        self["run_simulation_for_weather_file_run_periods"] = value

    @property
    def maximum_number_of_hvac_sizing_simulation_passes(self):
        return self["maximum_number_of_hvac_sizing_simulation_passes"]

    @maximum_number_of_hvac_sizing_simulation_passes.setter
    def maximum_number_of_hvac_sizing_simulation_passes(self, value=None):
        self["maximum_number_of_hvac_sizing_simulation_passes"] = value

    @property
    def do_system_sizing_calculation(self):
        return self["do_system_sizing_calculation"]

    @do_system_sizing_calculation.setter
    def do_system_sizing_calculation(self, value=None):
        self["do_system_sizing_calculation"] = value

    @property
    def do_hvac_sizing_simulation_for_sizing_periods(self):
        return self["do_hvac_sizing_simulation_for_sizing_periods"]

    @do_hvac_sizing_simulation_for_sizing_periods.setter
    def do_hvac_sizing_simulation_for_sizing_periods(self, value=None):
        self["do_hvac_sizing_simulation_for_sizing_periods"] = value

    @property
    def do_zone_sizing_calculation(self):
        return self["do_zone_sizing_calculation"]

    @do_zone_sizing_calculation.setter
    def do_zone_sizing_calculation(self, value=None):
        self["do_zone_sizing_calculation"] = value

    @property
    def do_plant_sizing_calculation(self):
        return self["do_plant_sizing_calculation"]

    @do_plant_sizing_calculation.setter
    def do_plant_sizing_calculation(self, value=None):
        self["do_plant_sizing_calculation"] = value




class GlobalGeometryRules(BaseObject):
    """Corresponds to object `GlobalGeometryRules`"""
    _schema = {
        'patternProperties': {
            '.*': {
                'required': [
                    'starting_vertex_position',
                    'vertex_entry_direction',
                    'coordinate_system'],
                'type': 'object',
                'properties': {
                    'daylighting_reference_point_coordinate_system': {
                        'default': 'Relative',
                        'enum': [
                            '',
                            'Absolute',
                            'Relative',
                            'World'],
                        'type': 'string'},
                    'rectangular_surface_coordinate_system': {
                        'default': 'Relative',
                        'enum': [
                            '',
                            'Absolute',
                            'Relative',
                            'World'],
                        'type': 'string'},
                    'coordinate_system': {
                        'type': 'string'},
                    'starting_vertex_position': {
                        'type': 'string'},
                    'vertex_entry_direction': {
                        'type': 'string'}}}},
        'maxProperties': 1,
        'minProperties': 1,
        'type': 'object'}

    @property
    def daylighting_reference_point_coordinate_system(self):
        return self["daylighting_reference_point_coordinate_system"]

    @daylighting_reference_point_coordinate_system.setter
    def daylighting_reference_point_coordinate_system(self, value=None):
        self["daylighting_reference_point_coordinate_system"] = value

    @property
    def rectangular_surface_coordinate_system(self):
        return self["rectangular_surface_coordinate_system"]

    @rectangular_surface_coordinate_system.setter
    def rectangular_surface_coordinate_system(self, value=None):
        self["rectangular_surface_coordinate_system"] = value

    @property
    def coordinate_system(self):
        return self["coordinate_system"]

    @coordinate_system.setter
    def coordinate_system(self, value=None):
        self["coordinate_system"] = value

    @property
    def starting_vertex_position(self):
        return self["starting_vertex_position"]

    @starting_vertex_position.setter
    def starting_vertex_position(self, value=None):
        self["starting_vertex_position"] = value

    @property
    def vertex_entry_direction(self):
        return self["vertex_entry_direction"]

    @vertex_entry_direction.setter
    def vertex_entry_direction(self, value=None):
        self["vertex_entry_direction"] = value




class HeatBalanceAlgorithm(BaseObject):
    """Corresponds to object `HeatBalanceAlgorithm`"""
    _schema = {
        'format': 'singleLine',
        'patternProperties': {
            '.*': {
                'type': 'object',
                'properties': {
                    'surface_temperature_upper_limit': {
                        'default': 200.0,
                        'units': 'C',
                        'minimum': 200.0,
                        'type': 'number'},
                    'minimum_surface_convection_heat_transfer_coefficient_value': {
                        'units': 'W/m2-K',
                        'default': 0.1,
                        'minimum': 0.0,
                        'type': 'number',
                        'exclusiveMinimum': True},
                    'maximum_surface_convection_heat_transfer_coefficient_value': {
                        'units': 'W/m2-K',
                        'default': 1000.0,
                        'minimum': 1.0,
                        'type': 'number'},
                    'algorithm': {
                        'default': 'ConductionTransferFunction',
                        'enum': [
                            '',
                            'CombinedHeatAndMoistureFiniteElement',
                            'ConductionFiniteDifference',
                            'ConductionTransferFunction',
                            'MoisturePenetrationDepthConductionTransferFunction'],
                        'type': 'string'}}}},
        'maxProperties': 1,
        'type': 'object'}

    @property
    def surface_temperature_upper_limit(self):
        return self["surface_temperature_upper_limit"]

    @surface_temperature_upper_limit.setter
    def surface_temperature_upper_limit(self, value=None):
        self["surface_temperature_upper_limit"] = value

    @property
    def minimum_surface_convection_heat_transfer_coefficient_value(self):
        return self["minimum_surface_convection_heat_transfer_coefficient_value"]

    @minimum_surface_convection_heat_transfer_coefficient_value.setter
    def minimum_surface_convection_heat_transfer_coefficient_value(
            self, value=None):
        self["minimum_surface_convection_heat_transfer_coefficient_value"] = value

    @property
    def maximum_surface_convection_heat_transfer_coefficient_value(self):
        return self["maximum_surface_convection_heat_transfer_coefficient_value"]

    @maximum_surface_convection_heat_transfer_coefficient_value.setter
    def maximum_surface_convection_heat_transfer_coefficient_value(
            self, value=None):
        self["maximum_surface_convection_heat_transfer_coefficient_value"] = value

    @property
    def algorithm(self):
        return self["algorithm"]

    @algorithm.setter
    def algorithm(self, value=None):
        self["algorithm"] = value


