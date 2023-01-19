# Imports
import time
import random
import math
from data_logger import sensor_log_append, sensor_log_init
from constructor import power, modules, doors
from iac import thermostat, humistat, oxygen_regulator, carbon_regulator, pressure_check, ionizing_rad_check, fire_check, disconnect_check, disconnect_close_door

# Start data logging
sensor_log_init()

# Settings
simulation_speed = 1        # set the simulation "tick" speed in seconds, default = 1
test_print = True           # Set to True in order to see simulated values in console, default False
orbit = True                # is our ship orbiting ?   (this will be later controlled trough IAC or simulation input)
orbit_speed = 1             # duration of orbit in minutes  (this will be later controlled trough IAC or simulation input)


# Global variables for timers and other simulation iterators
previous_time_loop = float(0)
previous_time_orbit = float(0)
angle = 0
solar_shadow = float()

"""
SIMULATION LOOP     *runs indefinitely
- calling every Environmental function at every loop
- calling Devices functions based on IaC variables
- printing power system values and every module sensor data (if desired)
"""

while True:             # infinite loop for simulation purposes
    time.sleep(0.1)     # infinite loop delay so weak PC's won't explode
    current_time = time.time()  # getting the current time for timers
    power.consumption_reset()   # restarting consumption before every simulation loop

    # Orbiting / solar shadow and fuel burn simulation (using only one sinus wave, totally not scientifically accurate)
    if orbit:                                                           # happens only if orbit is True
        if (current_time - previous_time_orbit) >= (orbit_speed / 3):   # timer, speed divided by 3 for time conversion
            previous_time_orbit = current_time                          # mark the current time as previous time
            angle = angle + 1                                           # add one degree to our angle towards sun
            if angle == 180:                                            # reset degree counter at 180
                angle = 0
            solar_shadow = 0.5 + math.sin(math.radians(angle))          # make sinus of our angle with positive offset
            if solar_shadow > 1:                                        # offset overflow catch
                solar_shadow = 1

    # Main simulation
    if (current_time - previous_time_loop) >= simulation_speed:     # timer (triggers when result is more than interval)
        previous_time_loop = current_time                           # mark the current time as previous time

        if orbit:                       # happens only if orbit is True
            if power.fuel_gauge > 0:    # if there is enough fuel
                power.fuel(1)          # burn fuel to stay in orbit (burned 1kg)
            else:                       # else burn emergency fuel to stay in orbit
                power.emer_fuel(1)

        loop_entropy = random.uniform(0.9, 1.1)  # variable entropy introducing slight randomness to every cycle

        # Environmental functions for modules (runs always)
        for i in modules:
            i.cold(loop_entropy)
            i.hum(loop_entropy)
            i.breathing(loop_entropy)
            for adj_list in i.adj_mod:              # additional loop for simulation of mixing air inbetween modules
                if doors[1].status:                     # air is mixing only if doors are open
                    temp = modules[adj_list].air[0]     # works based on adjacent_modules list for every module
                    hum = modules[adj_list].air[1]
                    hpa = modules[adj_list].air[2]
                    o2 = modules[adj_list].air[3]
                    co2 = modules[adj_list].air[4]
                    n2 = modules[adj_list].air[5]
                    usv = modules[adj_list].air[6]
                    i.mix(temp, hum, hpa, o2, co2, n2, usv)

        # IaC security functions (closing doors when needed)
        for i in range(len(modules)):                           # using range(len( to parse a module id integer to IaC
            pressure_check(modules[i].air_sensors(2), i)        # this has to be accounted for in here when calling func
            ionizing_rad_check(modules[i].air_sensors(6), i)
            fire_check(modules[i].fac, i)
            disconnect_check()
            disconnect_close_door(i)


        # IaC functions for modules (runs based on IaC)
        for i in modules:
            if thermostat(i.air_sensors(0)):        # IaC function used as condition
                i.heat(loop_entropy)                # turned heater on in simulation
                power.consumption_on(100)           # added 100W to consumption in current run

            if humistat(i.air_sensors(1)):          # similar as above but other devices...
                i.dehum(loop_entropy)
                power.consumption_on(50)

            if oxygen_regulator(i.air_sensors(3)):
                i.oxy_gen(loop_entropy)
                power.consumption_on(50)

            if carbon_regulator(i.air_sensors(4)):
                i.carb_abs(loop_entropy)
                power.consumption_on(20)

        # PowerFuel functions (runs always, some will be based on simulation inputs or IaC)
        power.solar(loop_entropy, orbit, solar_shadow)
        power.battery()
        power.weight()

        # PowerFuel functions (examples that will be called by IaC)
        # power.fuel(100)               # burns 100 kg of fuel
        # power.consumption_on(100)     # starts using 100 W of power
        # power.emergency_battery()     # starts discharging emergency battery to meet power demand (counts on dead main battery)

        # Data logging

        if test_print:
            print('')
            print('::::::::::::::::::::::::::::::::')
            print('SPACESHIP: ', power.name)
            print('____FUEL___')
            print('Main tank: {:.2f}'.format(power.fuel_gauge) + '\tmetric Tons')
            print('Main tank: {:.2f}'.format(power.emer_gauge) + '\tmetric Tons')
            print('____POWER___')
            print('Real input: {:.2f}'.format(power.input) + '\t\tW')
            print('Real load: {:.2f}'.format(power.load) + '\t\tW')
            print('Bat capacity: {:.2f}'.format(power.battery_cap) + '\tWh')
            print('Bat charge: {:.2f}'.format(power.battery_cha) + '\t\tWh')
            print('E_Bat capacity: {:.2f}'.format(power.emerbat_cap) + '\tWh')
            print('E_Bat charge: {:.2f}'.format(power.emerbat_cha) + '\tWh')
            print('___Modules___')
            for i in range(len(modules)):
                print("________________________")
                print('Module no.' + str(i) + '  ' + modules[i].name)
                print(".......................")
                print('{:.2f}'.format(modules[i].air_sensors(0)) + '\t\t°C')
                print('{:.2f}'.format(modules[i].air_sensors(1)) + '\t\t% H2O')
                print('{:.2f}'.format(modules[i].air_sensors(2)) + '\t\thPa')
                print('{:.2f}'.format(modules[i].air_sensors(3)) + '\t\t% O2')
                print('{:.2f}'.format(modules[i].air_sensors(4)) + '\t\t% CO2')
                print('{:.2f}'.format(modules[i].air_sensors(5)) + '\t\t% NO2')
                print('{:.2f}'.format(modules[i].air_sensors(6)) + '\t\tμSv/h')
                if modules[i].fire_sensors(): print("FAC status: FIRE !!!")
                else: print("FAC status: OK")
            for i in doors:
                print(str(i.door_id) + '\t\t' + i.belongs_to + '\t\t\t' + i.adjacent_to + '\t\t\t' + str(i.status) + '\t\t\t' + str(i.connection_status))


        sensor_log_append()
