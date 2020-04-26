import numpy as np
import math

import battery
import generator
import powertrain
import drone

# MODEL PARAMETERS #############################################################

NUMBER_OF_MOTORS=6
FRAME_WEIGHT=8000
MIN_BATTERY_PERCENTAGE = 15
LIPO_CELL_VOLTAGE = 3.7
DT = 0.5

################################################################################

HOBBYWING_XROTOR_8120_DATAPOINTS = np.array([
    [2017, 145.3],
    [2985, 236.2],
    [3981, 352.6],
    [5027, 489.6],
    [5983, 643.2],
    [6999, 812.6],
    [7978, 973.4],
    [9006, 1171],
    [9990, 1345],
    [10983, 1577],
    [11975, 1768.2],
    [13007, 2010.4],
    [13956, 2291]
])

HOBBYWING_XROTOR_8120_MOTOR_MODEL = powertrain.PowerCurveModel(
    HOBBYWING_XROTOR_8120_DATAPOINTS)

HOBBYWING_XROTOR_8120_MOTOR = powertrain.Motor(
    236.15, 12 * LIPO_CELL_VOLTAGE, HOBBYWING_XROTOR_8120_MOTOR_MODEL)

NIST_PAYLOAD_WEIGHT=10 / 2.20462 * 1000

class DroneDesigner:
    def __init__(self):
        self.powertrain = powertrain.Powertrain(HOBBYWING_XROTOR_8120_MOTOR, NUMBER_OF_MOTORS)

        self.pack = battery.SimpleBatteryPack(
            cells_in_series=6,
            designed_max_capacity=5.,
            weight=716.
        )

        self.bank = battery.SimpleBatteryBank(
            pack=self.pack,
            packs_in_series=2,
            packs_in_parallel=4
        )

        # Generator:
        # https://www.droneassemble.com/product/drone-hybrid-generator-power-system-for-aerial-photography-planting-and-mapping-uav-long-flight-time-endurance/
        TANK_CAPACITY=2 #L
        FUEL_DENSITY=780 # g/L
        FUEL_CONSUMPTION_RATE=600 #g/kW * h
        MAX_GENERATE_POWER=2400 #W
        GENERATOR_WEIGHT=4500

        self.sim_generator = generator.Generator(
            weight=GENERATOR_WEIGHT,
            max_power=MAX_GENERATE_POWER,
            fuel_consumption=FUEL_CONSUMPTION_RATE,
            tank_capacity=TANK_CAPACITY,
            fuel_density=FUEL_DENSITY
        )

        self.sim_drone = drone.Drone(
            battery_bank=self.bank,
            powertrain=self.powertrain,
            generator=self.sim_generator,
            frame_weight=FRAME_WEIGHT,
            nist_payload_weight=NIST_PAYLOAD_WEIGHT
        )

        self.time = 0

    def reset(self):
        self.sim_drone.reset()
        self.time = 0

    def format_info(self, step_info):
        hours = (math.floor(self.time / 3600))
        minutes = (math.floor(self.time / 60)) % 60
        seconds = math.floor(self.time % 60)

        print_format = "{hours:02d}:{minutes:02d}:{seconds:02d}" \
            "  |  {remaining_capacity:.2f}Ah" \
            "  |  {charge_percentage:%}" \
            "  |  {power_draw:.1f} W total draw" \
            "  |  {thrust:.1f} kg" \
            "  |  {battery_power:.1f} W from battery" \
            "  |  {generator_power:.1f} W from generator" \
            "  |  {fuel_remaining:.1f} L fuel remaining"

        formatted = print_format.format(
            hours=hours,
            minutes=minutes,
            seconds=seconds,
            remaining_capacity=self.sim_drone.battery_bank.remaining_capacity,
            charge_percentage=self.sim_drone.battery_bank.charge_percentage,
            power_draw=step_info['total_power_draw'],
            thrust=step_info['thrust'] / 1000,
            battery_power=step_info['battery_power_draw'],
            generator_power=step_info['generator_power_draw'],
            fuel_remaining=self.sim_drone.generator.remaining_tank
        )
        return formatted

    def step(self):
        step_info = self.sim_drone.run_step(DT)

        if self.sim_drone.battery_bank.charge_percentage <= MIN_BATTERY_PERCENTAGE / 100:
            return None

        formatted = self.format_info(step_info)

        self.time += DT
        return formatted

    def run(self):
        self.reset()
        while True:
            formatted_info = self.step()
            if formatted_info is None:
                break
            print(formatted_info)


if __name__ == "__main__":
    DroneDesigner().run()
