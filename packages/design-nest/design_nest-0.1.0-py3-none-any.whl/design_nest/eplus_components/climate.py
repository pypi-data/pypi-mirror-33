""" Data objects in group "climate" """
from design_nest.eplus_components.helper import BaseObject



class SizingPeriodDesignDay(BaseObject):
    """Corresponds to object `SizingPeriod:DesignDay`"""
    _schema = {
        'type': 'object',
        'patternProperties': {
            '.*': {
                'required': [
                    'month',
                    'day_of_month',
                    'day_type',
                    'wind_speed',
                    'wind_direction'],
                'type': 'object',
                'properties': {
                    'maximum_dry_bulb_temperature': {
                        'units': 'C',
                        'minimum': -90.0,
                        'type': 'number',
                        'maximum': 70.0},
                    'wind_direction': {
                        'maximum': 360.0,
                        'minimum': 0.0,
                        'units': 'deg',
                        'type': 'number'},
                    'month': {
                        'minimum': 1.0,
                        'type': 'number',
                                'maximum': 12.0},
                    'daylight_saving_time_indicator': {
                        'default': 'No',
                        'enum': [
                            '',
                            'No',
                            'Yes'],
                        'type': 'string'},
                    'day_type': {
                        'type': 'string',
                        'enum': [
                            'CustomDay1',
                            'CustomDay2',
                            'Friday',
                            'Holiday',
                            'Monday',
                            'Saturday',
                            'SummerDesignDay',
                            'Sunday',
                            'Thursday',
                            'Tuesday',
                            'Wednesday',
                            'WinterDesignDay']},
                    'barometric_pressure': {
                        'maximum': 120000.0,
                        'ip-units': 'inHg',
                        'minimum': 31000.0,
                        'units': 'Pa',
                        'type': 'number'},
                    'humidity_condition_day_schedule_name': {
                        'object_list': ['DayScheduleNames'],
                        'type': 'string',
                        'data_type': 'object_list'},
                    'humidity_condition_type': {
                        'default': 'WetBulb',
                        'enum': [
                            '',
                            'DewPoint',
                            'Enthalpy',
                            'HumidityRatio',
                            'RelativeHumiditySchedule',
                            'WetBulb',
                            'WetBulbProfileDefaultMultipliers',
                            'WetBulbProfileDifferenceSchedule',
                            'WetBulbProfileMultiplierSchedule'],
                        'type': 'string'},
                    'wetbulb_or_dewpoint_at_maximum_dry_bulb': {
                        'units': 'C',
                        'type': 'number'},
                    'ashrae_clear_sky_optical_depth_for_beam_irradiance_taub_': {
                        'default': 0.0,
                        'maximum': 1.2,
                        'minimum': 0.0,
                        'units': 'dimensionless',
                        'type': 'number'},
                    'dry_bulb_temperature_range_modifier_type': {
                        'default': 'DefaultMultipliers',
                        'enum': [
                            '',
                            'DefaultMultipliers',
                            'DifferenceSchedule',
                            'MultiplierSchedule',
                            'TemperatureProfileSchedule'],
                        'type': 'string'},
                    'solar_model_indicator': {
                        'default': 'ASHRAEClearSky',
                        'enum': [
                            '',
                            'ASHRAEClearSky',
                            'ASHRAETau',
                            'Schedule',
                            'ZhangHuang'],
                        'type': 'string'},
                    'sky_clearness': {
                        'default': 0.0,
                        'minimum': 0.0,
                        'type': 'number',
                        'maximum': 1.2},
                    'snow_indicator': {
                        'default': 'No',
                        'enum': [
                            '',
                            'No',
                            'Yes'],
                        'type': 'string'},
                    'dry_bulb_temperature_range_modifier_day_schedule_name': {
                        'object_list': ['DayScheduleNames'],
                        'type': 'string',
                        'data_type': 'object_list'},
                    'ashrae_clear_sky_optical_depth_for_diffuse_irradiance_taud_': {
                        'default': 0.0,
                        'maximum': 3.0,
                        'minimum': 0.0,
                        'units': 'dimensionless',
                        'type': 'number'},
                    'daily_wet_bulb_temperature_range': {
                        'units': 'deltaC',
                        'type': 'number'},
                    'enthalpy_at_maximum_dry_bulb': {
                        'units': 'J/kg',
                        'type': 'number'},
                    'diffuse_solar_day_schedule_name': {
                        'object_list': ['DayScheduleNames'],
                        'type': 'string',
                        'data_type': 'object_list'},
                    'wind_speed': {
                        'maximum': 40.0,
                        'ip-units': 'miles/hr',
                        'minimum': 0.0,
                        'units': 'm/s',
                        'type': 'number'},
                    'beam_solar_day_schedule_name': {
                        'object_list': ['DayScheduleNames'],
                        'type': 'string',
                        'data_type': 'object_list'},
                    'humidity_ratio_at_maximum_dry_bulb': {
                        'units': 'kgWater/kgDryAir',
                        'type': 'number'},
                    'day_of_month': {
                        'minimum': 1.0,
                        'type': 'number',
                        'maximum': 31.0},
                    'daily_dry_bulb_temperature_range': {
                        'units': 'deltaC',
                        'default': 0.0,
                        'minimum': 0.0,
                        'type': 'number'},
                    'rain_indicator': {
                        'default': 'No',
                        'enum': [
                            '',
                            'No',
                            'Yes'],
                        'type': 'string'}}}},
        'name': {
            'is_required': True,
            'type': 'string',
            'reference': ['RunPeriodsAndDesignDays']}}

    @property
    def maximum_dry_bulb_temperature(self):
        return self["maximum_dry_bulb_temperature"]

    @maximum_dry_bulb_temperature.setter
    def maximum_dry_bulb_temperature(self, value=None):
        self["maximum_dry_bulb_temperature"] = value

    @property
    def wind_direction(self):
        return self["wind_direction"]

    @wind_direction.setter
    def wind_direction(self, value=None):
        self["wind_direction"] = value

    @property
    def month(self):
        return self["month"]

    @month.setter
    def month(self, value=None):
        self["month"] = value

    @property
    def daylight_saving_time_indicator(self):
        return self["daylight_saving_time_indicator"]

    @daylight_saving_time_indicator.setter
    def daylight_saving_time_indicator(self, value=None):
        self["daylight_saving_time_indicator"] = value

    @property
    def day_type(self):
        return self["day_type"]

    @day_type.setter
    def day_type(self, value=None):
        self["day_type"] = value

    @property
    def barometric_pressure(self):
        return self["barometric_pressure"]

    @barometric_pressure.setter
    def barometric_pressure(self, value=None):
        self["barometric_pressure"] = value

    @property
    def humidity_condition_day_schedule_name(self):
        return self["humidity_condition_day_schedule_name"]

    @humidity_condition_day_schedule_name.setter
    def humidity_condition_day_schedule_name(self, value=None):
        self["humidity_condition_day_schedule_name"] = value

    @property
    def humidity_condition_type(self):
        return self["humidity_condition_type"]

    @humidity_condition_type.setter
    def humidity_condition_type(self, value=None):
        self["humidity_condition_type"] = value

    @property
    def wetbulb_or_dewpoint_at_maximum_dry_bulb(self):
        return self["wetbulb_or_dewpoint_at_maximum_dry_bulb"]

    @wetbulb_or_dewpoint_at_maximum_dry_bulb.setter
    def wetbulb_or_dewpoint_at_maximum_dry_bulb(self, value=None):
        self["wetbulb_or_dewpoint_at_maximum_dry_bulb"] = value

    @property
    def ashrae_clear_sky_optical_depth_for_beam_irradiance_taub_(self):
        return self["ashrae_clear_sky_optical_depth_for_beam_irradiance_taub_"]

    @ashrae_clear_sky_optical_depth_for_beam_irradiance_taub_.setter
    def ashrae_clear_sky_optical_depth_for_beam_irradiance_taub_(
            self, value=None):
        self["ashrae_clear_sky_optical_depth_for_beam_irradiance_taub_"] = value

    @property
    def dry_bulb_temperature_range_modifier_type(self):
        return self["dry_bulb_temperature_range_modifier_type"]

    @dry_bulb_temperature_range_modifier_type.setter
    def dry_bulb_temperature_range_modifier_type(self, value=None):
        self["dry_bulb_temperature_range_modifier_type"] = value

    @property
    def solar_model_indicator(self):
        return self["solar_model_indicator"]

    @solar_model_indicator.setter
    def solar_model_indicator(self, value=None):
        self["solar_model_indicator"] = value

    @property
    def sky_clearness(self):
        return self["sky_clearness"]

    @sky_clearness.setter
    def sky_clearness(self, value=None):
        self["sky_clearness"] = value

    @property
    def snow_indicator(self):
        return self["snow_indicator"]

    @snow_indicator.setter
    def snow_indicator(self, value=None):
        self["snow_indicator"] = value

    @property
    def dry_bulb_temperature_range_modifier_day_schedule_name(self):
        return self["dry_bulb_temperature_range_modifier_day_schedule_name"]

    @dry_bulb_temperature_range_modifier_day_schedule_name.setter
    def dry_bulb_temperature_range_modifier_day_schedule_name(
            self, value=None):
        self["dry_bulb_temperature_range_modifier_day_schedule_name"] = value

    @property
    def ashrae_clear_sky_optical_depth_for_diffuse_irradiance_taud_(self):
        return self["ashrae_clear_sky_optical_depth_for_diffuse_irradiance_taud_"]

    @ashrae_clear_sky_optical_depth_for_diffuse_irradiance_taud_.setter
    def ashrae_clear_sky_optical_depth_for_diffuse_irradiance_taud_(
            self, value=None):
        self["ashrae_clear_sky_optical_depth_for_diffuse_irradiance_taud_"] = value

    @property
    def daily_wet_bulb_temperature_range(self):
        return self["daily_wet_bulb_temperature_range"]

    @daily_wet_bulb_temperature_range.setter
    def daily_wet_bulb_temperature_range(self, value=None):
        self["daily_wet_bulb_temperature_range"] = value

    @property
    def enthalpy_at_maximum_dry_bulb(self):
        return self["enthalpy_at_maximum_dry_bulb"]

    @enthalpy_at_maximum_dry_bulb.setter
    def enthalpy_at_maximum_dry_bulb(self, value=None):
        self["enthalpy_at_maximum_dry_bulb"] = value

    @property
    def diffuse_solar_day_schedule_name(self):
        return self["diffuse_solar_day_schedule_name"]

    @diffuse_solar_day_schedule_name.setter
    def diffuse_solar_day_schedule_name(self, value=None):
        self["diffuse_solar_day_schedule_name"] = value

    @property
    def wind_speed(self):
        return self["wind_speed"]

    @wind_speed.setter
    def wind_speed(self, value=None):
        self["wind_speed"] = value

    @property
    def beam_solar_day_schedule_name(self):
        return self["beam_solar_day_schedule_name"]

    @beam_solar_day_schedule_name.setter
    def beam_solar_day_schedule_name(self, value=None):
        self["beam_solar_day_schedule_name"] = value

    @property
    def humidity_ratio_at_maximum_dry_bulb(self):
        return self["humidity_ratio_at_maximum_dry_bulb"]

    @humidity_ratio_at_maximum_dry_bulb.setter
    def humidity_ratio_at_maximum_dry_bulb(self, value=None):
        self["humidity_ratio_at_maximum_dry_bulb"] = value

    @property
    def day_of_month(self):
        return self["day_of_month"]

    @day_of_month.setter
    def day_of_month(self, value=None):
        self["day_of_month"] = value

    @property
    def daily_dry_bulb_temperature_range(self):
        return self["daily_dry_bulb_temperature_range"]

    @daily_dry_bulb_temperature_range.setter
    def daily_dry_bulb_temperature_range(self, value=None):
        self["daily_dry_bulb_temperature_range"] = value

    @property
    def rain_indicator(self):
        return self["rain_indicator"]

    @rain_indicator.setter
    def rain_indicator(self, value=None):
        self["rain_indicator"] = value




