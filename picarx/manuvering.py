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



if __name__ == "__main__":
    px = Picarx()
    straight_line(px, 90, 20, 2.0)
