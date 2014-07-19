'''
Created on 18 Jul 2014

@author: matthew
'''
from time import sleep

from random import random

from OSC import OSCClient, OSCMessage

from math import sin

client = OSCClient()

client.connect(("192.168.0.3", 8002))

while True:
    for x in xrange(0,360):
        x=sin        
        message=OSCMessage("/test")
        message.append(random()*200)
        client.send(message)
        sleep(500/1000.0)




