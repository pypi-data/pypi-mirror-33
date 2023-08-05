""" Data objects in group "construction" """
from design_nest.eplus_components.helper import BaseObject



class Material(BaseObject):
    """Corresponds to object `Material`"""
    _schema = {
        'name': {
            'is_required': True,
            'type': 'string',
            'reference': ['MaterialName']},
        'min_fields': 6.0,
        'patternProperties': {
            '.*': {
                'required': [
                    'roughness',
                    'thickness',
                    'conductivity',
                    'density',
                    'specific_heat'],
                'properties': {
                    'density': {
                        'units': 'kg/m3',
                        'minimum': 0.0,
                        'type': 'number',
                        'exclusiveMinimum': True},
                    'solar_absorptance': {
                        'default': 0.7,
                        'minimum': 0.0,
                        'type': 'number',
                                'maximum': 1.0},
                    'specific_heat': {
                        'units': 'J/kg-K',
                        'minimum': 100.0,
                        'type': 'number'},
                    'visible_absorptance': {
                        'default': 0.7,
                        'minimum': 0.0,
                        'type': 'number',
                        'maximum': 1.0},
                    'thickness': {
                        'exclusiveMinimum': True,
                        'ip-units': 'in',
                        'minimum': 0.0,
                        'units': 'm',
                        'type': 'number'},
                    'thermal_absorptance': {
                        'default': 0.9,
                        'exclusiveMinimum': True,
                        'minimum': 0.0,
                        'type': 'number',
                        'maximum': 0.99999},
                    'roughness': {
                        'type': 'string',
                        'enum': [
                            'MediumRough',
                            'MediumSmooth',
                            'Rough',
                            'Smooth',
                            'VeryRough',
                            'VerySmooth']},
                    'conductivity': {
                        'units': 'W/m-K',
                        'minimum': 0.0,
                        'type': 'number',
                        'exclusiveMinimum': True}},
                'type': 'object'}},
        'type': 'object'}

    @property
    def density(self):
        return self["density"]

    @density.setter
    def density(self, value=None):
        self["density"] = value

    @property
    def solar_absorptance(self):
        return self["solar_absorptance"]

    @solar_absorptance.setter
    def solar_absorptance(self, value=None):
        self["solar_absorptance"] = value

    @property
    def specific_heat(self):
        return self["specific_heat"]

    @specific_heat.setter
    def specific_heat(self, value=None):
        self["specific_heat"] = value

    @property
    def visible_absorptance(self):
        return self["visible_absorptance"]

    @visible_absorptance.setter
    def visible_absorptance(self, value=None):
        self["visible_absorptance"] = value

    @property
    def thickness(self):
        return self["thickness"]

    @thickness.setter
    def thickness(self, value=None):
        self["thickness"] = value

    @property
    def thermal_absorptance(self):
        return self["thermal_absorptance"]

    @thermal_absorptance.setter
    def thermal_absorptance(self, value=None):
        self["thermal_absorptance"] = value

    @property
    def roughness(self):
        return self["roughness"]

    @roughness.setter
    def roughness(self, value=None):
        self["roughness"] = value

    @property
    def conductivity(self):
        return self["conductivity"]

    @conductivity.setter
    def conductivity(self, value=None):
        self["conductivity"] = value




