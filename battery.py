class BatteryCell:
    def __init__(self, max_capacity):
        self.max_capacity = max_capacity
        self.remaining_capacity = self.max_capacity

    def discharge(self, discharge_amount):
        self.remaining_capacity -= discharge_amount

    def full_recharge(self):
        self.remaining_capacity = self.max_capacity

    @property
    def voltage(self):
        return (11.1 / 3)

class BatteryPackBase:
    """Base class for battery packs"""
    def copy(self):
        raise NotImplementedError()

    def full_recharge(self):
        raise NotImplementedError()

    def discharge(self, discharge_amount):
        raise NotImplementedError()

    @property
    def voltage(self):
        raise NotImplementedError()

    @property
    def max_capacity(self):
        raise NotImplementedError()

    @property
    def remaining_capacity(self):
        raise NotImplementedError()

class BatteryBankBase:
    """Base class for battery banks"""

    @property
    def voltage(self):
        raise NotImplementedError()

    @property
    def remaining_capacity(self):
        raise NotImplementedError()

    @property
    def max_capacity(self):
        raise NotImplementedError()

    @property
    def charge_percentage(self):
        return self.remaining_capacity / self.max_capacity

    @property
    def weight(self):
        raise NotImplementedError()

    def full_recharge(self):
        raise NotImplementedError()

    def discharge(self, discharge_amount):
        """Discharge the bank by a total of discharge_amount Watt-Hours"""
        raise NotImplementedError()

    def draw(self, power, dt):
        """Draw power Watts for dt seconds"""
        current = power / self.voltage  # in Amps
        charge = current * (dt / 3600.0)  # in Watt-Hours
        self.discharge(charge)

class BatteryPack(BatteryPackBase):
    def __init__(self, cells_in_series, designed_max_capacity, weight):
        self.cells_in_series = cells_in_series
        self.designed_max_capacity = designed_max_capacity
        self.weight = weight

        cell_capacity = self.designed_max_capacity / self.cells_in_series
        self.cells = []
        for _ in range(cells_in_series):
            self.cells.append(BatteryCell(cell_capacity))

    def copy(self):
        return BatteryPack(self.cells_in_series, self.designed_max_capacity, self.weight)

    def full_recharge(self):
        for cell in self.cells:
            cell.full_recharge()

    def discharge(self, discharge_amount):
        cell_discharge_amount = discharge_amount / self.cells_in_series
        for cell in self.cells:
            cell.discharge(cell_discharge_amount)

    @property
    def voltage(self):
        voltage = 0.0

        for cell in self.cells:
            voltage += cell.voltage

        return voltage

    @property
    def max_capacity(self):
        max_capacity = 0.0

        for cell in self.cells:
            max_capacity += cell.max_capacity

        return max_capacity

    @property
    def remaining_capacity(self):
        remaining_capacity = 0.0

        for cell in self.cells:
            remaining_capacity += cell.remaining_capacity

        return remaining_capacity

class BatteryBank(BatteryBankBase):
    def __init__(self, pack, packs_in_series, packs_in_parallel):
        self.packs_in_series = packs_in_series
        self.packs_in_parallel = packs_in_parallel

        self.bank = []
        for _ in range(self.packs_in_parallel):
            series_bank = []

            for _ in range(self.packs_in_series):
                series_bank.append(pack.copy())

            self.bank.append(series_bank)

    @property
    def voltage(self):
        voltage_sum = 0

        for series_pack in self.bank:
            for pack in series_pack:
                voltage_sum += pack.voltage

        return voltage_sum / self.packs_in_parallel

    @property
    def remaining_capacity(self):
        remaining_capacity = 0

        for series_pack in self.bank:
            for pack in series_pack:
                remaining_capacity += pack.remaining_capacity

        # NOTE: I don't think this should be divided by packs_in_series
        return remaining_capacity / self.packs_in_series

    @property
    def max_capacity(self):
        max_capacity = 0

        for series_pack in self.bank:
            for pack in series_pack:
                max_capacity += pack.max_capacity

        # NOTE: I don't think this should be divided by packs_in_series
        return max_capacity / self.packs_in_series

    @property
    def weight(self):
        weight_sum = 0

        for series_pack in self.bank:
            for pack in series_pack:
                weight_sum += pack.weight

        return weight_sum

    def full_recharge(self):
        for series_pack in self.bank:
            for pack in series_pack:
                pack.full_recharge()

    def discharge(self, discharge_amount):
        """Discharge the bank by a total of discharge_amount Watt-Hours"""

        # NOTE: I think this should also be dividied by self.packs_in_series
        series_discharge_amount = discharge_amount / self.packs_in_parallel

        for series_pack in self.bank:
            for pack in series_pack:
                pack.discharge(series_discharge_amount)


class SimpleBatteryPack:
    """Battery pack with the assumption that each cell is the same

    This simplifies the code and improves performance, but has less flexibility"""
    def __init__(self, cells_in_series, designed_max_capacity, weight):
        self.cells_in_series = cells_in_series
        self.designed_max_capacity = designed_max_capacity
        self.weight = weight

        cell_capacity = self.designed_max_capacity / self.cells_in_series
        self.cell = BatteryCell(cell_capacity)

    def copy(self):
        return BatteryPack(self.cells_in_series, self.designed_max_capacity, self.weight)

    def full_recharge(self):
        self.cell.full_recharge()

    def discharge(self, discharge_amount):
        cell_discharge_amount = discharge_amount / self.cells_in_series
        self.cell.discharge(cell_discharge_amount)

    @property
    def voltage(self):
        return self.cell.voltage * self.cells_in_series

    @property
    def max_capacity(self):
        return self.cell.max_capacity * self.cells_in_series

    @property
    def remaining_capacity(self):
        return self.cell.remaining_capacity * self.cells_in_series


class SimpleBatteryBank(BatteryBankBase):
    """Battery bank with the assumption that each pack is the same.

    This simplifies the code and improves performance, but is less flexible
    """

    def __init__(self, pack, packs_in_series, packs_in_parallel):
        self.packs_in_series = packs_in_series
        self.packs_in_parallel = packs_in_parallel

        self.pack = pack

    @property
    def voltage(self):
        return self.pack.voltage * self.packs_in_series

    @property
    def remaining_capacity(self):
        # NOTE: I think this should be multiplied by self.packs_in_series
        # since the total charge should be the sum in all packs
        return self.pack.remaining_capacity * self.packs_in_parallel

    @property
    def max_capacity(self):
        # NOTE: I think this should be multiplied by self.packs_in_series
        # Since charge multiplies by all packs
        return self.pack.max_capacity * self.packs_in_parallel

    @property
    def weight(self):
        return self.pack.weight * self.packs_in_parallel * self.packs_in_series

    def full_recharge(self):
        self.pack.full_recharge()

    def discharge(self, discharge_amount):
        """Discharge the bank by a total of discharge_amount Watt-Hours"""

        # NOTE: I think this should also be dividied by self.packs_in_series
        series_discharge_amount = discharge_amount / self.packs_in_parallel

        self.pack.discharge(series_discharge_amount)
