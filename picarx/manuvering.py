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

def parallel_parking_left(px, speed = 70, wait = 0.25):
    turn_in_value = 15
    px.set_dir_servo_angle(0)
    px.forward(speed)
    time.sleep(wait)

    px.set_dir_servo_angle(turn_in_value)
    px.backward(speed/2)
    time.sleep(wait*2.0)

    px.set_dir_servo_angle(turn_in_value)
    time.sleep(wait*2.0)

    px.set_dir_servo_angle(0)
    px.forward(speed/2)
    time.sleep(wait*2.0)

    px.stop()


def parallel_parking_right():
    pass

if __name__ == "__main__":
    px = Picarx()
    # straight_line(px)
    parallel_parking_left(px)
