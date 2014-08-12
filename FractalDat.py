'''
Created on 18 Jul 2014

@author: matthew
'''
from mpl_toolkits.mplot3d.axes3d import Axes3D        
import numpy as np
from scipy.interpolate import griddata
from pylab import *
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from math import sqrt
from collections import namedtuple
import random
import math
from mypyosc import *
import datetime
import matplotlib.gridspec as gridspec
Coord=namedtuple('Coord','x y')
Corners=namedtuple('Corners','tl tr bl br')


class Grid(object):
    '''grid handedness, 0,0=topleft  max,max=bottom right
    this class is currently confused as to wether it should generate rectangular grids
    as well as square grids... possibly the root of some coupling with FractalHeightmap()'''    

    def __init__(self,x,y):
        self.size_x=x
        self.size_y=y
        self.corners=Corners(Coord(0,0),Coord(self.size_x-1,0),
                      Coord(0,self.size_y-1),Coord(self.size_x-1,self.size_y-1))
        
        self._data=[ [0 for _ in xrange(x)] for _ in xrange(y) ]
                
    def _render_to_text(self):
        for row in self._data:
            print [ int(round(n)) for n in row ]
        
    def subgrid(self,sg_corners):
        tl,tr,bl,br=sg_corners
        subgrid=Grid(tr.x-tl.x,bl.y-tl.y)
        for sg_y,y in enumerate(xrange(tl.y,bl.y)):
            for sg_x,x in enumerate(xrange(tl.x,tr.x)):
                #print 'sg_x,y=',sg_x,sg_y
                subgrid.make(Coord(sg_x,sg_y),self.get(Coord(x,y)))
        return subgrid

    def _serialise(self):
        serial_data=[ v for row in self._data  for v in row  ] #return a new, not a reference.
        return serial_data

    def _render_to_colormap(self):
        #vals=self._serialise()
        #val_min=min(vals)
        #val_max=max(vals)
        #print 'DEBUG: val_min,val_max=',val_min,val_max
        #plt.imshow(self._data, interpolation='nearest',vmin=val_min,vmax=val_max,cmap=cm.BrBG)
        
        
        
        #this one averages by nearest neighbours, i think....
        #plt.imshow(self.data,cmap=cm.gist_rainbow)
        
        
        #plt.contour(self._data, cmap=cm.BrBG)
        data = np.array(self._data)
        length = data.shape[0]
        width = data.shape[1]
        x, y = np.meshgrid(np.arange(length), np.arange(width))
        
        fig = plt.figure()
        ax = fig.add_subplot(1,1,1, projection='3d')
        ax.plot_surface(x, y, data)
        plt.show()
        
        #this one averages by nearest neighbours, i think....
        #plt.imshow(self._data,cmap=cm.gist_rainbow)
        
        
        plt.show()
       
    def render(self):
        #self._render_to_colormap()
        self._render_to_text()
        
    def make(self,coordinate,value):#make? ino rite?
        #print 'making',coordinate.x,coordinate.y
        self._data[coordinate.x][coordinate.y]=value
            
    def logscaled(self,scale):
        for iy,row in enumerate(self._data):
            for ix,H in enumerate(row):
                if H!=0:
                    self._data[ix][iy]=log(H/(random.random()*2))*scale
            
            #we dont need get
            # OR MAKE! YOU FOOL! just access self._data, it's public
            #  but.. Coord()
    def get(self,coordinate):
        return self._data[coordinate.x][coordinate.y]
    
