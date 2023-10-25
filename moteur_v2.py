import RPi.GPIO as GPIO
from enum import Enum
import time
import numpy as np
from itertools import product
from tqdm import tqdm

class Direction(Enum):
	COUNTERCLOCKWISE = 1
	CLOCKWISE = 0

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
    
	def set_direction(self, direction):
		GPIO.output(self.dir_pin, direction)
	
	def single_step(self):
		GPIO.output(self.step_pin, GPIO.HIGH)
		time.sleep(self.vitesse)
		GPIO.output(self.step_pin, GPIO.LOW)
		time.sleep(self.vitesse)

	def move_step(self, pas):
		if pas > 0:
			direction = 1
		else:
			direction = 0
			pas = (-1)*pas

		self.set_direction(direction)
		for i in range(pas):
			self.single_step()

		def move_angle(self, angle):
			angle_to_pas = int(angle/self.deg_per_step)
			self.move_step(angle_to_pas)
       
class TwoAxis:
	
	mm_per_step = 0.2
	pos_x = 0
	pos_y = 0
	
	def __init__(self, motor_1, motor_2):
		self.motor_1 = motor_1
		self.motor_2 = motor_2
		self.pos_x = 0
		self.pos_y = 0
	
	def move_step(self, steps, dir_1, dir_2):
		self.motor_1.set_direction(dir_1.value)
		self.motor_2.set_direction(dir_2.value)
		for i in range(steps):
			self.motor_1.single_step()
			self.motor_2.single_step()
	
	def move_mm(self, mm, dir_1, dir_2):
		steps = int(mm/self.mm_per_step)
		self.move_step(steps, dir_1, dir_2)
	
	def move_x(self, mm):
		if mm > 0:
			direction_1 = Direction.CLOCKWISE
			direction_2 = Direction.COUNTERCLOCKWISE
		else:
			direction_2 = Direction.CLOCKWISE
			direction_1 = Direction.COUNTERCLOCKWISE
			mm = (-1)*mm
		self.move_mm(mm, direction_1, direction_2)
		self.pos_x += mm

	def move_y(self, mm):
		if mm > 0:
			direction_1 = Direction.CLOCKWISE
			direction_2 = Direction.CLOCKWISE
		else:
			direction_2 = Direction.COUNTERCLOCKWISE
			direction_1 = Direction.COUNTERCLOCKWISE
			mm = (-1)*mm
		self.move_mm(mm, direction_1, direction_2)
		self.pos_y += mm
		
	def move_to(self, x, y):
		delta_x = x-self.pos_x
		delta_y = y-self.pos_y
		self.move_x(delta_x)
		self.move_y(delta_y)

if __name__ == "__main__":
	x = np.linspace(0,150,150+1)
	y = np.linspace(0,200,200+1)
	list_points = list(product(x,y))
		
	mtr = Motor(17,27,0.001)
	mtr2 = Motor(9,10,0.001)
	
	twoAxis = TwoAxis(mtr, mtr2)
	for p in tqdm(list_points):
		twoAxis.move_to(p[0], p[1])

	print('clean up')
	GPIO.cleanup()
	
