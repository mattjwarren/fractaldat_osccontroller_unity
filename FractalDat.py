'''
Created on 18 Jul 2014

@author: matthew
'''
            

import matplotlib.pyplot as plt
import matplotlib.cm as cm
from math import sqrt
from collections import namedtuple
import random
from mypyosc import *
import datetime

Coord=namedtuple('Coord','x y')

class Grid(object):
    '''grid handedness, 0,0=topleft  max,max=bottomr right'''    

    def __init__(self,x,y):
        self.size_x=x
        self.size_y=y
        self.data=[ [0 for _ in xrange(x)] for _ in xrange(y) ]
        
    def _render_to_text(self):
        print '\n\n'
        for row in self.data:
            print [ int(n) for n in row ]
    
    def _render_to_colormap(self):
        plt.imshow(self.data, interpolation='nearest',cmap=cm.gist_rainbow)
        plt.show()
       
    def render(self):
        self._render_to_colormap()
        #self._render_to_text()
        
    def make(self,coordinate,value):
        self.data[coordinate.x][coordinate.y]=value
        
    def make_new(self,coordinate,value):
        if self.data[coordinate.x][coordinate.y]==0:
            self.make(coordinate,value)
            
    def get(self,coordinate):
        return self.data[coordinate.x][coordinate.y]
    
class FractalHeightmap(object):
    '''populates a 'grid' with a fractal heightmap'''
    def __init__(self,grid,rng_seed,roughness,
                 corner_seeds=[(0,100),(0,100),(0,100),(0,100)],
                 max_depth=3):
        self.grid=grid
        self.max_depth=max_depth
        self._set_initial_corners(corner_seeds)
        self.roughness=roughness
        self.generate_heightmap([Coord(0,0),
                                 Coord(self.grid.size_x-1,0),
                                 Coord(0,self.grid.size_y-1),
                                 Coord(self.grid.size_x-1,self.grid.size_y-1)],1
                                )

    def _set_initial_corners(self,corner_seeds):
        tl,tr,bl,br=corner_seeds
        seeds=[[tl,tr],[bl,br]]
        for x_idx,x in enumerate([0,self.grid.size_x-1]):
            for y_idx,y in enumerate([0,self.grid.size_y-1]):
                try:
                    minval,maxval=seeds[x_idx][y_idx]
                    val=minval+(random.random()*(maxval-minval))
                except ValueError:
                    val=seeds[x_idx][y_idx]
                self.grid.make_new(Coord(x,y),val)
                
    def generate_heightmap(self,corners,depth):
        '''corners = (Coord(),Coord(),Coord(),Coord() / tl/tr/bl/br'''
        if depth>self.max_depth: return
        #as soon as the midpoint overlays a corner (integer maths) we stop recursing
        
        #
        tl,tr,bl,br=corners
        center=Coord(tl.x+((tr.x-tl.x)/2),tr.y+((br.y-tr.y)/2))
        #define edge center coordinates
        top_c=Coord(tl.x+((tr.x-tl.x)/2),tl.y)
        left_c=Coord(tl.x,tl.y+((bl.y-tl.y)/2))
        right_c=Coord(tr.x,tr.y+((br.y-tr.y)/2))
        bot_c=Coord(bl.x+((br.x-bl.x)/2),bl.y)
        
        #calc the center and edge_center heights
        if self.grid.get(center)==0:
            avg=sum([self.grid.get(tl),
                    self.grid.get(tr),
                    self.grid.get(bl),
                    self.grid.get(br)]
                    )/4.0  ###NOTE, we can choose to use the current corners, the new edge-centers, or all
                    #currenty we use the current corners
                    #then do the edge centers
            offset=((random.random())-.5)*self.roughness 
            self.grid.make_new(center,avg+offset)
        
        #top_c
        if self.grid.get(top_c)==0:
            avg=sum([self.grid.get(tl),
                    self.grid.get(tr)]
                    )/2.0
            offset=((random.random())-.5)*self.roughness
            self.grid.make_new(top_c,avg+offset)
        
        #left_c
        if self.grid.get(left_c)==0:
            avg=sum([self.grid.get(tl),
                     self.grid.get(bl)]
                    )/2.0
            offset=((random.random())-.5)*self.roughness
            self.grid.make_new(left_c,avg+offset)
        
        #right_c
        if self.grid.get(right_c)==0:  
            avg=sum([self.grid.get(tr),
                     self.grid.get(br)]
                    )/2.0
            offset=((random.random())-.5)*self.roughness
            self.grid.make_new(right_c,avg+offset)
            
        #bot_c
        if self.grid.get(bot_c)==0:
            avg=sum([self.grid.get(bl),
                     self.grid.get(br)]
                    )/2.0
            offset=((random.random())-.5)*self.roughness
            self.grid.make_new(bot_c,avg+offset)

        #g.render()
        self.generate_heightmap((tl,top_c,left_c,center),depth+1)
        #g.render()
        self.generate_heightmap((top_c,tr,center,right_c),depth+1)
        #g.render()
        self.generate_heightmap((left_c,center,bl,bot_c),depth+1)
        #g.render()
        self.generate_heightmap((center,right_c,bot_c,br),depth+1)
        #g.render()


if __name__ == '__main__':
    g_size=16#//must be power of 2
    roughness=3.0
    
    test_ip=IPAddr('192.168.0.3',8002)
    test_emitter=OSCSender('/test',test_ip)
    
    target_rate=50
    sleep_time=(1000.0/target_rate)/1000.0
    g=Grid(g_size+1,g_size+1)
    f=FractalHeightmap(g,1,roughness,max_depth=sqrt(g_size))
    while True:
        g=Grid(g_size+1,g_size+1)
        start=datetime.datetime.now()
        f=FractalHeightmap(g,1,roughness,max_depth=sqrt(g_size))
        for y in xrange(0,f.grid.size_y-1):
            for x in xrange(0,f.grid.size_x-1):
                ###[ test_emitter.message.append(v) for v in [(x,y,n) for n in [ row for row in f.grid.data ]] ]
                test_emitter.message.clearData()
                [ test_emitter.message.append(n) for n in ( x,y,f.grid.get(Coord(x,y)) ) ]
                test_emitter.send()
                sleep(sleep_time)
        end=datetime.datetime.now()
        print 'Send time',end-start
        