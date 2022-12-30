# Imports
import time
import random
import math

# Settings
simulation_speed = 1        # set the simulation "tick" speed in seconds, default = 1
constructor_print = True    # Set to True to see all input parameters of our ship at the beginning of simulation
test_print = False          # Set to True in order to see simulated values in console, default False
orbit = True                # is our ship orbiting ?   (this will be later controlled trough IAC or simulation input)
orbit_speed = 1             # duration of orbit in minutes  (this will be later controlled trough IAC or simulation input)

# Ship constructor

# Global variables for timers and other simulation iterators
previous_time_loop = float(0)
previous_time_orbit = float(0)
angle = 0
solar_shadow = float()

"""
Simulating crew members in spaceship
- basic list of basic parameters
- name, height, weight
- weight is used in calculations
"""


class Crewmate (object):

    def __init__(self, human_name: str, human_height: float, human_weight: float):
        self.human_name = human_name
        self.human_height = human_height
        self.human_weight = human_weight


"""
Simulating modules in spaceship
DISCLAIMER: This in no way represents actual scientific calculations, constants or simulations
- using class: Module in order to make simulation universal for any spaceship layout
- every module dissipates heat into space and gains heat from crew bodies
- every module gains humidity by crew breathing and skin evaporation
- pressure in every module should stay at normal value unless there is a hull breach
- every module loses oxygen and gains carbon dioxide based on average cew members inside
- every module has its own heater, dehumidifier, oxygen generator and carbon dioxide absorber to make simulation easier
- infinite loop repeatedly calls functions to cause changes in values
- variable entropy is added to every function to introduce randomness
"""


class Module (object):

    def __init__(self, module_name: str, module_size: float, module_weight: float, adjacent_modules: list, avg_crew: int, power_draw: float, lights_draw: float):
        self.sim_const = 39                     # simulation constant (for speeding/slowing simulation calculations)
        self.name = module_name                 # module name (obviously)
        self.size = module_size                 # module size (used for hysteresis simulation value)
        self.weight = module_weight             # module weight
        self.adj_mod = adjacent_modules         # doors to adjacent modules (used for automatic doors generation)
        self.crew = avg_crew                    # average crew members per module
        self.draw = power_draw                  # base power draw for module
        self.light = lights_draw                # lights power draw for module
        self.emer_lights = lights_draw * 0.2    # emergency lights power draw for module
        self.air = list()                       # list of atmospheric data including radiation dose
        self.fac = bool()                       # status of fire alarm control sensor

        # Module always starts simulation with "normalized" values
        self.air.append(22)    # deg C (temperature)
        self.air.append(40)    # % (relative humidity)
        self.air.append(827)   # hPa (pressure)
        self.air.append(21)    # % O2
        self.air.append(0.04)  # % CO2
        self.air.append(78)    # % N2
        self.air.append(5)     # μSv/h (ionizing radiation)
        self.fac = False

    # Environment

    def cold(self, entropy: float):     # heat loss + body heat gain
        self.air[0] = self.air[0] - ((20 * entropy) / (self.size * self.sim_const))
        self.air[0] = self.air[0] + ((3 * entropy * self.crew) / (self.size * self.sim_const))
        return

    def hum(self, entropy: float):      # humidity caused by crew
        self.air[1] = self.air[1] + ((7 * entropy * self.crew) / (self.size * self.sim_const))
        return

    def breathing(self, entropy: float):  # crew breathing (-O2 +CO2)
        self.air[3] = self.air[3] - ((5 * entropy * self.crew) / (self.size * self.sim_const))
        self.air[4] = self.air[4] + ((5 * entropy * self.crew) / (self.size * self.sim_const))
        return

    # air mixing trough open doors (essential for hull breach simulation, good for added "realism")
    def mix(self,temp: float, hum: float, hpa: float, o2: float, co2: float, n2: float, usv: float):
        self.air[0] = (((self.air[0] * 5) + temp) / 6)
        self.air[1] = (((self.air[1] * 5) + hum) / 6)
        self.air[2] = (((self.air[2] * 5) + hpa) / 6)
        self.air[3] = (((self.air[3] * 5) + o2) / 6)
        self.air[4] = (((self.air[4] * 5) + co2) / 6)
        self.air[5] = (((self.air[5] * 5) + n2) / 6)
        self.air[6] = (((self.air[6] * 5) + usv) / 6)

    # Devices

    def heat(self, entropy: float):     # heater
        self.air[0] = self.air[0] + ((50 * entropy) / (self.size * self.sim_const))
        return

    def dehum(self, entropy: float):    # dehumidifier
        self.air[1] = self.air[1] - ((20 * entropy) / (self.size * self.sim_const))
        return

    def oxy_gen(self, entropy: float):  # oxygen generator
        self.air[3] = self.air[3] + ((10 * entropy) / (self.size * self.sim_const))
        self.air[2] = self.air[2] + ((5 * entropy) / (self.size * self.sim_const))
        return

    def carb_abs(self, entropy: float): # carbon dioxide absorber
        self.air[4] = self.air[4] - ((10 * entropy) / (self.size * self.sim_const))
        self.air[2] = self.air[2] - ((5 * entropy) / (self.size * self.sim_const))
        return

    # Sensors

    def air_sensors(self, index):
        return self.air[index]

    def fire_sensors(self):
        return self.fac

    # Failures (call only manually)

    def module_breach(self, size: int, entropy: float):
        self.air[2] = self.air[2] - ((size * entropy) / (self.size * self.sim_const))
        return

    def module_breach_reset(self):
        self.air[2] = 827
        return

    def fire(self):
        self.fac = True
        return

    def fire_reset(self):
        self.fac = False
        return

    def radiation_hazard(self, size: int, entropy: float):
        self.air[6] = self.air[6] + ((size * entropy) / (self.size * self.sim_const))
        return

    def radiation_hazard_reset(self):
        self.air[6] = 5
        return

    def oxygen_depletion(self, size: int, entropy: float):
        self.air[3] = self.air[3] + ((size * entropy) / (self.size * self.sim_const))
        self.air[4] = self.air[4] + ((size * entropy) / (self.size * self.sim_const))
        return

    def oxygen_depletion_reset(self):
        self.air[3] = 21
        self.air[4] = 0.04
        return


