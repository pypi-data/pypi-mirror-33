class Settings:

    info = {
        "version": "0.1.0",
        "description": "Python library which allows to read, modify, create and run EnergyPlus files and simulations."
    }

    groups = {
        'simulation_parameters': [
            'Version',
            'SimulationControl',
            'ShadowCalculations',
            'SurfaceConvectionAlgorithm:Outside',
            'SurfaceConvectionAlgorithm:Inside'
            'TimeStep',
            'GlobalGeometryRules',
            'HeatBalanceAlgorithm'
        ],
        'building': [
            'Site:Location',
            'Building'
        ],
        'climate': [
            'SizingPeriod:DesignDay',
            'Site:GroundTemperature:BuildingSurface',
        ],
        'schedules': [
            'ScheduleTypeLimits',
            'ScheduleDayHourly',
            'ScheduleDayInterval',
            'ScheduleWeekDaily',
            'ScheduleWeekCompact',
            'ScheduleConstant',
            'ScheduleFile',
            'ScheduleDayList',
            'ScheduleYear',
            'ScheduleCompact'
        ],
        'construction': [
            'Material',
            'Material:NoMass',
            'Material:AirGap',
            'WindowMaterial:SimpleGlazingSystem',
            'WindowMaterial:Glazing',
            'WindowMaterial:Gas',
            'WindowMaterial:Gap',
            'Construction'
        ],
        'internal_gains': [
            'People',
            'Lights',
            'ElectricEquipment',

        ],
        'airflow': [
            'ZoneInfiltration:DesignFlowRate',
            'ZoneVentilation:DesignFlowRate'
        ],
        'zone': [
            'BuildingSurface:Detailed',
        ],
        'zone_control': [
            'ZoneControl:Thermostat',
            'ThermostatSetpoint:SingleHeating',
            'ThermostatSetpoint:SingleCooling',
            'ThermostatSetpoint:SingleHeatingOrCooling',
            'ThermostatSetpoint:DualSetpoint',
        ],
        'systems': [
            'Zone:IdealAirLoadsSystem',
            'HVACTemplate:Zone:IdealLoadsAirSystem'
        ],
        'outputs': [
            'Output:SQLite',
            'Output:Table:SummaryReports'
        ]
    }