class FractalHeightmap(object):
    '''populates a 'grid' with a fractal heightmap'''
    def __init__(self,grid,rng_seed,roughness,
                 ##
                 ## the numbers in corner_seed_ranges specify the range of numbers each corner can take
                 ## when the drid is first initialised
                 ##  *you can change these* 
                 #corner_seed_ranges=[(10,90),(10,90),(10,90),(10,90)],
                 ##corner_seed_ranges=[(10,100),(10,100),(10,100),(10,100)],
                 corner_seed_ranges=[ ( int(random.random()*60)+20, int(random.random()*60)+20 ),
                                      ( int(random.random()*60)+20, int(random.random()*60)+20 ),
                                      ( int(random.random()*60)+20, int(random.random()*60)+20 ),
                                      ( int(random.random()*60)+20, int(random.random()*60)+20 ) ],
                 
                 max_depth=3,
                 center_val=None):
        self.grid=grid
        self.max_depth=max_depth
        self._set_initial_corners(corner_seed_ranges,center_val)
        self.roughness=roughness
        self.generate_heightmap([Coord(0,0),###############EDIED OUT MINNUS ONES FRM size parm exp[ressions
                                 Coord(self.grid.size_x-1,0),
                                 Coord(0,self.grid.size_y-1),
                                 Coord(self.grid.size_x-1,self.grid.size_y-1)],1
                                )

    #currently performs centered subgrid zoom, subgrid size expressed as percentage
    def zoom(self,subgrid_size):
        #calculate subgrid and grab it
        sg_width=int(round(self.grid.size_x*subgrid_size))
        sg_height=int(round(self.grid.size_y*subgrid_size))
        sg_x_off=int(round(self.grid.size_x-sg_width)/2.0)
        sg_y_off=int(round(self.grid.size_y-sg_height)/2.0)
                      
        sg_tl=Coord(sg_x_off,sg_y_off)
        sg_tr=Coord(self.grid.size_x-sg_x_off,sg_y_off)
        sg_bl=Coord(sg_x_off,self.grid.size_y-sg_y_off)
        sg_br=Coord(self.grid.size_x-sg_x_off,self.grid.size_y-sg_y_off)
        
        corners=Corners(sg_tl,sg_tr,sg_bl,sg_br)
        subgrid=self.grid.subgrid(corners)
        zoomed_grid=Grid(self.grid.size_x,self.grid.size_y)
        step_x=zoomed_grid.size_x/float(subgrid.size_x)
        step_y=zoomed_grid.size_y/float(subgrid.size_y)
        
        #explode-scale subgrid into new full size grid
        for idx_y,sg_y in enumerate(xrange(0,subgrid.size_y)):
            for idx_x,sg_x in enumerate(xrange(0,subgrid.size_x)):
                zg_x=int(round(idx_x*step_x))
                zg_y=int(round(idx_y*step_y))
                zoomed_grid.make(Coord(zg_x,zg_y),
                                    subgrid.get(Coord(sg_x,sg_y)))
        print 'ZOOM SCLED'
        zoomed_grid.render()
        print '-------------------------'
        self.grid=zoomed_grid
        self.generate_heightmap([Coord(0,0),
                                 Coord(self.grid.size_x-1,0),
                                 Coord(0,self.grid.size_y-1),
                                 Coord(self.grid.size_x-1,self.grid.size_y-1)],1
                                )

    def _set_initial_corners(self,corner_seed_ranges, center_val=None):
        tl,tr,bl,br=corner_seed_ranges #could be same representation as Corners(), but out of expecteed ranges
        seeds=[[tl,tr],
               [bl,br]]
        for x_idx,x in enumerate([0,self.grid.size_x-1]):
            for y_idx,y in enumerate([0,self.grid.size_y-1]):
                try:
                    minval,maxval=seeds[x_idx][y_idx]
                    print 'CORNER VAL MINMAX INIT',minval,maxval
                    val=minval+(random.random()*(maxval-minval))
                except ValueError:
                    val=seeds[x_idx][y_idx]
                self.grid.make(Coord(x,y),val)
        if center_val:
            self.grid.make(Coord(self.grid.size_x/2,self.grid.size_y/2),center_val)
    def generate_heightmap(self,corners,depth):
        '''corners = Corners(Coord(),Coord(),Coord(),Coord()) / tl/tr/bl/br'''
        if depth>self.max_depth: return
        tl,tr,bl,br=corners
        #define center-center coords
        center=Coord(tl.x+((tr.x-tl.x)/2),tr.y+((br.y-tr.y)/2))
        #define edge center coordinates
        top_c=Coord(tl.x+((tr.x-tl.x)/2),tl.y)
        left_c=Coord(tl.x,tl.y+((bl.y-tl.y)/2))
        right_c=Coord(tr.x,tr.y+((br.y-tr.y)/2))
        bot_c=Coord(bl.x+((br.x-bl.x)/2),bl.y)
        
        #calc the center and edge_center heights
        
        #center
        if self.grid.get(center)==0:
            avg=sum([self.grid.get(tl),
                    self.grid.get(tr),
                    self.grid.get(bl),
                    self.grid.get(br)]
                    )/4.0  ###NOTE, we can choose to use the current corners, the new edge-centers, or all
                    #currenty we use the current corners
                    #then do the edge centers using only the edge corners, not the new center
            offset=((random.random())-.5)*self.roughness #'they' have mentioned needing a scaled constant 
                                                         #(inverse scaled to the  the depth of recurion)
                                                         #scaling down results in landscape smoothing out in the cracks,
                                                         #fairly good approx behaviour for water erosion
            self.grid.make(center,avg+offset)
        
        #top_c
        if self.grid.get(top_c)==0:
            avg=sum([self.grid.get(tl),
                    self.grid.get(tr)]
                    )/2.0
            offset=((random.random())-.5)*self.roughness
            self.grid.make(top_c,avg+offset)
        
        #left_c
        if self.grid.get(left_c)==0:
            avg=sum([self.grid.get(tl), #no need to use sum
                     self.grid.get(bl)]
                    )/2.0
            offset=((random.random())-.5)*self.roughness
            self.grid.make(left_c,avg+offset)
        
        #right_c
        if self.grid.get(right_c)==0:  
            avg=sum([self.grid.get(tr),
                     self.grid.get(br)]
                    )/2.0
            offset=((random.random())-.5)*self.roughness
            self.grid.make(right_c,avg+offset)
            
        #bot_c
        if self.grid.get(bot_c)==0:
            avg=sum([self.grid.get(bl),
                     self.grid.get(br)]
                    )/2.0
            offset=((random.random())-.5)*self.roughness
            self.grid.make(bot_c,avg+offset)

        #g.render()
        self.generate_heightmap(Corners(tl,top_c,left_c,center),depth+1)
        #g.render()
        self.generate_heightmap(Corners(top_c,tr,center,right_c),depth+1)
        #g.render()
        self.generate_heightmap(Corners(left_c,center,bl,bot_c),depth+1)
        #g.render()
        self.generate_heightmap(Corners(center,right_c,bot_c,br),depth+1)
        #g.render()

