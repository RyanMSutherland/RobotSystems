from picarx_improved import Picarx
from vilib import Vilib
import time
import logging
import numpy as np
import cv2

logging_format = "%(asctime)s: %(message)s"
logging.basicConfig(format=logging_format, level = logging.INFO, datefmt="%H:%M:%S")
logging.getLogger().setLevel(logging.DEBUG)

class Sense():
    def __init__(self, camera = False):
        self.px = Picarx()
        self.reference = np.array(self.px.grayscale._reference)
        if camera:
            Vilib.camera_start()
            time.sleep(0.5)
            #Vilib.display()
            self.path = "picarx"
            self.image_name = "image"
            self.px.set_cam_tilt_angle(-30)
    
    def get_grayscale(self):
        return np.array(self.px.grayscale.read()) - self.reference
    
    def take_photo(self):
        logging.debug("Photo Taken")
        Vilib.take_photo(photo_name = self.image_name, path = self.path)

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
    
    def line_location_grayscale(self, grayscale_values):
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
                    self.robot_location = self.robot_location
                    return
                self.robot_location -= 1
                return
            self.robot_location = (middle-right)/max(middle, right)
            if self.robot_location < 0:
                self.robot_location = -1*self.robot_location
                return
            self.robot_location = 1-self.robot_location
            return
        except:
            logging.debug(f'Divide by zero error, continuing')

    def line_location_camera(self, path, image_name):
        gray_img = cv2.imread(f'{path}/{image_name}.jpg')
        gray_img = cv2.cvtColor(gray_img, cv2.COLOR_BGR2GRAY)
        print(gray_img)

    def robot_position(self):
        logging.debug(f'Robot Location: {self.robot_location}')
        return self.robot_location

class Control():
    def __init__(self, k_p = 30.0, k_i = 0.0, threshold = 0.15):
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
    sense = Sense(camera=True)
    think = Interpret(polarity = False)
    control = Control()
    time.sleep(2)
    sense.take_photo()
    think.line_location_camera(sense.path, sense.image_name)
    # sense.px.forward(20)
    # while True:
    #     think.line_location_grayscale(sense.get_grayscale())
    #     robot_position = think.robot_position()
    #     control.steer(sense.px, robot_position)