"""
Simulating spaceship airlock doors between modules where they connect
- every module gets doors based on how many adjacent modules it has
- imaginary "airlock" as a gate to outer space has its separate mechanism as a part of module and does not belong here
- opening and closing of doors is managed trough Iac
"""


class Door(object):

    def __init__(self, door_id: int, belongs_to: str, adjacent_to: str):
        self.door_id = door_id
        self.belongs_to = belongs_to
        self.adjacent_to = adjacent_to
        self.status = True

    def open(self):
        self.status = True

    def close(self):
        self.status = False


"""
Simulating spaceship Power System
DISCLAIMER: This in no way represents actual scientific calculations, constants or simulations
- ship constantly draws xy.z W of power for its basic needs
- solar panels have different output based on orbit position
- battery charges and discharges as expected only when there is more/less power than demand
- emergency uranium battery kicks in at 0 charge of the main battery (IaC)
- emergency status in IaC (less heating, emergency lighting)
"""


class PowerFuel (object):

    def __init__(self, ship_name: str, m_weight: float, constant_draw: float, solar_max: int, main_battery: int, emer_battery: int, main_tank: int, emer_tank: int):
        self.name = ship_name           # ship name (obviously)
        self.draw = constant_draw       # constant power draw (sum of minimal draw of all modules)
        self.m_weight = m_weight        # ship weight (sum of modules weight + crew)
        self.t_weight = m_weight        # ship weight (accounted for fuel)
        self.load = float               # real time power demand of whole spaceship
        self.input_max = solar_max      # maximum solar input power
        self.input = float              # actual solar input power
        self.battery_cap = main_battery     # capacity of the main battery
        self.battery_cha = float            # charge of the main battery
        self.emerbat_cap = emer_battery     # capacity of the emergency battery
        self.emerbat_cha = float            # charge of the emergency battery
        self.fuel_tank = main_tank          # main fuel tank capacity
        self.fuel_gauge = float             # fuel amount
        self.emer_tank = emer_tank          # emergency fuel tank capacity
        self.emer_gauge = float             # emergency fuel amount

        # Power always starts simulation with "normalized" values (main battery is half charged)
        self.load = self.draw
        self.input = solar_max
        self.battery_cha = main_battery - (main_battery / 2)
        self.emerbat_cha = emer_battery
        self.fuel_gauge = main_tank
        self.emer_gauge = emer_tank

    def weight(self):
        self.t_weight = self.m_weight + self.fuel_gauge + self.emer_gauge

    def solar(self, entropy: float, is_orbit: bool, orbit_constant: float):     # solar panels input power
        if is_orbit:                                                            # orbit simulation (sinus)
            self.input = self.input_max * orbit_constant * entropy
        else:                                                                   # direct sunlight
            self.input = self.input_max * entropy
        return

    def consumption_on(self, device_draw: float):       # adds consumption to load value
        self.load = self.load + device_draw
        return

    def consumption_off(self, device_draw: float):      # removes consumption from load value
        self.load = self.load - device_draw
        return

    # battery charging/discharging simulation (always call at the end of simulation loop !!!)
    def battery(self):
        charge_const = 0.002    # faking battery capacity
        max_charge = self.battery_cap / 10  # setting maximum charge power to 1/10 of battery capacity
        if self.input > self.load and self.battery_cha < self.battery_cap:  # charging with excess power
            if (self.input - self.load) > max_charge:                       # catching the max charge limit
                self.battery_cha = self.battery_cha + (max_charge * charge_const)   # charging with maximum limit
            else:                                                                   # charging under maximum limit
                self.battery_cha = self.battery_cha + ((self.input - self.load) * charge_const)

        elif self.input < self.load and self.battery_cha > (self.battery_cap / 100):    # discharging to meet the demand
            self.battery_cha = self.battery_cha - ((self.load - self.input) * charge_const)     # discharging -//-
        return

    def emergency_battery(self):    # emergency battery discharging to meet the demand
        charge_const = 0.002        # faking battery capacity
        if self.input < self.load and self.emerbat_cha > (self.emerbat_cap / 1000):     # discharging to meet the demand
            self.emerbat_cha = self.emerbat_cha - ((self.load - self.input) * charge_const)     # discharging -//-

    def emergency_battery_change(self, entropy):     # "physically" changing the emergency battery for a new one
        self.emerbat_cha = self.emerbat_cap * entropy     # new battery

    def fuel(self, burn: float):
        self.fuel_gauge = self.fuel_gauge - (burn / 1000)

    def emer_fuel(self, burn: float):
        self.emer_gauge = self.emer_gauge - (burn / 1000)