#        print 'THIS SHOULD APPEAR ONCE PER GRID'
#        self.grid.logscaled(15)


import threading
class OSCFractgrid(threading.Thread):
    
    def __init__(self,grid_size,roughness,zoom,inter_grid_gap,
                  osc_rate,ip_addr,port,target,
                  starting_corners=None,zoom_steps=4,center_val=None):
        threading.Thread.__init__(self)
        self.sleep_time=(1000.0/osc_rate)/1000.0
        self.zoom=zoom
        self.inter_grid_sleep=inter_grid_gap
        self.grid_size=grid_size
        self.grid=Grid(grid_size+1,grid_size+1)
        self.ip_addr=IPAddr(ip_addr,8002)
        self.target=target
        self.fractal_heightmap=FractalHeightmap(self.grid,1,roughness,max_depth=sqrt(self.grid_size),center_val=center_val)#sqrt because spatial doubling of point data
        self.osc_emitter=OSCSender(self.target,self.ip_addr)
        self.zoom_steps=zoom_steps
        
    def run(self):
        ctr=1
        while True:
            #init
            start=datetime.datetime.now()
            if ctr % self.zoom_steps==0:
                print 'NEW GRID'
                self.fractal_heightmap=FractalHeightmap(self.grid,1,roughness,max_depth=sqrt(self.grid_size),
                                                        corner_seed_ranges=[( int(random.random()*60)+20, int(random.random()*60)+20 ),
                                                                            ( int(random.random()*60)+20, int(random.random()*60)+20 ),
                                                                            ( int(random.random()*60)+20, int(random.random()*60)+20 ),
                                                                            ( int(random.random()*60)+20, int(random.random()*60)+20 )
                                                                            ],center_val=center_val
                                                        )#sqrt because spatial doubling of point data
            else:
                self.fractal_heightmap.zoom(self.zoom)#parameter is perecnt size of original grid, zoom is a stretched subgrid of that size, centered, and scaled out to fit the
                                                 #base grid with gaps generated fractally from the points that did exist :::::::::::: generated fractally from the points that did exist  NNEEDDS MOOREE EXPLAANATION

            for y in xrange(0,self.fractal_heightmap.grid.size_y):
                for x in xrange(0,self.fractal_heightmap.grid.size_x):
                    self.osc_emitter.message.clearData()
                    [ self.osc_emitter.message.append(n) for n in ( x,y,self.fractal_heightmap.grid.get(Coord(x,y)) ) ]#thats a tuple not a function call on in.()
                    #send
                    self.osc_emitter.send()
                    sleep(self.sleep_time)#roughly approximates target_rate considering sleep is approximate and other execution time. real rate will always be a little slower
            #render
            self.fractal_heightmap.grid.render()
            ctr+=1
            ##
            sleep(self.inter_grid_sleep)
            end=datetime.datetime.now()
            print '(estimated) Init+Calc+Send+Render+grid_sleep time',end-start
            print '\n\n'



    
    
    
if __name__ == '__main__': 
    
    def roughness_handler(a,b,c,d):
        #osc_fgrid.fractal_heightmap.roughness=something
        print '\n\n\n\n\nGOT SOMETHING\n\n\n\n\n\n',a,b,c,d
        pass
    
    #setup server
    osc_srv=OSCReceiver(13579, [('/roughness',roughness_handler)] )
    osc_srv.start()
    osc_emitter=OSCSender('/roughness',('localhost',13579))
    #TESTPROG
    
    g_size=32#32
    roughness=80#80
    osc_rate=300 #300 OSC Messages sent per second
    zoom=.75#.25
    inter_grid_sleep=12.33#12.33
    center_val=400#400
    zoom_steps=8#4
    ip_addr='77.101.65.99'
    port=8002
    target='/test'
    osc_fgrid=OSCFractgrid(g_size,roughness,zoom,inter_grid_sleep,osc_rate,ip_addr,port,target,zoom_steps=zoom_steps,center_val=center_val)
    osc_fgrid.start()
    print 'Whoopie'
    sleep(120)
    osc_emitter.message.append(100)
    osc_emitter.send()
    
    
    