class MaterialNoMass(BaseObject):
    """Corresponds to object `Material:NoMass`"""
    _schema = {
        'name': {
            'is_required': True,
            'type': 'string',
            'reference': ['MaterialName']},
        'min_fields': 3.0,
        'patternProperties': {
            '.*': {
                'required': [
                    'roughness',
                    'thermal_resistance'],
                'properties': {
                    'thermal_absorptance': {
                        'default': 0.9,
                        'exclusiveMinimum': True,
                        'minimum': 0.0,
                        'type': 'number',
                        'maximum': 0.99999},
                    'solar_absorptance': {
                        'default': 0.7,
                        'minimum': 0.0,
                        'type': 'number',
                                'maximum': 1.0},
                    'thermal_resistance': {
                        'units': 'm2-K/W',
                        'minimum': 0.001,
                        'type': 'number'},
                    'visible_absorptance': {
                        'default': 0.7,
                        'minimum': 0.0,
                        'type': 'number',
                        'maximum': 1.0},
                    'roughness': {
                        'type': 'string',
                        'enum': [
                            'MediumRough',
                            'MediumSmooth',
                            'Rough',
                            'Smooth',
                            'VeryRough',
                            'VerySmooth']}},
                'type': 'object'}},
        'type': 'object'}

    @property
    def thermal_absorptance(self):
        return self["thermal_absorptance"]

    @thermal_absorptance.setter
    def thermal_absorptance(self, value=None):
        self["thermal_absorptance"] = value

    @property
    def solar_absorptance(self):
        return self["solar_absorptance"]

    @solar_absorptance.setter
    def solar_absorptance(self, value=None):
        self["solar_absorptance"] = value

    @property
    def thermal_resistance(self):
        return self["thermal_resistance"]

    @thermal_resistance.setter
    def thermal_resistance(self, value=None):
        self["thermal_resistance"] = value

    @property
    def visible_absorptance(self):
        return self["visible_absorptance"]

    @visible_absorptance.setter
    def visible_absorptance(self, value=None):
        self["visible_absorptance"] = value

    @property
    def roughness(self):
        return self["roughness"]

    @roughness.setter
    def roughness(self, value=None):
        self["roughness"] = value




class MaterialAirGap(BaseObject):
    """Corresponds to object `Material:AirGap`"""
    _schema = {
        'name': {
            'is_required': True,
            'type': 'string',
            'reference': ['MaterialName']},
        'min_fields': 2.0,
        'patternProperties': {
            '.*': {
                'required': ['thermal_resistance'],
                'type': 'object',
                'properties': {
                    'thermal_resistance': {
                        'units': 'm2-K/W',
                        'minimum': 0.0,
                        'type': 'number',
                        'exclusiveMinimum': True}}}},
        'type': 'object'}

    @property
    def thermal_resistance(self):
        return self["thermal_resistance"]

    @thermal_resistance.setter
    def thermal_resistance(self, value=None):
        self["thermal_resistance"] = value




class WindowMaterialSimpleGlazingSystem(BaseObject):
    """Corresponds to object `WindowMaterial:SimpleGlazingSystem`"""
    _schema = {
        'name': {
            'is_required': True,
            'type': 'string',
            'reference': [
                'GlazingMaterialName',
                'MaterialName']},
        'min_fields': 3.0,
        'patternProperties': {
            '.*': {
                'required': [
                    'u_factor',
                    'solar_heat_gain_coefficient'],
                'type': 'object',
                'properties': {
                    'u_factor': {
                        'exclusiveMinimum': True,
                        'maximum': 7.0,
                        'minimum': 0.0,
                        'units': 'W/m2-K',
                        'type': 'number'},
                    'visible_transmittance': {
                        'exclusiveMaximum': True,
                        'type': 'number',
                                'maximum': 1.0,
                                'minimum': 0.0,
                                'exclusiveMinimum': True},
                        'solar_heat_gain_coefficient': {
                        'exclusiveMaximum': True,
                        'exclusiveMinimum': True,
                        'maximum': 1.0,
                        'minimum': 0.0,
                        'type': 'number'}}}},
        'type': 'object'}

    @property
    def u_factor(self):
        return self["u_factor"]

    @u_factor.setter
    def u_factor(self, value=None):
        self["u_factor"] = value

    @property
    def visible_transmittance(self):
        return self["visible_transmittance"]

    @visible_transmittance.setter
    def visible_transmittance(self, value=None):
        self["visible_transmittance"] = value

    @property
    def solar_heat_gain_coefficient(self):
        return self["solar_heat_gain_coefficient"]

    @solar_heat_gain_coefficient.setter
    def solar_heat_gain_coefficient(self, value=None):
        self["solar_heat_gain_coefficient"] = value