"""
SPACESHIP CONSTRUCTOR   *runs once
- specify each crew member according to crew class
- ('name', height [cm], weight [kg]) 
- specify each module according to class Module
- ('name', volume m^3, weight tones, [adjacent to, adjacent to, ...], average crew members, base power draw, lights power draw)
- specify the ships power system
- ('name of the ship', constant power draw [W], maximum solar output [W], main battery capacity [Wh], emergency battery capacity [Wh])
- constructor is now as a part of code but it could be made via some UI 
"""
# Crew input
crew_members = list()
crew_members.append(Crewmate('Mike', 175, 78))
crew_members.append(Crewmate('Carl', 181, 80))
crew_members.append(Crewmate('Gordon', 172, 75))

# Module input
modules = list()
modules.append(Module('Bridge', 35.5, 20.5, [1, 3], 2, 150.5, 54.6))
modules.append(Module('Living', 55.5, 41.2, [0, 2], 4, 47.5, 112.7))
modules.append(Module('Storage', 20.2, 12.4, [1], 1, 54.2, 21.6))
modules.append(Module('BioLab', 45.5, 32.1, [0], 2, 21.5, 121.6))

# Door generator
doors = list()
door_counter = -1
for i in modules:
    for adj_list in i.adj_mod:
        door_counter = door_counter + 1
        doors.append(Door(door_counter, i.name, modules[adj_list].name))

