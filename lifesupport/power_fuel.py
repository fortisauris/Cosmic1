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