class SiteGroundTemperatureBuildingSurface(BaseObject):
    """Corresponds to object `Site:GroundTemperature:BuildingSurface`"""
    _schema = {
        'format': 'singleLine', 'min_fields': 12.0, 'patternProperties': {
            '.*': {
                'properties': {
                    'october_ground_temperature': {
                        'units': 'C', 'default': 18.0, 'type': 'number'}, 'july_ground_temperature': {
                        'units': 'C', 'default': 18.0, 'type': 'number'}, 'may_ground_temperature': {
                            'units': 'C', 'default': 18.0, 'type': 'number'}, 'august_ground_temperature': {
                                'units': 'C', 'default': 18.0, 'type': 'number'}, 'march_ground_temperature': {
                                    'units': 'C', 'default': 18.0, 'type': 'number'}, 'december_ground_temperature': {
                                        'units': 'C', 'default': 18.0, 'type': 'number'}, 'november_ground_temperature': {
                                            'units': 'C', 'default': 18.0, 'type': 'number'}, 'april_ground_temperature': {
                                                'units': 'C', 'default': 18.0, 'type': 'number'}, 'june_ground_temperature': {
                                                    'units': 'C', 'default': 18.0, 'type': 'number'}, 'january_ground_temperature': {
                                                        'units': 'C', 'default': 18.0, 'type': 'number'}, 'february_ground_temperature': {
                                                            'units': 'C', 'default': 18.0, 'type': 'number'}, 'september_ground_temperature': {
                                                                'units': 'C', 'default': 18.0, 'type': 'number'}}, 'type': 'object'}}, 'maxProperties': 1, 'type': 'object'}

    @property
    def october_ground_temperature(self):
        return self["october_ground_temperature"]

    @october_ground_temperature.setter
    def october_ground_temperature(self, value=None):
        self["october_ground_temperature"] = value

    @property
    def july_ground_temperature(self):
        return self["july_ground_temperature"]

    @july_ground_temperature.setter
    def july_ground_temperature(self, value=None):
        self["july_ground_temperature"] = value

    @property
    def may_ground_temperature(self):
        return self["may_ground_temperature"]

    @may_ground_temperature.setter
    def may_ground_temperature(self, value=None):
        self["may_ground_temperature"] = value

    @property
    def august_ground_temperature(self):
        return self["august_ground_temperature"]

    @august_ground_temperature.setter
    def august_ground_temperature(self, value=None):
        self["august_ground_temperature"] = value

    @property
    def march_ground_temperature(self):
        return self["march_ground_temperature"]

    @march_ground_temperature.setter
    def march_ground_temperature(self, value=None):
        self["march_ground_temperature"] = value

    @property
    def december_ground_temperature(self):
        return self["december_ground_temperature"]

    @december_ground_temperature.setter
    def december_ground_temperature(self, value=None):
        self["december_ground_temperature"] = value

    @property
    def november_ground_temperature(self):
        return self["november_ground_temperature"]

    @november_ground_temperature.setter
    def november_ground_temperature(self, value=None):
        self["november_ground_temperature"] = value

    @property
    def april_ground_temperature(self):
        return self["april_ground_temperature"]

    @april_ground_temperature.setter
    def april_ground_temperature(self, value=None):
        self["april_ground_temperature"] = value

    @property
    def june_ground_temperature(self):
        return self["june_ground_temperature"]

    @june_ground_temperature.setter
    def june_ground_temperature(self, value=None):
        self["june_ground_temperature"] = value

    @property
    def january_ground_temperature(self):
        return self["january_ground_temperature"]

    @january_ground_temperature.setter
    def january_ground_temperature(self, value=None):
        self["january_ground_temperature"] = value

    @property
    def february_ground_temperature(self):
        return self["february_ground_temperature"]

    @february_ground_temperature.setter
    def february_ground_temperature(self, value=None):
        self["february_ground_temperature"] = value

    @property
    def september_ground_temperature(self):
        return self["september_ground_temperature"]

    @september_ground_temperature.setter
    def september_ground_temperature(self, value=None):
        self["september_ground_temperature"] = value


