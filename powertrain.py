import math
import numpy as np

class PowerCurveModel:
    def __init__(self, samples):
        # y = ax^b
        # log(y) = log(a) + b * log(x)
        samples_log = np.log(samples)
        x = samples_log[:,1]
        y = samples_log[:,0]

        # Take linear regression to find slope b and intercept ln(a)
        X = np.vstack([x, np.ones(len(y))]).T
        m, c = np.linalg.lstsq(X, y, rcond=None)[0]

        # Store the constants for the power curve fit.
        self.coefficient = math.exp(c)
        self.power = m

    def x_to_y(self, x):
        return self.coefficient * pow(x, self.power)

    def y_to_x(self, y):
        return pow((y / self.coefficient), 1 / self.power)

class Motor:
    def __init__(self, cost, voltage, model):
        self.cost = cost
        self.voltage = voltage
        self.thrust_to_power_model = model

class Powertrain:
    def __init__(self, motor, number_of_motors):
        self.motor = motor
        self.number_of_motors = number_of_motors

    def instantaneous_power(self, thrust):
        return self.number_of_motors * \
            self.motor.thrust_to_power_model.y_to_x(thrust / self.number_of_motors)

    def instantaneous_thrust(self, power):
        return self.number_of_motors * \
            self.motor.thrust_to_power_model.x_to_y(power / self.number_of_motors)


# print(hobbywing_xrotor_8120_motor_thrust_datapoints[:,0])
# x = np.linalg.lstsq(hobbywing_xrotor_8120_motor_thrust_datapoints)
# hobbywing_xrotor_8120_motor = Motor()