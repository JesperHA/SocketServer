#!/usr/bin/env python3

import socket
import pigpio

HOST = ''  # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)

xAxis = 0
yAxis = 0
zAxis = 0

xServo = 17
yServo = 27
zServo = 22

exceptionAmount = 1

p = pigpio.pi()

p.set_mode(xServo, pigpio.OUTPUT)
p.set_mode(yServo, pigpio.OUTPUT)
p.set_mode(zServo, pigpio.OUTPUT)

p.set_PWM_frequency(xServo, 50)
p.set_PWM_frequency(yServo, 50)
p.set_PWM_frequency(zServo, 50)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.bind((HOST, PORT))
s.listen()
print("Listening...")
conn, addr = s.accept()
with conn:
    print('Connected by', addr)
    # p.start(2.5)

    flag = True

    while flag:
        data = conn.recv(1024)

        string = str(data, 'utf8')
        strings = string.split()

        try:

            if strings[0] == "xAxis":
                xAxis = float(strings[1])  # converting to float
            if strings[2] == "yAxis":
                yAxis = float(strings[3])
            if strings[4] == "zAxis":
                zAxis = float(strings[5])
            if strings[0] == "q":
                p.set_PWM_dutycycle(xServo, 0)
                p.set_PWM_dutycycle(yServo, 0)
                p.set_PWM_dutycycle(zServo, 0)
                flag = False

            if strings[0] == "f":
                p.set_PWM_dutycycle(xServo, 0)
                p.set_PWM_dutycycle(yServo, 0)
                p.set_PWM_dutycycle(zServo, 0)
        except:
            print("Corrupt data, continuing program. Amount of corrupted data packets:  ", exceptionAmount)
            exceptionAmount = exceptionAmount + 1

        try:
            p.set_servo_pulsewidth(xServo, xAxis)
            p.set_servo_pulsewidth(yServo, yAxis)
            p.set_servo_pulsewidth(zServo, zAxis)
            # time.sleep(0.25)
        except KeyboardInterrupt:
            p.stop()

        # conn.sendall(data)

s.close()



