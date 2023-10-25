import RPi.GPIO as GPIO
import time

class Motor:
    def __init__(self, pin_dir, pin_step, vitesse):
        self.step_pin = pin_step
        self.dir_pin = pin_dir

        self.vitesse = vitesse
        self.deg_per_step = 1.8  # for full-step drive
        self.steps_per_rev = int(360 / self.deg_per_step)  # 200
        self.step_angle = 0 # angle initial


        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.step_pin, GPIO.OUT)
        GPIO.setup(self.dir_pin, GPIO.OUT)

    def move_step(self, pas):
        if pas > 0:
            direction = 1
        else:
            direction = 0
            pas = (-1)*pas
        GPIO.output(self.dir_pin, direction)
        
        for i in range(pas):
            GPIO.output(self.step_pin, GPIO.HIGH)
            time.sleep(self.vitesse)
            GPIO.output(self.step_pin, GPIO.LOW)
            time.sleep(self.vitesse)

    def move_angle(self, angle):
        angle_to_pas = int(angle/self.deg_per_step)
        self.move_step(angle_to_pas)
        

if __name__ == "__main__":
    mtr = Motor(27,17,0.001)
    mtr.move_angle(200)
    time.sleep(5)
    mtr.move_angle(-200)
    print('cleanup')
    GPIO.cleanup()

        
