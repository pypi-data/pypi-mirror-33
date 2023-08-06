import serial
from time import sleep
import serial.tools.list_ports as find_ports

__version__ = "1.0.1"

X_MOTOR = 0
Y_MOTOR = 1
Z_MOTOR = 2
MOTOR_TURN = 16 * 32 # steps
POSITIVE = 1
NEGATIVE = 0
MAX_STEPS = 32
STEP_TIME = 11e-3

def findPorts():
    ports = [port.device for port in find_ports.comports()]
    return ports

def getUserInput(label):
    while True:
        try:
            return int(input(label + ": "))
        except ValueError:
            pass

class Stage(serial.Serial):
    def __init__(self, port):
        super(Stage, self).__init__(port, baudrate = 9600)

    def make8Byte(self, steps, motor, direction):
        if steps > 32 or steps < 1:
            raise(ValueError("Wrong number of steps: %d. Range is 1 to 32."%steps))
        steps -= 1
        steps = (steps << 3)

        if motor > 2 or motor < 0:
            raise(ValueError("Wrong motor. Range is 0 to 2."))
        motor = motor << 1

        if direction > 1 or motor < 0:
            raise(ValueError("Wrong direction. Either is 0 or 1."))
        return steps | motor | direction

    def send(self, steps, motor, direction):
        global STEP_TIME
        number = self.make8Byte(steps, motor, direction)
        self.write([number])
        sleep(STEP_TIME * steps)

    def move(self, steps, motor, direction):
        global MAX_STEPS, STEP_TIME
        n_max = steps // MAX_STEPS
        remaining = steps % MAX_STEPS
        for i in range(n_max):
            self.send(MAX_STEPS, motor, direction)
        if remaining:
            self.send(remaining, motor, direction)

    def printB(self, number):
        print("{0:b}".format(number))
