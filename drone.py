class Drone:
    def __init__(self, battery_bank, powertrain, frame_weight, generator, nist_payload_weight):
        self.battery_bank = battery_bank
        self.powertrain = powertrain
        self.frame_weight = frame_weight
        self.generator = generator
        self.nist_payload_weight = nist_payload_weight

    def get_weight(self):
        """Get the current total weight of the drone (in grams)"""
        weight_sum = 0

        weight_sum += self.frame_weight
        weight_sum += self.battery_bank.weight
        weight_sum += self.generator.get_weight()
        weight_sum += self.nist_payload_weight

        return weight_sum

    def reset(self):
        self.battery_bank.full_recharge()
        self.generator.reset()

    def run_step(self, dt):
        weight = self.get_weight()
        thrust = 1.3 * weight

        # in Watts
        power_draw = self.powertrain.instantaneous_power(weight)
        # also in Watts
        generator_power = self.generator.generate(power_draw, dt)

        # Watts
        battery_power_draw = power_draw - generator_power
        self.battery_bank.draw(battery_power_draw, dt)

        return {
            'total_power_draw': power_draw,
            'battery_power_draw': battery_power_draw,
            'generator_power_draw': generator_power,
            'thrust': thrust 
        }
