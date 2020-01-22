#!/usr/bin/env python3
#!LD_PRELOAD=/usr/lib/arm-linux-gnueabihf/libatomic.so.1 python3

import sys
import socket
import pigpio
import time
import cv2
import base64
import zlib
import zmq
import numpy as np

sys.path.append('/usr/lib/python3/dist-packages')
# remember to run pigpio daemon!

HOST = ''  # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)

xAxis = 0
yAxis = 0
zAxis = 0
throttle = 0

xServo = 17
yServo = 27
zServo = 22
tServo = 23

exceptionAmount = 1

p = pigpio.pi()

p.set_mode(xServo, pigpio.OUTPUT)
p.set_mode(yServo, pigpio.OUTPUT)
p.set_mode(zServo, pigpio.OUTPUT)
p.set_mode(tServo, pigpio.OUTPUT)

p.set_PWM_frequency(xServo, 50)
p.set_PWM_frequency(yServo, 50)
p.set_PWM_frequency(zServo, 50)
p.set_PWM_frequency(tServo, 50)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


s.bind((HOST, PORT))
s.listen()
print("Listening...")
conn, addr = s.accept()

video = cv2.VideoCapture("sample.mp4")

with conn:
    print('Connected by', addr)

    flag = True

    while flag:
        startTime = time.time()
        data = conn.recv(1024)
        # time.sleep(0.01)

        string = str(data, 'utf-8')
        strings = string.split()
        try:
            ret, frame = video.read()
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            frame = cv2.resize(frame, (427, 240))
            # frame = cv2.resize(frame, (1280, 720))
            sizeBefore = sys.getsizeof(frame)

            encoded, buf = cv2.imencode(".jpg", frame)
            image = base64.b64encode(buf)
            sizeAfter = sys.getsizeof(image)
            print("Size before: ", sizeBefore)
            print("Size After: ", sizeAfter)

            # image_string = str(image, 'utf-8')
            # compressedImage = zlib.compress(image)
            # size = sys.getsizeof(compressedImage)




        except:
            print("Video exception")

        try:

            if string == "q":

                print("Shutting down!....")
                flag = False
            if strings[0] == "control":
                xAxis = float(strings[1])  # converting to float
                yAxis = float(strings[2])
                zAxis = float(strings[3])
                throttle = float(strings[4])

            if strings[0] == "f":
                p.set_PWM_dutycycle(xServo, 0)
                p.set_PWM_dutycycle(yServo, 0)
                p.set_PWM_dutycycle(zServo, 0)
        except:
            print("Corrupt data, continuing program if flag is still true - flag state: ", str(flag) + " Amount of corrupted data packets:  ", exceptionAmount)
            exceptionAmount = exceptionAmount + 1

        # print("--------------")
        # print("****", xAxis, "****")
        # print(yAxis, "******", zAxis)

        try:
            p.set_servo_pulsewidth(xServo, xAxis)
            p.set_servo_pulsewidth(yServo, yAxis)
            p.set_servo_pulsewidth(zServo, zAxis)
            p.set_servo_pulsewidth(tServo, throttle)
        except KeyboardInterrupt:
            p.stop()

        # print(image)

        conn.sendall(image)
        # print(value)
        # conn.sendall(bytes("executed!", 'utf-8'))
        delay = time.time() - startTime
        # sleep = ((1 / 24) - delay % (1 / 24))
        # time.sleep(sleep)
        tickTime = delay
        tickrate = 1 / tickTime
        print("tickTime: ", tickTime)
        print("tickrate: ", tickrate)

s.close()



