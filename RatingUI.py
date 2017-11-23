#!/usr/local/bin/python
# coding: utf-8
#
from __future__ import with_statement

import argparse
import random
import threading
import time
import json

from Tkinter import *

from Ar2c import Ar2c
from tableSimple import patternNames as names

rating = ['not detected',
          'bad clarity\nand intensity',
          'OK clarity\nbut bad intensity',
          'OK intensity\nbut bad clarity',
          'both OK']

patterns=[ 2, 5,11,26,29,
          53,57,60,97]
trials=3

class RatingUI(object):
    def __init__(self, port,title='Rating'):  # None):
        # protocol
        self.Ngrades = len(rating)
        self.expData=self.protocol()
        self.trialPointer=0

        # hardware
        self.ar2c = Ar2c(port)
        self.ar2c.setupTypes([0,0,0])

        self.root = Tk()
        self.root.title(title)

        self.title = Label(self.root, text="Trial 1 of %d"%len(self.expData),
                           font=("Helvetica", 18))
        self.title.grid(row=0, columnspan=self.Ngrades, pady=50)

        self.label = Label(self.root, text="", font=("Helvetica", 24))
        self.label.grid(row=1, columnspan=self.Ngrades, pady=50)
        firstTrial=self.expData[0]
        self.label.config(text=names[firstTrial['pattern']])

        self.btnRepeat = Button(self.root, text="Play", font=("Helvetica", 24),
                                command = self.replayRequest)
        self.btnRepeat.grid(row=2, columnspan=self.Ngrades, pady=50)

        for i in range(0, self.Ngrades):
            btn = Button(self.root,
                         command=lambda a=i: self.ratingSubmit(a),
                         text=rating[i], font=("Helvetica", 24), \
                                    width=15)
            btn.grid(row=3, column=i, pady=100, padx=30)

        self.lock = threading.Lock()
        # response: 0 for no key pressed, -1 for space, int>0 for rating
        self.response = 0
        self.responseTime = 0
        self.ie = True

    def protocol(self):
        experimentData=[]
        for round in range(0,trials):
            trialRound=[]
            for motor in [1,2,3]:
                for pattern in patterns:
                    trialData={"motor":motor,
                               "pattern":pattern,
                               "rating":None}
                    trialRound.append(trialData)
            random.shuffle(trialRound)
            experimentData+=trialRound

        #print experimentData
        print len(trialRound)
        print len(experimentData)
        return experimentData


    def startLoop(self):
        self.isOpen = True
        #self.root.protocol("WM_DELETE_WINDOW", self.closeHandler)
        self.root.after(100, self.root.focus_force)
        self.root.mainloop()

    def setInputEnable(self, b):
        self.ie = b

    def replayRequest(self):
        trial=self.expData[self.trialPointer]
        self.ar2c.play(trial['motor'], trial['pattern'], 1)

    def ratingSubmit(self,rating):
        trial = self.expData[self.trialPointer]
        trial['rating']=rating
        if self.trialPointer==len(self.expData)-1:
            self.root.destroy()
        else:
            self.trialPointer+=1
            self.title.config(text="trial %d of %d"%(self.trialPointer+1,len(self.expData)))
            trial = self.expData[self.trialPointer]
            self.label.config(text=names[trial['pattern']])

    def closeHandler(self):
        print "closing"
        if self.cBack:
            self.cBack.windowClosing()

        self.isOpen = False
        self.root.destroy()

    def close(self):
        self.root.after(10, self.root.destroy)

    def saveFile(self):
        print self.expData

        print "Subject name? Leave blank to discard"
        fn = raw_input(">>")

        if len(fn) is 0:
            print "not saving"
            return

        fname = "./resultsType/%s_%s.json" % (fn, time.strftime("%Y%m%d_%H%M%S"))

        with open(fname, 'w') as outfile:
            js = json.dumps(self.expData)
            js = js.replace('},', '},\n').replace('[{', '\n[{').replace('}],', '}],\n')
            js = js.replace("'", '"')
            outfile.write(js)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Demo')
    parser.add_argument('-p', required=True, action="store", dest="port",
                        default='COM5',
                        help='set port. example python DemoGui.py -n COM5')

    port = parser.parse_args().port

    g = RatingUI(port)
    g.startLoop()
    g.saveFile()
