from picarx_improved import Picarx
import time
import logging

logging_format = "%(asctime)s: %(message)s"
logging.basicConfig(format=logging_format, level = logging.INFO, datefmt="%H:%M:%S")
logging.getLogger().setLevel(logging.DEBUG)

def straight_line(px, speed = 70, angle = 0, wait = 3.0):
    logging.debug(f'Setting angle to {angle} at speed {speed} for {wait} seconds')
    px.set_dir_servo_angle(angle)
    px.forward(speed)
    time.sleep(wait)

    px.stop()
    time.sleep(wait)

    logging.debug(f'Setting angle to {angle} at speed {speed} for {wait} seconds')
    px.set_dir_servo_angle(-angle)
    px.backward(speed)
    time.sleep(wait)

    logging.debug("Stopping")
    px.stop()

def parallel_parking(px, speed = 70, wait = 1.5, left = False):
    turn_in_value = 15
    if left:
        turn_in_value *= -1

    logging.debug(f'Setting angle to {0} at speed {speed} for {wait} seconds')
    px.set_dir_servo_angle(0)
    px.forward(speed)
    time.sleep(wait)

    logging.debug(f'Setting angle to {turn_in_value} at speed {speed/2} for {wait*1.5} seconds')
    px.set_dir_servo_angle(turn_in_value)
    px.backward(speed/2)
    time.sleep(wait*1.5)

    logging.debug(f'Setting angle to {-turn_in_value} at speed {speed} for {wait*1.5} seconds')
    px.set_dir_servo_angle(-turn_in_value)
    time.sleep(wait*1.5)

    logging.debug(f'Setting angle to {0} at speed {speed/2} for {wait*1.5} seconds')
    px.set_dir_servo_angle(0)
    px.forward(speed/2)
    time.sleep(wait*1.5)

    logging.debug("Stopping")
    px.stop()

def k_turn(px, speed = 70, wait = 1.5, left = False):
    turn_in_value = 15
    if left: 
        turn_in_value *= -1

    logging.debug(f'Setting angle to {turn_in_value} at speed {speed} for {wait} seconds')
    px.set_dir_servo_angle(turn_in_value)
    px.forward(speed)
    time.sleep(wait)
    
    px.stop()
    time.sleep(wait/10)

    logging.debug(f'Setting angle to {-turn_in_value} at speed {speed} for {wait} seconds')
    px.set_dir_servo_angle(-turn_in_value)
    px.backward(speed)
    time.sleep(wait)
    
    px.stop()
    time.sleep(wait/10)

    logging.debug(f'Setting angle to {turn_in_value} at speed {speed} for {wait} seconds')
    px.set_dir_servo_angle(turn_in_value)
    px.forward(speed)
    time.sleep(wait)
    
    px.stop()
    time.sleep(wait/10)

    logging.debug(f'Setting angle to {0} at speed {speed} for {wait} seconds')
    px.set_dir_servo_angle(0)
    px.forward(speed)
    time.sleep(wait)

    logging.debug("Stopping")
    px.stop()

if __name__ == "__main__":
    px = Picarx()
    
    user_value = 0
    while user_value != 4:
        user_value = int(input("Please choose from the following options. 1 : Drive Forwawrd/Backwards. 2 : Parallel Parking. 3 : K-Turn. 4 : Quit \n"))
        if user_value == 1:
            straight_line(px)
        elif user_value == 2:
            parallel_parking(px, left = False)
        elif user_value == 3:
            k_turn(px, left = False)
