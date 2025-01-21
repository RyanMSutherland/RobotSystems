from picarx_improved import Picarx
import time

def straight_line(px, speed = 70, angle = 0, wait = 3.0):
    px.set_dir_servo_angle(angle)
    px.forward(speed)
    time.sleep(wait)

    px.stop()
    time.sleep(wait)

    px.backward(speed)
    time.sleep(wait)

def parallel_parking(px, speed = 70, wait = 1.5, left = False):
    turn_in_value = 15
    if left:
        turn_in_value *= -1
    px.set_dir_servo_angle(0)
    px.forward(speed)
    time.sleep(wait)

    px.set_dir_servo_angle(turn_in_value)
    px.backward(speed/2)
    time.sleep(wait*1.5)

    px.set_dir_servo_angle(-turn_in_value)
    time.sleep(wait*1.5)

    px.set_dir_servo_angle(0)
    px.forward(speed/2)
    time.sleep(wait*1.5)

    px.stop()

def k_turn(px, speed = 70, wait = 1.5, left = False):
    turn_in_value = 15
    if left: 
        turn_in_value *= -1

    px.set_dir_servo_angle(turn_in_value)
    px.forward(speed)
    time.sleep(wait)
    
    px.stop()
    time.sleep(wait/10)

    px.set_dir_servo_angle(-turn_in_value)
    px.backward(speed)
    time.sleep(wait)
    
    px.stop()
    time.sleep(wait/10)

    px.set_dir_servo_angle(turn_in_value)
    px.forward(speed)
    time.sleep(wait)
    
    px.stop()
    time.sleep(wait/10)

    px.set_dir_servo_angle(0)
    px.forward(speed)
    time.sleep(wait)

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
