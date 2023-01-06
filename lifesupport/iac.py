# Imports
from constructor import power, modules, doors
"""
IaC acts as a multiplexer controller/regulator,
simulation calls on its functions to regulate (on/off) certain devices
"""


"""
SETTINGS FOR AIR DEVICES
"""
# emergency status (if true different values apply)
emergency = False
# temperature degC, humidity %, pressure hPa, O2 %, CO2 %, N2 %, radiation μSv/h
air_desired = [22, 40, 827, 21, 0.04, 78, 5]
air_emergency = [19, 60, 800, 19.5, 0.1, 78, 5]

"""
AIR regulator devices
"""


def thermostat(measured_temp):      # hysteresis 0.5degC

    if emergency:
        if measured_temp <= (air_emergency[0] - 0.5):
            return True
        elif measured_temp >= (air_emergency[0] + 0.5):
            return False
        else:
            return
    else:
        if measured_temp <= (air_desired[0] - 0.5):
            return True
        elif measured_temp >= (air_desired[0] + 0.5):
            return False
        else:
            return


def humistat(measured_hum):         # hysteresis 5%

    if emergency:
        if measured_hum >= (air_emergency[1] + 5):
            return True
        elif measured_hum <= (air_emergency[1] - 5):
            return False
        else:
            return
    else:
        if measured_hum >= (air_desired[1] + 5):
            return True
        elif measured_hum <= (air_desired[1] + 5):
            return False
        else:
            return


def oxygen_regulator(measured_oxy):  # hysteresis 0.5%

    if emergency:
        if measured_oxy <= (air_emergency[3] - 0.5):
            return True
        elif measured_oxy >= (air_emergency[3] + 0.5):
            return False
        else:
            return
    else:
        if measured_oxy <= (air_desired[3] - 0.5):
            return True
        elif measured_oxy >= (air_desired[3] + 0.5):
            return False
        else:
            return


def carbon_regulator(measured_carb):  # hysteresis 0.02%
    if emergency:
        if measured_carb >= (air_emergency[4] + 0.02):
            return True
        elif measured_carb <= (air_emergency[4] - 0.02):
            return False
        else:
            return
    else:
        if measured_carb >= (air_desired[4] + 0.02):
            return True
        elif measured_carb <= (air_desired[4] - 0.02):
            return False
        else:
            return


def pressure_check(measured_pressure, module_id):  # hysteresis triggers at -20 difference against desired
    if measured_pressure <= (air_desired[3] - 20):
        for i in doors:
            if i.belongs_to == modules[module_id].name:
                i.close()
    else:
        for i in doors:
            if i.belongs_to == modules[module_id].name:
                i.open()


def ionizing_rad_check(measured_rad, module_id):  # hysteresis triggers at +5 difference against desired 10uS/h
    if measured_rad >= (air_desired[6] + 5):
        for i in doors:
            if i.belongs_to == modules[module_id].name:
                i.close()
    else:
        for i in doors:
            if i.belongs_to == modules[module_id].name:
                i.open()


def fire_check(fac_status, module_id):     # wile looking useless, this function simulates the information flow trough IaC
    if fac_status:
        for i in doors:
            if i.belongs_to == modules[module_id].name:
                i.close()
    else:
        for i in doors:
            if i.belongs_to == modules[module_id].name:
                i.open()


def disconnect_close_door(module_id):       # automatically finds and closes door adjacent to module that was disconnected
    for i in doors:
        if (i.connection_status == False) and (i.adjacent_to == modules[module_id].name):
            i.close()

    for i in doors:
        if (i.connection_status == True) and i.adjacent_to == modules[module_id].name:
            i.open()


def disconnect_check():                                         # matching the status for adjacent doors in airlock
    for i in doors:
        for o in doors:
            if i.belongs_to == o.adjacent_to:
                o.connection_status = i.connection_status
