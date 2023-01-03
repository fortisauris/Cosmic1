# Imports
from model import Crewmate, Module, Door
from power_fuel import PowerFuel
import random

"""
SPACESHIP CONSTRUCTOR   *runs once (simulation.py calls it by itself)
- specify each crew member according to crew class
-   'name', 
-   height [cm]
-   weight [kg]
- specify each module according to class Module
-   'name'
-   volume m^3
-   weight tones
-   [adjacent to, adjacent to, ...]
-   average crew members
-   base power draw
-   lights power draw
- specify the ships power system
-   'name of the ship'
-   maximum solar output [W]
-   main battery capacity [Wh]
-   emergency battery capacity [Wh]
-   main fuel tank capacity [metric tonnes]
-   emergency fuel tank capacity [metric tonnes]

* constructor is now as a part of code but it could be made via some UI 
"""

"""
___INPUTS___
"""
constructor_print = True    # Set to True to see all input parameters of our ship at the beginning of simulation

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

# Power system input
system = ['COSMIC1', 1000, 1500, 500, 5, 2]


"""
___CODE___
"""

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
power = PowerFuel(system[0], ship_base_weight, ship_base_draw, system[1], system[2], system[3], system[4], system[5])

# Recalculates weight at the start of simulation to account for fuel
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