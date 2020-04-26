class Generator:
    def __init__(self, weight, max_power, fuel_consumption, tank_capacity, fuel_density):
        self.weight = weight
        # g / Kw * h
        self.fuel_consumption = fuel_consumption

        # L
        self.tank_capacity = tank_capacity

        self.max_power = max_power

        # g/L
        self.fuel_density = fuel_density

        self.reset()

    def reset(self):
        self.remaining_tank = self.tank_capacity

    def get_weight(self):
        return self.weight + self.remaining_tank * self.fuel_density

    def generate(self, power_required, dt):
        # Don't allow power to exceed max power that the generator can put out.
        actual_power = min(power_required, self.max_power)

        fuel_required_grams = self.fuel_consumption * (actual_power / 1000) * (dt / 3600)

        original_tank = self.remaining_tank
        self.remaining_tank -= fuel_required_grams / self.fuel_density
        self.remaining_tank = max(0, self.remaining_tank)

        actual_power = (original_tank - self.remaining_tank) * self.fuel_density / (self.fuel_consumption / 1000 * dt / 3600)

        return actual_power
