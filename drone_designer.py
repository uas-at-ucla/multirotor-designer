import numpy as np
import math

import battery
import generator
import powertrain
import drone

# MODEL PARAMETERS #############################################################

NUMBER_OF_MOTORS=6
FRAME_WEIGHT=5000
MIN_BATTERY_PERCENTAGE = 15
LIPO_CELL_VOLTAGE = 3.7
DT = 0.5

TANK_CAPACITY=6 #L
FUEL_DENSITY=780 # g/L
FUEL_CONSUMPTION_RATE=750 #g/kW * h
MAX_GENERATE_POWER=5000 #W
GENERATOR_WEIGHT=7200
NIST_PAYLOAD_WEIGHT=10 / 2.20462 * 1000 + (645 + 85 + 180) * NUMBER_OF_MOTORS

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

powertrain = powertrain.Powertrain(HOBBYWING_XROTOR_8120_MOTOR, NUMBER_OF_MOTORS)

pack = battery.BatteryPack(
    cells_in_series=6,
    max_capacity=5.,
    weight=716.
)

bank = battery.BatteryBank(
    pack=pack,
    packs_in_series=2,
    packs_in_parallel=3
)

# Generator:
# https://www.droneassemble.com/product/drone-hybrid-generator-power-system-for-aerial-photography-planting-and-mapping-uav-long-flight-time-endurance/

sim_generator = generator.Generator(
    weight=GENERATOR_WEIGHT,
    max_power=MAX_GENERATE_POWER,
    fuel_consumption=FUEL_CONSUMPTION_RATE,
    tank_capacity=TANK_CAPACITY,
    fuel_density=FUEL_DENSITY
)


sim_drone = drone.Drone(
    battery_bank=bank,
    powertrain=powertrain,
    generator=sim_generator,
    frame_weight=FRAME_WEIGHT,
    nist_payload_weight=NIST_PAYLOAD_WEIGHT
)

time = 0
while True:
    step_info = sim_drone.run_step(DT)

    if sim_drone.battery_bank.get_charge_percentage() <= MIN_BATTERY_PERCENTAGE / 100:
        break

    hours = (math.floor(time / 3600))
    minutes = (math.floor(time / 60)) % 60
    seconds = math.floor(time % 60)

    print_format = "{hours:02d}:{minutes:02d}:{seconds:02d}" \
        "  |  {remaining_capacity:.2f}Ah" \
        "  |  {charge_percentage:%}" \
        "  |  {power_draw:.1f} W total draw" \
        "  |  {weight:.1f} kg weight" \
        "  |  {thrust:.1f} kg thrust" \
        "  |  {battery_power:.1f} W from battery" \
        "  |  {generator_power:.1f} W from generator" \
        "  |  {fuel_remaining:.1f} L fuel remaining"

    time += DT

    # formatted = print_format.format(
    #     time=time,
    #     remaining_capacity=sim_drone.battery_bank.get_remaining_capacity(),
    #     charge_percentage=sim_drone.battery_bank.get_charge_percentage(),
    #     power_draw=step_info['total_power_draw'],
    #     weight=sim_drone.get_weight() / 1000,
    #     thrust=step_info['thrust'] / 1000,
    #     battery_power=step_info['battery_power_draw'],
    #     generator_power=step_info['generator_power_draw'],
    #     fuel_remaining=sim_drone.generator.remaining_tank
    # )

    formatted = print_format.format(
        hours=hours,
        minutes=minutes,
        seconds=seconds,
        remaining_capacity=sim_drone.battery_bank.get_remaining_capacity(),
        charge_percentage=sim_drone.battery_bank.get_charge_percentage(),
        power_draw=step_info['total_power_draw'],
        weight=sim_drone.get_weight() / 1000,
        thrust=step_info['thrust'] / 1000,
        battery_power=step_info['battery_power_draw'],
        generator_power=step_info['generator_power_draw'],
        fuel_remaining=sim_drone.generator.remaining_tank
    )
    print(formatted)
