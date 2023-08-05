""" Data objects in group "zone" """
from design_nest.eplus_components.helper import BaseObject



class BuildingSurfaceDetailed(BaseObject):
    """Corresponds to object `BuildingSurface:Detailed`"""
    _schema = {
        'extensible_size': 3.0,
        'name': {
            'is_required': True,
            'type': 'string',
            'reference': [
                'AllHeatTranAngFacNames',
                'AllHeatTranSurfNames',
                'AllShadingAndHTSurfNames',
                'FloorSurfaceNames',
                'OutFaceEnvNames',
                'RadiantSurfaceNames',
                'SurfAndSubSurfNames',
                'SurfaceNames']},
        'format': 'vertices',
        'min_fields': 19.0,
        'patternProperties': {
            '.*': {
                'required': [
                    'surface_type',
                    'construction_name',
                    'zone_name',
                    'outside_boundary_condition'],
                'type': 'object',
                'properties': {
                    'surface_type': {
                        'type': 'string',
                                'enum': [
                                    'Ceiling',
                                    'Floor',
                                    'Roof',
                                    'Wall']},
                        'number_of_vertices': {
                                'default': 'Autocalculate',
                                'anyOf': [
                                    {
                                        'minimum': 3.0,
                                        'type': 'number'},
                                    {
                                        'enum': [
                                            '',
                                            'Autocalculate'],
                                        'type': 'string'}]},
                        'outside_boundary_condition_object': {
                                'object_list': ['OutFaceEnvNames'],
                                'type': 'string',
                                'data_type': 'object_list'},
                        'construction_name': {
                        'type': 'string',
                                'object_list': ['ConstructionNames'],
                                'data_type': 'object_list'},
                        'wind_exposure': {
                        'default': 'WindExposed',
                        'enum': [
                            '',
                            'NoWind',
                            'WindExposed'],
                        'type': 'string'},
                    'vertices': {
                        'items': {
                            'required': [
                                'vertex_x_coordinate',
                                'vertex_y_coordinate',
                                'vertex_z_coordinate'],
                            'type': 'object',
                                    'properties': {
                                        'vertex_y_coordinate': {
                                            'units': 'm',
                                            'type': 'number'},
                                        'vertex_z_coordinate': {
                                            'units': 'm',
                                            'type': 'number'},
                                        'vertex_x_coordinate': {
                                            'units': 'm',
                                            'type': 'number'}}},
                        'type': 'array'},
                    'view_factor_to_ground': {
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
                        'zone_name': {
                        'type': 'string',
                                'object_list': ['ZoneNames'],
                                'data_type': 'object_list'},
                        'sun_exposure': {
                        'default': 'SunExposed',
                        'enum': [
                            '',
                            'NoSun',
                            'SunExposed'],
                        'type': 'string'},
                    'outside_boundary_condition': {
                        'type': 'string',
                                'enum': [
                                    'Adiabatic',
                                    'Foundation',
                                    'Ground',
                                    'GroundBasementPreprocessorAverageFloor',
                                    'GroundBasementPreprocessorAverageWall',
                                    'GroundBasementPreprocessorLowerWall',
                                    'GroundBasementPreprocessorUpperWall',
                                    'GroundFCfactorMethod',
                                    'GroundSlabPreprocessorAverage',
                                    'GroundSlabPreprocessorCore',
                                    'GroundSlabPreprocessorPerimeter',
                                    'OtherSideCoefficients',
                                    'OtherSideConditionsModel',
                                    'Outdoors',
                                    'Surface',
                                    'Zone']}}}},
        'type': 'object'}

    @property
    def surface_type(self):
        return self["surface_type"]

    @surface_type.setter
    def surface_type(self, value=None):
        self["surface_type"] = value

    @property
    def number_of_vertices(self):
        return self["number_of_vertices"]

    @number_of_vertices.setter
    def number_of_vertices(self, value=None):
        self["number_of_vertices"] = value

    @property
    def outside_boundary_condition_object(self):
        return self["outside_boundary_condition_object"]

    @outside_boundary_condition_object.setter
    def outside_boundary_condition_object(self, value=None):
        self["outside_boundary_condition_object"] = value

    @property
    def construction_name(self):
        return self["construction_name"]

    @construction_name.setter
    def construction_name(self, value=None):
        self["construction_name"] = value

    @property
    def wind_exposure(self):
        return self["wind_exposure"]

    @wind_exposure.setter
    def wind_exposure(self, value=None):
        self["wind_exposure"] = value

    @property
    def vertices(self):
        return self["vertices"]

    @vertices.setter
    def vertices(self, value=None):
        self["vertices"] = value

    @property
    def view_factor_to_ground(self):
        return self["view_factor_to_ground"]

    @view_factor_to_ground.setter
    def view_factor_to_ground(self, value=None):
        self["view_factor_to_ground"] = value

    @property
    def zone_name(self):
        return self["zone_name"]

    @zone_name.setter
    def zone_name(self, value=None):
        self["zone_name"] = value

    @property
    def sun_exposure(self):
        return self["sun_exposure"]

    @sun_exposure.setter
    def sun_exposure(self, value=None):
        self["sun_exposure"] = value

    @property
    def outside_boundary_condition(self):
        return self["outside_boundary_condition"]

    @outside_boundary_condition.setter
    def outside_boundary_condition(self, value=None):
        self["outside_boundary_condition"] = value