class WindowMaterialGlazing(BaseObject):
    """Corresponds to object `WindowMaterial:Glazing`"""
    _schema = {
        'name': {
            'is_required': True,
            'type': 'string',
            'reference': [
                'CFSGlazingName',
                'GlazingMaterialName',
                'MaterialName']},
        'min_fields': 14.0,
        'patternProperties': {
            '.*': {
                'required': [
                    'optical_data_type',
                    'thickness'],
                'type': 'object',
                'properties': {
                    'front_side_solar_reflectance_at_normal_incidence': {
                        'minimum': 0.0,
                        'type': 'number',
                                'maximum': 1.0},
                        'back_side_solar_reflectance_at_normal_incidence': {
                        'minimum': 0.0,
                        'type': 'number',
                                'maximum': 1.0},
                        'window_glass_spectral_and_incident_angle_transmittance_data_set_table_name': {
                        'object_list': ['BiVariateTables'],
                        'type': 'string',
                        'data_type': 'object_list'},
                    'front_side_visible_reflectance_at_normal_incidence': {
                        'minimum': 0.0,
                        'type': 'number',
                                'maximum': 1.0},
                        'optical_data_type': {
                        'type': 'string',
                                'enum': [
                                    'BSDF',
                                    'Spectral',
                                    'SpectralAndAngle',
                                    'SpectralAverage']},
                        'back_side_visible_reflectance_at_normal_incidence': {
                                'minimum': 0.0,
                                'type': 'number',
                                'maximum': 1.0},
                        'window_glass_spectral_and_incident_angle_back_reflectance_data_set_table_name': {
                        'object_list': ['BiVariateTables'],
                        'type': 'string',
                                'data_type': 'object_list'},
                        'back_side_infrared_hemispherical_emissivity': {
                        'exclusiveMaximum': True,
                        'default': 0.84,
                        'type': 'number',
                                'maximum': 1.0,
                                'minimum': 0.0,
                        'exclusiveMinimum': True},
                    'thickness': {
                        'exclusiveMinimum': True,
                        'ip-units': 'in',
                        'minimum': 0.0,
                        'units': 'm',
                        'type': 'number'},
                    'infrared_transmittance_at_normal_incidence': {
                        'default': 0.0,
                        'minimum': 0.0,
                        'type': 'number',
                                'maximum': 1.0},
                        'visible_transmittance_at_normal_incidence': {
                        'minimum': 0.0,
                        'type': 'number',
                                'maximum': 1.0},
                        'young_s_modulus': {
                        'default': 72000000000.0,
                        'exclusiveMinimum': True,
                        'minimum': 0.0,
                        'units': 'Pa',
                        'type': 'number'},
                    'solar_diffusing': {
                        'default': 'No',
                        'enum': [
                            '',
                            'No',
                            'Yes'],
                        'type': 'string'},
                    'front_side_infrared_hemispherical_emissivity': {
                        'exclusiveMaximum': True,
                        'default': 0.84,
                        'type': 'number',
                                'maximum': 1.0,
                                'minimum': 0.0,
                        'exclusiveMinimum': True},
                    'poisson_s_ratio': {
                        'exclusiveMaximum': True,
                        'default': 0.22,
                        'type': 'number',
                                'maximum': 1.0,
                                'minimum': 0.0,
                        'exclusiveMinimum': True},
                    'solar_transmittance_at_normal_incidence': {
                        'minimum': 0.0,
                        'type': 'number',
                                'maximum': 1.0},
                        'window_glass_spectral_data_set_name': {
                        'object_list': ['SpectralDataSets'],
                        'type': 'string',
                                'data_type': 'object_list'},
                        'dirt_correction_factor_for_solar_and_visible_transmittance': {
                        'default': 1.0,
                        'exclusiveMinimum': True,
                        'minimum': 0.0,
                        'type': 'number',
                                'maximum': 1.0},
                        'window_glass_spectral_and_incident_angle_front_reflectance_data_set_table_name': {
                        'object_list': ['BiVariateTables'],
                        'type': 'string',
                                'data_type': 'object_list'},
                        'conductivity': {
                        'units': 'W/m-K',
                        'exclusiveMinimum': True,
                        'default': 0.9,
                        'minimum': 0.0,
                        'type': 'number'}}}},
        'type': 'object'}

    @property
    def front_side_solar_reflectance_at_normal_incidence(self):
        return self["front_side_solar_reflectance_at_normal_incidence"]

    @front_side_solar_reflectance_at_normal_incidence.setter
    def front_side_solar_reflectance_at_normal_incidence(self, value=None):
        self["front_side_solar_reflectance_at_normal_incidence"] = value

    @property
    def back_side_solar_reflectance_at_normal_incidence(self):
        return self["back_side_solar_reflectance_at_normal_incidence"]

    @back_side_solar_reflectance_at_normal_incidence.setter
    def back_side_solar_reflectance_at_normal_incidence(self, value=None):
        self["back_side_solar_reflectance_at_normal_incidence"] = value

    @property
    def window_glass_spectral_and_incident_angle_transmittance_data_set_table_name(
            self):
        return self["window_glass_spectral_and_incident_angle_transmittance_data_set_table_name"]

    @window_glass_spectral_and_incident_angle_transmittance_data_set_table_name.setter
    def window_glass_spectral_and_incident_angle_transmittance_data_set_table_name(
            self, value=None):
        self["window_glass_spectral_and_incident_angle_transmittance_data_set_table_name"] = value

    @property
    def front_side_visible_reflectance_at_normal_incidence(self):
        return self["front_side_visible_reflectance_at_normal_incidence"]

    @front_side_visible_reflectance_at_normal_incidence.setter
    def front_side_visible_reflectance_at_normal_incidence(self, value=None):
        self["front_side_visible_reflectance_at_normal_incidence"] = value

    @property
    def optical_data_type(self):
        return self["optical_data_type"]

    @optical_data_type.setter
    def optical_data_type(self, value=None):
        self["optical_data_type"] = value

    @property
    def back_side_visible_reflectance_at_normal_incidence(self):
        return self["back_side_visible_reflectance_at_normal_incidence"]

    @back_side_visible_reflectance_at_normal_incidence.setter
    def back_side_visible_reflectance_at_normal_incidence(self, value=None):
        self["back_side_visible_reflectance_at_normal_incidence"] = value

    @property
    def window_glass_spectral_and_incident_angle_back_reflectance_data_set_table_name(
            self):
        return self["window_glass_spectral_and_incident_angle_back_reflectance_data_set_table_name"]

    @window_glass_spectral_and_incident_angle_back_reflectance_data_set_table_name.setter
    def window_glass_spectral_and_incident_angle_back_reflectance_data_set_table_name(
            self, value=None):
        self["window_glass_spectral_and_incident_angle_back_reflectance_data_set_table_name"] = value

    @property
    def back_side_infrared_hemispherical_emissivity(self):
        return self["back_side_infrared_hemispherical_emissivity"]

    @back_side_infrared_hemispherical_emissivity.setter
    def back_side_infrared_hemispherical_emissivity(self, value=None):
        self["back_side_infrared_hemispherical_emissivity"] = value

    @property
    def thickness(self):
        return self["thickness"]

    @thickness.setter
    def thickness(self, value=None):
        self["thickness"] = value

    @property
    def infrared_transmittance_at_normal_incidence(self):
        return self["infrared_transmittance_at_normal_incidence"]

    @infrared_transmittance_at_normal_incidence.setter
    def infrared_transmittance_at_normal_incidence(self, value=None):
        self["infrared_transmittance_at_normal_incidence"] = value

    @property
    def visible_transmittance_at_normal_incidence(self):
        return self["visible_transmittance_at_normal_incidence"]

    @visible_transmittance_at_normal_incidence.setter
    def visible_transmittance_at_normal_incidence(self, value=None):
        self["visible_transmittance_at_normal_incidence"] = value

    @property
    def young_s_modulus(self):
        return self["young_s_modulus"]

    @young_s_modulus.setter
    def young_s_modulus(self, value=None):
        self["young_s_modulus"] = value

    @property
    def solar_diffusing(self):
        return self["solar_diffusing"]

    @solar_diffusing.setter
    def solar_diffusing(self, value=None):
        self["solar_diffusing"] = value

    @property
    def front_side_infrared_hemispherical_emissivity(self):
        return self["front_side_infrared_hemispherical_emissivity"]

    @front_side_infrared_hemispherical_emissivity.setter
    def front_side_infrared_hemispherical_emissivity(self, value=None):
        self["front_side_infrared_hemispherical_emissivity"] = value

    @property
    def poisson_s_ratio(self):
        return self["poisson_s_ratio"]

    @poisson_s_ratio.setter
    def poisson_s_ratio(self, value=None):
        self["poisson_s_ratio"] = value

    @property
    def solar_transmittance_at_normal_incidence(self):
        return self["solar_transmittance_at_normal_incidence"]

    @solar_transmittance_at_normal_incidence.setter
    def solar_transmittance_at_normal_incidence(self, value=None):
        self["solar_transmittance_at_normal_incidence"] = value

    @property
    def window_glass_spectral_data_set_name(self):
        return self["window_glass_spectral_data_set_name"]

    @window_glass_spectral_data_set_name.setter
    def window_glass_spectral_data_set_name(self, value=None):
        self["window_glass_spectral_data_set_name"] = value

    @property
    def dirt_correction_factor_for_solar_and_visible_transmittance(self):
        return self["dirt_correction_factor_for_solar_and_visible_transmittance"]

    @dirt_correction_factor_for_solar_and_visible_transmittance.setter
    def dirt_correction_factor_for_solar_and_visible_transmittance(
            self, value=None):
        self["dirt_correction_factor_for_solar_and_visible_transmittance"] = value

    @property
    def window_glass_spectral_and_incident_angle_front_reflectance_data_set_table_name(
            self):
        return self["window_glass_spectral_and_incident_angle_front_reflectance_data_set_table_name"]

    @window_glass_spectral_and_incident_angle_front_reflectance_data_set_table_name.setter
    def window_glass_spectral_and_incident_angle_front_reflectance_data_set_table_name(
            self, value=None):
        self["window_glass_spectral_and_incident_angle_front_reflectance_data_set_table_name"] = value

    @property
    def conductivity(self):
        return self["conductivity"]

    @conductivity.setter
    def conductivity(self, value=None):
        self["conductivity"] = value




