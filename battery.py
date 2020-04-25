class BatteryCell:
    def __init__(self, max_capacity):
        self.max_capacity = max_capacity
        self.remaining_capacity = self.max_capacity

    def discharge(self, discharge_amount):
        self.remaining_capacity -= discharge_amount

    def full_recharge(self):
        self.remaining_capacity = self.max_capacity

    def get_voltage(self):
        return (11.1 / 3)

    def get_remaining_capacity(self):
        return self.remaining_capacity

class BatteryPack:
    def __init__(self, cells_in_series, max_capacity, weight):
        self.cells_in_series = cells_in_series
        self.max_capacity = max_capacity
        self.weight = weight

        self.cells = []
        for _ in range(cells_in_series):
            self.cells.append(BatteryCell(max_capacity))

    def copy(self):
        return BatteryPack(self.cells_in_series, self.max_capacity, self.weight)

    def full_recharge(self):
        for cell in self.cells:
            cell.full_recharge()

    def discharge(self, discharge_amount):
        for cell in self.cells:
            cell.discharge(discharge_amount)

    def get_weight(self):
        return self.weight

    def get_voltage(self):
        voltage = 0.0

        for cell in self.cells:
            voltage += cell.get_voltage()

        return voltage

    def get_max_capacity(self):
        max_capacity = 0.0

        for cell in self.cells:
            max_capacity += cell.max_capacity

        return max_capacity / self.cells_in_series

    def get_remaining_capacity(self):
        remaining_capacity = 0.0

        for cell in self.cells:
            remaining_capacity += cell.get_remaining_capacity()

        return remaining_capacity / self.cells_in_series

class BatteryBank:
    def __init__(self, pack, packs_in_series, packs_in_parallel):
        self.packs_in_series = packs_in_series
        self.packs_in_parallel = packs_in_parallel

        self.bank = []
        for _ in range(self.packs_in_parallel):
            series_bank = []

            for _ in range(self.packs_in_series):
                series_bank.append(pack.copy())

            self.bank.append(series_bank)

    def get_voltage(self):
        voltage_sum = 0

        for series_pack in self.bank:
            for pack in series_pack:
                voltage_sum += pack.get_voltage()

        return voltage_sum / self.packs_in_parallel

    def get_remaining_capacity(self):
        remaining_capacity = 0

        for series_pack in self.bank:
            for pack in series_pack:
                remaining_capacity += pack.get_remaining_capacity()

        return remaining_capacity / self.packs_in_series

    def get_max_capacity(self):
        max_capacity = 0

        for series_pack in self.bank:
            for pack in series_pack:
                max_capacity += pack.get_max_capacity()

        return max_capacity / self.packs_in_series

    def get_charge_percentage(self):
        return self.get_remaining_capacity() / self.get_max_capacity()

    def get_weight(self):
        weight_sum = 0

        for series_pack in self.bank:
            for pack in series_pack:
                weight_sum += pack.get_weight()

        return weight_sum

    def full_recharge(self):
        for series_pack in self.bank:
            for pack in series_pack:
                pack.full_recharge()

    def discharge(self, discharge_amount):
        series_discharge_amount = discharge_amount / self.packs_in_parallel

        for series_pack in self.bank:
            for pack in series_pack:
                pack.discharge(series_discharge_amount)
