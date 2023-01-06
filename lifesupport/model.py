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
        self.sim_const = 39                    # simulation constant (for speeding/slowing simulation calculations)
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
    def mix(self, temp: float, hum: float, hpa: float, o2: float, co2: float, n2: float, usv: float):
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
        self.air[3] = self.air[3] + ((70 * entropy) / (self.size * self.sim_const))
        # self.air[2] = self.air[2] + ((5 * entropy) / (self.size * self.sim_const))
        return

    def carb_abs(self, entropy: float):     # carbon dioxide absorber
        self.air[4] = self.air[4] - ((30 * entropy) / (self.size * self.sim_const))
        if self.air[4] <= 0:
            self.air[4] = 0.01
        # self.air[2] = self.air[2] - ((5 * entropy) / (self.size * self.sim_const))
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
        self.connection_status = True

    def open(self):
        self.status = True

    def close(self):
        self.status = False

    def connect(self):
        self.status = True

    def disconnect(self):
        self.status = False

