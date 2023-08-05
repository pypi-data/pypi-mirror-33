import os
import sys
import select
import RPi.GPIO as GPIO
import smbus2
from time import sleep

from devices import ShiftRegister
from devices import Multiplexer
from devices import DigitalModule
from devices import AnalogModule

class Mainboard:

    def __init__(self):
        
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)


#        dataPinP = 18   #pin 14 on the 74HC595
#        latchPinP = 17  #pin 12 on the 74HC595
#        clockPinP = 4   #pin 11 on the 74HC595
#
#        dataPinR = 24   #pin 14 on the 74HC595
#        latchPinR = 23  #pin 12 on the 74HC595
#        clockPinR = 27  #pin 11 on the 74HC595

        dataPin = 18   #pin 14 on the 74HC595
        latchPin = 17  #pin 12 on the 74HC595
        clockPin = 27  #pin 11 on the 74HC595

        # 74HC4067
        S0Pin = 5
        S1Pin = 6
        S2Pin = 12
        S3Pin = 13
        COMPin = 7

        # Number of Relays
        self.relay_num = 12
        self.input_num = 14

#        self.relaysP = ShiftRegister(dataPinP, latchPinP, clockPinP)
#        self.relaysR = ShiftRegister(dataPinR, latchPinR, clockPinR)
        self.relays = ShiftRegister(dataPin, latchPin, clockPin)
        self.lineInputs = Multiplexer(S0Pin, S1Pin, S2Pin, S3Pin, COMPin)
        self.digitalModules = self.scanModule()
        self.analogModules = self.scanAnalogModule()

        self.RELAYS = {}
        self.INPUTS = []
        self.AINPUTS = []
        self.AOUTPUTS = []

        # Generate Relay Output Names
        for i in range(self.relay_num):
#            if i<8:
#                self.RELAYS["K"+str(i+1)] = (i, self.relaysP.output)
#            else:
#                self.RELAYS["K"+str(i+1)] = (i-8, self.relaysR.output)
            self.RELAYS["K"+str(i+1)] = (i, self.relays.output)

        for j,m in enumerate(self.digitalModules):
            for i in range(6):
                self.RELAYS["K"+str(self.relay_num + j * 6 + i + 1)] = (i, m.output)

        # Generate Valve Output Names
        for i in range(3):
            self.RELAYS["V"+str(i+1)] = (self.relay_num+i, self.relays.output)

        # Generate Digital Input Names
        for i in range(self.input_num):
            if i < 8:
                self.INPUTS.append("L" + str(i+1))
            else:
                self.INPUTS.append("D" + str(i+1-8))

        # Generate Digital Module Input Names
        for j,m in enumerate(self.digitalModules):
            for i in range(6):
                self.INPUTS.append("L" + str(j * 6 + i + 1 + 8))

        # Generate Analog Module Input Names
        for j,m in enumerate(self.analogModules):
            for i in range(4):
                self.AINPUTS.append("A" + str(j * 4 + i + 1))
                self.AOUTPUTS.append("S" + str(j * 4 + i + 1))

    def digitalWrite(self, name, state):
        try:
            value = self.RELAYS[name]
            value[1](value[0], state)
        except:
            pass

    def digitalRead(self, name):
        if name in self.INPUTS[:self.input_num]:
            inputs = self.lineInputs.read()
            try:
                index = self.INPUTS.index(name)
            except:
                pass
            return inputs[index]
        else:
            n = self.INPUTS[self.input_num:].index(name)
            m = n / 6
            i = n % 6
            value = self.digitalModules[m].read()
            return int((value & (1 << i)) != 0)

    def digitalReadAll(self):
        inputs = self.lineInputs.read()[:self.input_num]
        for m in self.digitalModules:
            inputs.extend([int(_) for _ in reversed(list("{0:08b}".format(m.read())))][:6])
        return inputs

    def analogRead(self, name):
        n = self.AINPUTS.index(name)
        m = n / 4
        i = n % 4
        value = self.analogModules[m][0].read(i)
        return value

    def analogWrite(self, name, value):
        n = self.AOUTPUTS.index(name)
        m = n / 4
        i = n % 4
        self.analogModules[m][1].write(i, value)
        

    def scanModule(self):
        modules = []
        bus = smbus2.SMBus(1)
        for address in range(32,40):
            try:
                bus.read_byte(address)
                modules.append(DigitalModule(address))
            except:
                pass
        return modules

    def scanAnalogModule(self):
        modules = []
        bus = smbus2.SMBus(1)
        for address in range(104,111):
            try:
                bus.read_byte(address)
                modules.append((AnalogModule.Input(address), AnalogModule.Output(address-7)))
            except:
                pass
        return modules

if __name__ == "__main__":
    app = Mainboard()
    while True:
        print app.digitalReadAll()
        app.digitalWrite("K1", GPIO.HIGH)
        sleep(0.1)
        app.digitalWrite("K1", GPIO.LOW)
        sleep(0.1)
