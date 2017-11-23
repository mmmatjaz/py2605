import argparse
import os

import serial
import time
from table import patternNames

class Ar2c:

    def __init__(self, serialPort=None):
        if serialPort is None:
            serialPort='COM6' if os.name == 'nt' else '/dev/ttyUSB0'

        print "connecting to " + serialPort + " at " + str(38400)
        self.ser = serial.Serial(timeout=1)
        self.ser.port = serialPort
        self.ser.baudrate = 38400
        self.ser.parity=serial.PARITY_NONE
        self.ser.stopbits=serial.STOPBITS_ONE
        self.ser.bytesize=serial.EIGHTBITS
        self.ser.open()
        ''' the FTDI tends to reset the board, therefore it's neccessary to
            wait 2s before sending anything
        '''
        ''' try:
            print self.sendCmd("INFO")
        except IOError:
            print "FTDI reset connected"
            time.sleep(1.5) '''
        time.sleep(1.5)

    def sendCmd(self, cmd, waitForReply=True):
        tout = 10.
        if cmd is not None:
            self.ser.write(cmd + ';\r')
        # print '>>'+cmd+';'
        if waitForReply:
            time.sleep(.001)
            tic = time.time()
            while self.ser.inWaiting() == 0:
                el = time.time() - tic
                if el > tout:
                    raise IOError("Timeout")
            rep = ""
            while self.ser.inWaiting() > 0:
                rep = rep + self.ser.readline()

            return rep

        # else:
        if self.ser.inWaiting() > 0:
            self.ser.flushInput()

    def setupTypes(self,isLRA):
        cmd="init;"
        for bul in isLRA:
            cmd+=str(bul)+';'
        print self.sendCmd(cmd)

    def play(self,driver,sample,repeat):
        cmd="play;{};{};{};".format(driver,sample,repeat)
        #print cmd
        res=self.sendCmd(cmd)
        print res

    def close(self):
        self.ser.close()

    def __del__(self):
        self.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Mag discrimination')
    parser.add_argument('-t', action="store",       dest="test", type=int, default=0)

    res=parser.parse_args()

    if res.test is 1:
        ar2c = Ar2c()
        ar2c.setupTypes([0, 0, 0])
        patterns = [2, 5, 8, 11, 13, 26, 29,
                    46, 49, 53, 55, 57, 60, 66]
        for pat in patterns:
            pat-=1
            print patternNames[pat]

            ar2c.play(3, pat, 1)
            time.sleep(1)

            ar2c.play( 1, pat, 1)
            time.sleep(1)

            ar2c.play(2, pat, 1)
            time.sleep(2)