#!/usr/bin/env python3
import socket
from threading import Thread
import pigpio
import time
import cv2
import base64
from picamera import PiCamera
from picamera.array import PiRGBArray


# remember to run pigpio daemon!

# Setting socket connection
HOST = '192.168.7.130'  # Standard loopback interface address (localhost)
PORT = 65432       # Port to listen on (non-privileged ports are > 1023)
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = (HOST, PORT)
s.connect(server_address)

# Initiating different axis
xAxis = 0
yAxis = 0
zAxis = 0
throttle = 0

# setting servo pins
xServo = 17
yServo = 27
zServo = 22
tServo = 23

# Making pigpio instance
p = pigpio.pi()

# Setting gpio pins output mode
p.set_mode(xServo, pigpio.OUTPUT)
p.set_mode(yServo, pigpio.OUTPUT)
p.set_mode(zServo, pigpio.OUTPUT)
p.set_mode(tServo, pigpio.OUTPUT)

# setting gpio pins frequency
p.set_PWM_frequency(xServo, 50)
p.set_PWM_frequency(yServo, 50)
p.set_PWM_frequency(zServo, 50)
p.set_PWM_frequency(tServo, 50)


class PiVideoStream:
    def __init__(self, resolution=(368, 240), framerate=24):
        self.camera = PiCamera()
        self.camera.resolution = resolution
        self.camera.framerate = framerate
        self.rawCapture = PiRGBArray(self.camera, size=resolution)
        self.stream = self.camera.capture_continuous(self.rawCapture, format="bgr", use_video_port=True)

        self.frame = None
        self.stopped = False

    def start(self):

        Thread(target=self.update, args=()).start()
        return self

    def update(self):

        for f in self.stream:
            self.frame = f.array
            self.rawCapture.truncate(0)

            if self.stopped:
                self.stream.close()
                self.rawCapture.close()
                self.camera.close()
                return

    def read(self):
        return self.frame

    def stop(self):
        self.stopped = True


mainStream = 0
run_once = 0
fps = 1
frames = 1

vs = PiVideoStream().start()
time.sleep(2)

prevImage = None
flag = True
while flag:
    startTime = time.time()

    frame = vs.read()
    encoded, buf = cv2.imencode(".jpg", frame)
    image = base64.b64encode(buf)
    imageString = str(image, 'utf-8')
    image = "image " + imageString
    image = bytes(image, 'utf-8')


    if image != prevImage:
        s.sendto(image, server_address)
        prevImage = image[:]
    else:
        s.sendto(b'nothing', server_address)

    data, server = s.recvfrom(1024)

    string = str(data, 'utf-8')
    strings = string.split()

    try:

        if string == "q":
            s.close()
            vs.stop()
            flag = False
            print("Shutting down!....")
        if strings[0] == "control":
            xAxis = float(strings[1])  # converting to float
            yAxis = float(strings[2])
            zAxis = float(strings[3])
            throttle = float(strings[4])

    except:
        print("Corrupt data, continuing program if flag is still true - flag state: ", str(flag) + " Amount of corrupted data packets:  ", exceptionAmount)
        exceptionAmount = exceptionAmount + 1

    try:
        p.set_servo_pulsewidth(xServo, xAxis)
        p.set_servo_pulsewidth(yServo, yAxis)
        p.set_servo_pulsewidth(zServo, zAxis)
        p.set_servo_pulsewidth(tServo, throttle)
    except KeyboardInterrupt:
        print("Servo adjustment exception")


    delay = time.time() - startTime
    # sleep = ((1 / 24) - delay % (1 / 24))
    # time.sleep(sleep)
    tickTime = delay
    tickrate = 1 / tickTime
    # print("tickTime: ", tickTime)

    frames += 1
    fps += tickrate
    realFps = fps / frames
    # print("tickrate: ", tickrate)
    print("fps: ", realFps)
    mainStream += 1
    print("Main: ", mainStream)
