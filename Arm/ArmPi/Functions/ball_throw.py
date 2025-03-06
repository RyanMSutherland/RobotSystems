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

class Ball_Throw(Perception):
    def __init__(self):
        super().__init__()
        self.possible_colour_values = {'orange': (0, 165, 255),
                                       'black': (0, 0, 0)}
        self.color_range = {'orange': [(0, 151, 100), (255, 255, 255)],
                            'black': [(0, 0, 0), (56, 255, 255)], 
                            'white': [(193, 0, 0), (255, 250, 255)]}
        self.target_color = ('orange')
        self.color_to_number = {"orange" : 1}
        self.number_to_color = {1 : "orange"}
        self.gripper_open = 280
        self.gripper_closed = 500
        self.minimum_contour_thresh = 2500
        self.sleep_time = 0.5
        self.arm_kinematics = ArmIK()
        self.servo_1_id = 1
        self.servo_2_id = 2
        self.currently_moving = False
        self.sleep_divider = 1000
        self.desired_approach_height_grasp = 7
        self.desired_final_height_grasp = 1.0
        self.throw_height = 30.0
    
    def find_ball(self):
        # We will need to thread this
        self.find_objects()

    def throw_ball(self):
        current_colour = 'None'
        self.set_led_colour(current_colour)
        time.sleep(3*self.sleep_time)     
        while True:
            if self.current_colour != "None":
                current_colour = self.current_colour
                self.set_led_colour(current_colour)

                desired_x, desired_y, desired_angle = self.last_x, self.last_y, self.rotation_angle
                result = self.arm_kinematics.setPitchRangeMoving((desired_x, desired_y, self.desired_approach_height_grasp), -90, -90, 0)  

                if result:
                    time.sleep(result[2]/self.sleep_divider)

                    block_rotation = getAngle(desired_x, desired_y, desired_angle)
                    Board.setBusServoPulse(self.servo_1_id, self.gripper_closed - self.gripper_open, self.gripper_closed)
                    Board.setBusServoPulse(self.servo_2_id, block_rotation, self.gripper_closed)
                    time.sleep(self.sleep_time)

                    self.arm_kinematics.setPitchRangeMoving((desired_x, desired_y, self.desired_final_height_grasp), -90, -90, 0, 1000)
                    time.sleep(self.sleep_time)

                    Board.setBusServoPulse(self.servo_1_id, self.gripper_closed, self.gripper_closed)
                    time.sleep(self.sleep_time)

                    Board.setBusServoPulse(self.servo_2_id, self.gripper_closed, self.gripper_closed)
                    self.arm_kinematics.setPitchRangeMoving((0, 30, self.desired_approach_height_grasp*3), -90, -90, 0, 200)


                    # Board.setBusServoPulse(self.servo_2_id, self.gripper_closed, self.gripper_closed)
                    # self.arm_kinematics.setPitchRangeMoving((0, -5, 10), -90, -90, 0, 1000)
                    
                    Board.setBusServoPulse(self.servo_1_id, self.gripper_closed - self.gripper_open, self.gripper_closed)
                    time.sleep(self.sleep_time)

                    self.move_home()

                    current_colour = 'None'
                    self.set_led_colour(current_colour)
                    time.sleep(3*self.sleep_time)                    

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

    t1 = threading.Thread(target=ball_throw.find_ball)
    t2 = threading.Thread(target=ball_throw.throw_ball)

    t1.start()
    t2.start()