class WindowMaterialGas(BaseObject):
    """Corresponds to object `WindowMaterial:Gas`"""
    _schema = {
        'name': {
            'is_required': True,
            'type': 'string',
            'reference': [
                'MaterialName',
                'WindowGasAndGasMixtures']},
        'min_fields': 3.0,
        'patternProperties': {
            '.*': {
                'required': [
                    'gas_type',
                    'thickness'],
                'properties': {
                    'specific_heat_ratio': {
                        'exclusiveMinimum': True,
                        'minimum': 1.0,
                        'type': 'number'},
                    'gas_type': {
                        'type': 'string',
                        'enum': [
                                'Air',
                                'Argon',
                                'Custom',
                                'Krypton',
                                'Xenon']},
                        'molecular_weight': {
                            'units': 'g/mol',
                            'minimum': 20.0,
                            'type': 'number',
                            'maximum': 200.0},
                        'thickness': {
                            'exclusiveMinimum': True,
                            'ip-units': 'in',
                            'minimum': 0.0,
                            'units': 'm',
                            'type': 'number'},
                        'specific_heat_coefficient_a': {
                        'units': 'J/kg-K',
                            'minimum': 0.0,
                            'type': 'number',
                            'exclusiveMinimum': True},
                        'specific_heat_coefficient_c': {
                            'units': 'J/kg-K3',
                            'type': 'number'},
                        'specific_heat_coefficient_b': {
                            'units': 'J/kg-K2',
                            'type': 'number'},
                        'conductivity_coefficient_b': {
                            'units': 'W/m-K2',
                            'type': 'number'},
                        'conductivity_coefficient_c': {
                            'units': 'W/m-K3',
                            'type': 'number'},
                        'conductivity_coefficient_a': {
                            'units': 'W/m-K',
                            'type': 'number'},
                        'viscosity_coefficient_a': {
                            'units': 'kg/m-s',
                            'minimum': 0.0,
                            'type': 'number',
                            'exclusiveMinimum': True},
                        'viscosity_coefficient_c': {
                            'units': 'kg/m-s-K2',
                            'type': 'number'},
                        'viscosity_coefficient_b': {
                            'units': 'kg/m-s-K',
                            'type': 'number'}},
                    'type': 'object'}},
        'type': 'object'}

    @property
    def specific_heat_ratio(self):
        return self["specific_heat_ratio"]

    @specific_heat_ratio.setter
    def specific_heat_ratio(self, value=None):
        self["specific_heat_ratio"] = value

    @property
    def gas_type(self):
        return self["gas_type"]

    @gas_type.setter
    def gas_type(self, value=None):
        self["gas_type"] = value

    @property
    def molecular_weight(self):
        return self["molecular_weight"]

    @molecular_weight.setter
    def molecular_weight(self, value=None):
        self["molecular_weight"] = value

    @property
    def thickness(self):
        return self["thickness"]

    @thickness.setter
    def thickness(self, value=None):
        self["thickness"] = value

    @property
    def specific_heat_coefficient_a(self):
        return self["specific_heat_coefficient_a"]

    @specific_heat_coefficient_a.setter
    def specific_heat_coefficient_a(self, value=None):
        self["specific_heat_coefficient_a"] = value

    @property
    def specific_heat_coefficient_c(self):
        return self["specific_heat_coefficient_c"]

    @specific_heat_coefficient_c.setter
    def specific_heat_coefficient_c(self, value=None):
        self["specific_heat_coefficient_c"] = value

    @property
    def specific_heat_coefficient_b(self):
        return self["specific_heat_coefficient_b"]

    @specific_heat_coefficient_b.setter
    def specific_heat_coefficient_b(self, value=None):
        self["specific_heat_coefficient_b"] = value

    @property
    def conductivity_coefficient_b(self):
        return self["conductivity_coefficient_b"]

    @conductivity_coefficient_b.setter
    def conductivity_coefficient_b(self, value=None):
        self["conductivity_coefficient_b"] = value

    @property
    def conductivity_coefficient_c(self):
        return self["conductivity_coefficient_c"]

    @conductivity_coefficient_c.setter
    def conductivity_coefficient_c(self, value=None):
        self["conductivity_coefficient_c"] = value

    @property
    def conductivity_coefficient_a(self):
        return self["conductivity_coefficient_a"]

    @conductivity_coefficient_a.setter
    def conductivity_coefficient_a(self, value=None):
        self["conductivity_coefficient_a"] = value

    @property
    def viscosity_coefficient_a(self):
        return self["viscosity_coefficient_a"]

    @viscosity_coefficient_a.setter
    def viscosity_coefficient_a(self, value=None):
        self["viscosity_coefficient_a"] = value

    @property
    def viscosity_coefficient_c(self):
        return self["viscosity_coefficient_c"]

    @viscosity_coefficient_c.setter
    def viscosity_coefficient_c(self, value=None):
        self["viscosity_coefficient_c"] = value

    @property
    def viscosity_coefficient_b(self):
        return self["viscosity_coefficient_b"]

    @viscosity_coefficient_b.setter
    def viscosity_coefficient_b(self, value=None):
        self["viscosity_coefficient_b"] = value