# Sum of parameters that apply to whole ship based on modules and crew
ship_base_draw = 0
ship_base_weight = 0
for i in modules:
    ship_base_draw = ship_base_draw + i.draw
    ship_base_weight = ship_base_weight + i.weight
for i in crew_members:
    ship_base_weight = ship_base_weight + (i.human_weight / 1000)

# Power system constructor
power = PowerFuel('COSMIC_1', ship_base_weight, ship_base_draw, 1000, 1500, 500, 5, 2)

# Recalculates weight at the start to account for fuel
power.weight()
# Power system emergency battery satus randomized before every simulation
power.emergency_battery_change(random.uniform(0.99, 1.01))

# Ship Constructor print Data
if constructor_print:
    print('=======================================')
    print('SPACESHIP: ', power.name)
    print('=======================================')
    print('____WEIGHT____')
    print('Raw weight: {:.2f}'.format(power.m_weight) + '\t\tmetric Tons (ship + crew)')
    print('Total weight: {:.2f}'.format(power.t_weight) + '\tmetric Tons (ship + crew + fuel)')
    print('____CREW_____')
    for i in crew_members:
        print(i.human_name + "   " + str(i.human_height) + ' cm   ' + str(i.human_weight) + ' kg')
    print('____FUEL____')
    print('Main tank: {:.2f}'.format(power.fuel_tank) + '\tmetric Tons')
    print('Main tank: {:.2f}'.format(power.emer_tank) + '\tmetric Tons')
    print('____POWER____')
    print('Max input: {:.2f}'.format(power.input_max) + '\t\tW')
    print('Bat capacity: {:.2f}'.format(power.battery_cap) + '\tWh')
    print('E_Bat capacity: {:.2f}'.format(power.emerbat_cap) + '\tWh')
    print('E_Bat charge: {:.2f}'.format(power.emerbat_cha) + '\tWh')
    print('____DOORS____')
    print('no.   Belongs to      Adjacent to')
    for i in doors:
        print(str(i.door_id) + '\t\t' + i.belongs_to + '\t\t\t' + i.adjacent_to)

"""
SIMULATION LOOP     *runs indefinitely
- calling every Environmental function at every loop
- calling Devices functions based on IaC variables
- printing power system values and every module sensor data (if desired)
"""

while True:             # infinite loop for simulation purposes
    time.sleep(0.1)     # infinite loop delay so weak PC's won't explode
    current_time = time.time()  # getting the current time for timers

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
                temp = modules[adj_list].air[0]     # works based on adjacent_modules list for every module
                hum = modules[adj_list].air[1]
                hpa = modules[adj_list].air[2]
                o2 = modules[adj_list].air[3]
                co2 = modules[adj_list].air[4]
                n2 = modules[adj_list].air[5]
                usv = modules[adj_list].air[6]
                i.mix(temp, hum, hpa, o2, co2, n2, usv)

        # IaC functions for modules (runs based on IaC)
            #to be added if statements based on IaC code caling for devices and their power consumption

        # PowerFuel functions (runs always, some will be based on simulation inputs or IaC)
        power.solar(loop_entropy, orbit, solar_shadow)
        power.battery()
        power.weight()

        # PowerFuel functions (examples that will be called by IaC)
        # power.fuel(100)               # burns 100 kg of fuel
        # power.consumption_on(100)     # starts using 100 W of power
        # power.emergency_battery()     # starts discharging emergency battery to meet power demand (counts on dead main battery)

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
            print('____DOORS____')
            print('no.   Belongs to      Adjacent to')
            for i in doors:
                print(str(i.door_id) + '\t\t' + i.belongs_to + '\t\t\t' + i.adjacent_to)
