'''
Created on 18 Jul 2014

@author: matthew
'''
from time import sleep
from my_pyOSC import OSCClient, OSCMessage

from my_pyOSC import OSCServer
from threading import Thread

from collections import namedtuple

IPAddr=namedtuple('IPAddr','ip port')

class OSCReceiver(Thread,OSCServer):
    
    def __init__(self,port,addresses):
        Thread.__init__(self)
        OSCServer.__init__(self,('192.168.0.8',port))
        for address,handler in addresses:
            self.addMsgHandler(address,handler)
    
    def run(self):
        self.serve_forever()

class OSCSender(OSCClient):
    '''places a message of '0' in pos 1 of the list'''
    
    def __init__(self,target,ip_addr):
        OSCClient.__init__(self)
        self._target=target
        self._ip_addr=ip_addr
        self.message=OSCMessage(self._target)
        #force creation of the message_list
        #for fast assignment later
        #self.message.append(0)
        self.connect(ip_addr)

    def send(self):
        OSCClient.send(self,self.message)


if __name__=='__main__':
    test_ip=IPAddr('192.168.0.3',8002)
    test_emitter=OSCSender('/test',test_ip)
    
    target_rate=50.0
    sleep_time=(1000.0/target_rate)/1000.0
    while True:
        for y in xrange(0,10):
            for x in xrange(0,10):
                [ test_emitter.message.append(n) for n in (x,y,randint(0,100)) ]
                test_emitter.send()
                test_emitter.message.clearData()
                sleep(sleep_time)

    





















































# client = OSCClient()
# 
# client.connect(("192.168.0.3", 8002))
# 
# while True:
#     for x in xrange(0,360):
#         x=sin        
#         message=OSCMessage("/test")
#         message.append(random()*200)
#         client.send(message)
#         sleep(500/1000.0)
    