class WindowMaterialGap(BaseObject):
    """Corresponds to object `WindowMaterial:Gap`"""
    _schema = {
        'type': 'object',
        'patternProperties': {
            '.*': {
                'required': [
                    'thickness',
                    'gas_or_gas_mixture_'],
                'type': 'object',
                'properties': {
                    'pressure': {
                        'units': 'Pa',
                        'default': 101325.0,
                        'type': 'number'},
                    'gas_or_gas_mixture_': {
                        'type': 'string',
                        'object_list': ['WindowGasAndGasMixtures'],
                        'data_type': 'object_list'},
                    'deflection_state': {
                        'object_list': ['WindowGapDeflectionStates'],
                        'type': 'string',
                                'data_type': 'object_list'},
                    'support_pillar': {
                        'object_list': ['WindowGapSupportPillars'],
                        'type': 'string',
                        'data_type': 'object_list'},
                    'thickness': {
                        'units': 'm',
                        'minimum': 0.0,
                        'type': 'number',
                        'exclusiveMinimum': True}}}},
        'name': {
            'is_required': True,
            'type': 'string',
            'reference': ['CFSGap']}}

    @property
    def pressure(self):
        return self["pressure"]

    @pressure.setter
    def pressure(self, value=None):
        self["pressure"] = value

    @property
    def gas_or_gas_mixture_(self):
        return self["gas_or_gas_mixture_"]

    @gas_or_gas_mixture_.setter
    def gas_or_gas_mixture_(self, value=None):
        self["gas_or_gas_mixture_"] = value

    @property
    def deflection_state(self):
        return self["deflection_state"]

    @deflection_state.setter
    def deflection_state(self, value=None):
        self["deflection_state"] = value

    @property
    def support_pillar(self):
        return self["support_pillar"]

    @support_pillar.setter
    def support_pillar(self, value=None):
        self["support_pillar"] = value

    @property
    def thickness(self):
        return self["thickness"]

    @thickness.setter
    def thickness(self, value=None):
        self["thickness"] = value




