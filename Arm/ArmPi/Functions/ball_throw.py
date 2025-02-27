import sys
sys.path.append('/home/pi/ArmPi/')
import cv2
import time
import threading
from LABConfig import *
from ArmIK.Transform import *
from ArmIK.ArmMoveIK import *
import HiwonderSDK.Board as Board
from CameraCalibration.CalibrationConfig import *
from upgrade_perception import Perception
from upgrade_motion import Motion

class Ball_Throw(Perception):
    def __init__(self):
        super().__init__()
        self.possible_colour_values = {'orange': (255, 165, 0)}
        self.color_range = {'orange': [(100, 200, 0), (255, 128, 0)],
                            'black': [(0, 0, 0), (56, 255, 255)], 
                            'white': [(193, 0, 0), (255, 250, 255)]}
        self.gripper_open = 280
        self.gripper_closed = 500
        self.sleep_time = 0.5
        self.arm_kinematics = ArmIK()
        self.servo_1_id = 1
        self.servo_2_id = 2
    
    def find_ball(self):
        # We will need to thread this
        self.find_objects()

    def pickup_ball(self):
        pass

    def throw_ball(self):
        pass

    def process_region_of_interest(self, img_lab_color):
        self.best_contour = None
        self.best_contour_area = 0
        self.color_of_interest = None

        for color in self.color_range:
            if color in self.target_color:
                color_mask = cv2.inRange(img_lab_color, self.color_range[color][0], self.color_range[color][1]) # Find all values within given color range we want to analyze
                cleaned_image = cv2.morphologyEx(color_mask, cv2.MORPH_OPEN, np.ones(self.filter_kernal, np.uint8))
                cleaned_image = cv2.morphologyEx(cleaned_image, cv2.MORPH_CLOSE, np.ones(self.filter_kernal, np.uint8))
                contours = cv2.findContours(cleaned_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2] # Only give us the contours, don't care about the image or hierarchy

                try:
                    largest_contour = max(contours, key=cv2.contourArea)
                    largest_contour_area = cv2.contourArea(largest_contour)

                    if largest_contour_area > self.best_contour_area:
                        self.best_contour_area = largest_contour_area
                        self.best_contour = largest_contour
                        self.color_of_interest = color
                except:
                    continue

    def set_led_colour(self, colour):
        if colour == "orange":
            Board.RGB.setPixelColor(0, Board.PixelColor(255, 128, 0))
            Board.RGB.setPixelColor(1, Board.PixelColor(255, 128, 0))
            Board.RGB.show()
        else:
            Board.RGB.setPixelColor(0, Board.PixelColor(0, 0, 0))
            Board.RGB.setPixelColor(1, Board.PixelColor(0, 0, 0))
            Board.RGB.show()
    
    def move_home(self):
        Board.setBusServoPulse(1, self.gripper_closed - 50, self.gripper_open)
        Board.setBusServoPulse(2, self.gripper_closed, self.gripper_closed)
        self.arm_kinematics.setPitchRangeMoving((0, 10, 10), -30, -30, -90, 1500)
        time.sleep(self.sleep_time)

if __name__ == "__main__":
    ball_throw = Ball_Throw()
    ball_throw.find_ball()