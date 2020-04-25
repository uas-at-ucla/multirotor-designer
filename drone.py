class Drone:
    def __init__(self, battery_bank, powertrain, frame_weight, generator, nist_payload_weight):
        self.battery_bank = battery_bank
        self.powertrain = powertrain
        self.frame_weight = frame_weight
        self.generator = generator
        self.nist_payload_weight = nist_payload_weight

    def get_weight(self):
        weight_sum = 0

        weight_sum += self.frame_weight
        weight_sum += self.battery_bank.get_weight()
        weight_sum += self.generator.get_weight()
        weight_sum += self.nist_payload_weight

        return weight_sum

    def run_step(self, dt):
        weight = self.get_weight()
        thrust = 1.3 * weight

        power_draw = self.powertrain.instantaneous_power(weight)
        generator_power = self.generator.generate(power_draw, dt)

        battery_power_draw = power_draw - generator_power
        amps_required = battery_power_draw / self.battery_bank.get_voltage()
        amp_hours_required = amps_required * dt / 3600
        self.battery_bank.discharge(amp_hours_required)

        return {
            'total_power_draw': power_draw,
            'battery_power_draw': battery_power_draw,
            'generator_power_draw': generator_power,
            'thrust': thrust 
        }