class Construction(BaseObject):
    """Corresponds to object `Construction`"""
    _schema = {
        'type': 'object', 'patternProperties': {
            '.*': {
                'required': ['outside_layer'], 'type': 'object', 'properties': {
                    'layer_9': {
                        'object_list': ['MaterialName'], 'type': 'string', 'data_type': 'object_list'}, 'layer_8': {
                        'object_list': ['MaterialName'], 'type': 'string', 'data_type': 'object_list'}, 'outside_layer': {
                            'type': 'string', 'object_list': ['MaterialName'], 'data_type': 'object_list'}, 'layer_2': {
                                'object_list': ['MaterialName'], 'type': 'string', 'data_type': 'object_list'}, 'layer_5': {
                                    'object_list': ['MaterialName'], 'type': 'string', 'data_type': 'object_list'}, 'layer_4': {
                                        'object_list': ['MaterialName'], 'type': 'string', 'data_type': 'object_list'}, 'layer_7': {
                                            'object_list': ['MaterialName'], 'type': 'string', 'data_type': 'object_list'}, 'layer_6': {
                                                'object_list': ['MaterialName'], 'type': 'string', 'data_type': 'object_list'}, 'layer_10': {
                                                    'object_list': ['MaterialName'], 'type': 'string', 'data_type': 'object_list'}, 'layer_3': {
                                                        'object_list': ['MaterialName'], 'type': 'string', 'data_type': 'object_list'}}}}, 'name': {
                                                            'is_required': True, 'type': 'string', 'reference': ['ConstructionNames']}}

    @property
    def layer_9(self):
        return self["layer_9"]

    @layer_9.setter
    def layer_9(self, value=None):
        self["layer_9"] = value

    @property
    def layer_8(self):
        return self["layer_8"]

    @layer_8.setter
    def layer_8(self, value=None):
        self["layer_8"] = value

    @property
    def outside_layer(self):
        return self["outside_layer"]

    @outside_layer.setter
    def outside_layer(self, value=None):
        self["outside_layer"] = value

    @property
    def layer_2(self):
        return self["layer_2"]

    @layer_2.setter
    def layer_2(self, value=None):
        self["layer_2"] = value

    @property
    def layer_5(self):
        return self["layer_5"]

    @layer_5.setter
    def layer_5(self, value=None):
        self["layer_5"] = value

    @property
    def layer_4(self):
        return self["layer_4"]

    @layer_4.setter
    def layer_4(self, value=None):
        self["layer_4"] = value

    @property
    def layer_7(self):
        return self["layer_7"]

    @layer_7.setter
    def layer_7(self, value=None):
        self["layer_7"] = value

    @property
    def layer_6(self):
        return self["layer_6"]

    @layer_6.setter
    def layer_6(self, value=None):
        self["layer_6"] = value

    @property
    def layer_10(self):
        return self["layer_10"]

    @layer_10.setter
    def layer_10(self, value=None):
        self["layer_10"] = value

    @property
    def layer_3(self):
        return self["layer_3"]

    @layer_3.setter
    def layer_3(self, value=None):
        self["layer_3"] = value


