from picarx_improved import Picarx
import time
import logging

logging_format = "%(asctime)s: %(message)s"
logging.basicConfig(format=logging_format, level = logging.INFO, datefmt="%H:%M:%S")
logging.getLogger().setLevel(logging.DEBUG)

class Sense():
    def __init__(self):
        self.px = Picarx()
    
    def get_grayscale(self):
        return self.px.grayscale.read()

class Interpret():
    def __init__(self, range = [0, 3600], polarity = False):
        ''' Initialize Interpreter
        
        param range: Indicates range of acceptable light -> dark values
        type range: list[int, int]
        param polarity: False indicates light floor, dark line, True indicates dark floor, light line
        type polarity: Bool      
        '''
        self.low_range, self.high_range = range
        self.polarity = polarity
        self.robot_location = 0
    
    def line_location(self, grayscale_values):
        if self.polarity:
            grayscale_values = [grayscale_value - min(grayscale_values) for grayscale_value in grayscale_values] 
        else:
            grayscale_values = [abs(grayscale_value - max(grayscale_values)) for grayscale_value in grayscale_values] 

        left, middle, right = grayscale_values
        logging.debug(f'MODIFIED - Left: {left}, Middle: {middle}, Right: {right}')

        try:
            if left > right:
                self.robot_location = (middle - left)/max(left, middle)
                if self.robot_location < 0:
                    self.robot_location = abs(self.robot_location)
                    return
                self.robot_location = 1-self.robot_location
                return
            self.robot_location = (middle-right)/max(middle, right)
            if self.robot_location < 0:
                return
            self.robot_location -= 1
            return
        except:
            logging.debug(f'Divide by zero error, continuing')

    def robot_position(self):
        logging.debug(f'Robot Location: {self.robot_location}')
        return self.robot_location

class Control():
    def __init__(self, k_p = 10.0, k_i = 0.0, threshold = 0.15):
        self.k_p = k_p
        self.k_i = k_i
        self.threshold = threshold
        self.error = 0.0
        self.angle = 0.0
    
    def steer(self, px, car_position):
        if abs(car_position) > self.threshold:
            self.error += car_position
            self.angle = self.k_p * car_position + self.error * self.k_i
            logging.debug(f'Steering Angle: {self.angle}')
            px.set_dir_servo_angle(self.angle)
            return self.angle
        self.angle = 0
        logging.debug(f'Steering Angle: {self.angle}')
        px.set_dir_servo_angle(self.angle)
        return self.angle

if __name__ == "__main__":
    sense = Sense()
    think = Interpret(polarity = True)
    control = Control()
    while True:
        think.line_location(sense.get_grayscale())
        robot_position = think.robot_position()
        control.steer(sense.px, robot_position)
