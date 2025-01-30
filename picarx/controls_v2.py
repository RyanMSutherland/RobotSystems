from picarx_improved import Picarx
from vilib import Vilib
import time
import logging
import numpy as np
import cv2
import concurrent.futures
from readerwriterlock import rwlock

logging_format = "%(asctime)s: %(message)s"
logging.basicConfig(format=logging_format, level = logging.INFO, datefmt="%H:%M:%S")
logging.getLogger().setLevel(logging.DEBUG)

class Sense():
    def __init__(self, px, sense_interpret_bus, sense_delay = 0.1, camera = False):
        self.px = px
        self.sense_interpret_bus = sense_interpret_bus
        self.sense_delay = sense_delay
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
        while True:
            logging.debug("Photo Taken")
            Vilib.take_photo(photo_name = self.image_name, path = self.path)
            self.sense_interpret_bus.write(f'{self.path}/{self.image_name}')
            time.sleep(self.sense_delay)
    
    def set_grayscale(self):
        while True:
            self.sense_interpret_bus.write(self.get_grayscale())
            time.sleep(self.sense_delay)

class Interpret():
    def __init__(self, sense_interpret_bus, interpret_control_bus, sense_delay = 0.1, control_delay = 0.1, range = [0, 3600], polarity = False):
        ''' Initialize Interpreter
        
        param range: Indicates range of acceptable light -> dark values
        type range: list[int, int]
        param polarity: False indicates light floor, dark line, True indicates dark floor, light line
        type polarity: Bool      
        '''
        self.low_range, self.high_range = range
        self.polarity = polarity
        self.sense_interpret_bus = sense_interpret_bus
        self.interpret_control_bus = interpret_control_bus
        self.sense_delay = sense_delay
        self.control_delay = control_delay
        self.robot_location = 0
        self.thresh = 75
        self.colour = 255
        self.img_start = 350
        self.img_cutoff = 425
    
    def line_location_grayscale(self):
        while True:
            try:
                grayscale_values = self.sense_interpret_bus.read()
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
                time.sleep(sense_delay)
            except:
                logging.debug(f'Grayscale not initialized, passing')
                time.sleep(sense_delay)

    def line_location_camera(self):
        while True:
            logging.debug("About to request grayscale")
            file_name = self.sense_interpret_bus.read()
            gray_img = cv2.imread(f'{file_name}.jpg')
            gray_img = cv2.cvtColor(gray_img, cv2.COLOR_BGR2GRAY)
            gray_img = gray_img[self.img_start:self.img_cutoff, :]
            _, img_width = gray_img.shape
            img_width /= 2
            if self.polarity:
                _, mask = cv2.threshold(gray_img, thresh = self.thresh, maxval=self.colour, type = cv2.THRESH_BINARY)
            else:
                _, mask = cv2.threshold(gray_img, thresh = self.thresh, maxval=self.colour, type = cv2.THRESH_BINARY_INV)
            
            try:
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                largest_contour = max(contours, key=cv2.contourArea)
                M = cv2.moments(largest_contour)
            except:
                logging.debug("NO CONTOUR FOUND")
                time.sleep(self.sense_delay)
                return 

            if M['m00'] != 0:
                # cx = int(M['m10']/M['m00'])
                # cy = int(M['m01']/M['m00'])
                self.robot_location = (int(M['m10']/M['m00']) - img_width)/img_width
                # cv2.circle(gray_img, (cx, cy), 5, (0, 0, 255), -1)
            # cv2.imshow("Gray", gray_img)
            # cv2.waitKey(0)
            #cv2.destroyAllWindows()
            time.sleep(self.sense_delay)

    def robot_position(self):
        while True:
            self.interpret_control_bus.write(self.robot_location)
            logging.debug(f'Robot Location: {self.robot_location}')
            time.sleep(self.control_delay)

class Control():
        def __init__(self, px, interpret_control_bus, control_delay = 0.1, k_p = 30, k_i = 0.0, threshold = 0.1):
            self.px = px
            self.k_p = k_p
            self.k_i = k_i
            self.threshold = threshold
            self.interpret_control_bus = interpret_control_bus
            self.control_delay = control_delay
            self.error = 0.0
            self.angle = 0.0
    
        def steer(self):
            while True:
                car_position = self.interpret_control_bus.read()
                if abs(car_position) > self.threshold:
                    self.error += car_position
                    self.angle = self.k_p * car_position + self.error * self.k_i
                    logging.debug(f'Steering Angle: {self.angle}')
                    self.px.set_dir_servo_angle(self.angle)
                    break
                else:
                    self.angle = 0
                    logging.debug(f'Steering Angle: {self.angle}')
                    self.px.set_dir_servo_angle(self.angle)
                time.sleep(self.control_delay)

class Bus():
    def __init__(self):
        self.message = None
        self.lock = rwlock.RWLockWriteD()

    def write(self, message):
        with self.lock.gen_wlock():
            self.message = message
            logging.debug(f'Write message: {self.message}')

    def read(self):
        with self.lock.gen_rlock():
            logging.debug(f'Read message: {self.message}')
            return self.message

if __name__ == "__main__":
    method = 0
    px = Picarx()
    while method != 1 and method != 2:
        method = int(input("Select 1 for grayscale or 2 for camera based line following: "))
    
    sense_interpret_bus = Bus()
    interpret_control_bus = Bus()

    sense_delay = 0.2
    control_delay = 0.2

    sense = Sense(px = px, sense_interpret_bus=sense_interpret_bus, sense_delay=sense_delay, camera = False)
    think = Interpret(sense_interpret_bus=sense_interpret_bus, interpret_control_bus=interpret_control_bus, 
                      sense_delay = sense_delay, control_delay = control_delay, polarity = False)
    control = Control(interpret_control_bus=interpret_control_bus, control_delay=control_delay, px = px, threshold = 0.1)

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        eSensor = executor.submit(sense.set_grayscale)
        eInterpreter = executor.submit(think.line_location_grayscale)
        eControl = executor.submit(control.steer)
    
    eSensor.result()
    eInterpreter.result()
    eControl.result()
    
    # if method == 1:
    #     sense = Sense(px = px, camera=False)
    #     think = Interpret(polarity = False)
    #     control = Control(px = px, threshold = 0.1)
    #     time.sleep(2)
    #     sense.px.forward(30)
    #     while True:
    #         think.line_location_grayscale(sense.get_grayscale())
    #         robot_position = think.robot_position()
    #         control.steer(robot_position)
    # elif method == 2:
    #     sense = Sense(camera=True)
    #     think = Interpret(polarity = False)
    #     control = Control(threshold = 0.05)
    #     time.sleep(2)
    #     sense.px.forward(30) 
    #     while True:
    #         sense.take_photo()
    #         think.line_location_camera(sense.path, sense.image_name)
    #         robot_position = think.robot_position()
    #         control.steer(robot_position)
