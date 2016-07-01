from datetime import datetime
import RPi.GPIO as GPIO
import threading
import select
import socket
import cv2
import time
import sys

class HaBonBon_DCMotor:

    pwm_frequency = 200

    def __init__(self, (right1, right2), (left1, left2)):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(right1, GPIO.OUT)
        GPIO.setup(right2, GPIO.OUT)
        GPIO.setup(left1, GPIO.OUT)
        GPIO.setup(left2, GPIO.OUT)
        self.right1_pwm = GPIO.PWM(right1, self.pwm_frequency)
        self.right1_pwm.start(0.0)
        self.left1_pwm = GPIO.PWM(left1, self.pwm_frequency)
        self.left1_pwm.start(0.0)
        self.right2 = right2
        self.left2 = left2
        GPIO.output(self.right2, False)
        GPIO.output(self.left2, False)

    def rightWheel(self, value):
        if value >= 0:
            self.right1_pwm.ChangeDutyCycle(value)
            GPIO.output(self.right2, False)
        else:
            self.right1_pwm.ChangeDutyCycle(100.0 + value)
            GPIO.output(self.right2, True)

    def leftWheel(self, value):
        if value >= 0:
            self.left1_pwm.ChangeDutyCycle(value)
            GPIO.output(self.left2, False)
        else:
            self.left1_pwm.ChangeDutyCycle(100.0 + value)
            GPIO.output(self.left2, True)

    def __del__(self):
        self.left1_pwm.stop()
        self.right1_pwm.stop()

class ControlClient(threading.Thread):

    def __init__(self, (client, address)):
        threading.Thread.__init__(self)
        self.client = client
        self.address = address
        self.running = 1
        self.lock = threading.Lock()
        log(self.address, "connect")

    def run(self):
        try:
            while self.running:
                self.lock.acquire()
                car.rightWheel(0.0)
                car.leftWheel(0.0)
                self.lock.release()

                data = self.client.recv(64)
                if not data:
                    self.client.close()
                    self.running = 0

                cmd = ''
                for char in data:
                    if char == '\n' or char == '\r':
                        break
                    cmd += char

                pre = ''
                self.lock.acquire()
                if cmd == 'forward':
                    car.rightWheel(40.0)
                    car.leftWheel(39.0)
                    time.sleep(0.1)
                elif cmd == 'backward':
                    car.rightWheel(-40.0)
                    car.leftWheel(-39.0)
                    time.sleep(0.1)
                else:
                    pre = 'unknown '
                self.lock.release()

                log(self.address, pre+'command: '+cmd.strip())
        except socket.error as e:
            pass
        self.client.close()
        log(self.address, "close")
