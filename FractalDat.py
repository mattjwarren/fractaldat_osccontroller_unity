'''
Created on 18 Jul 2014

@author: matthew
'''
            
import OSC
from collections import namedtuple
import random

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
            
    def render(self):
        self._render_to_text()
        
    def make(self,coordinate,value):
        self.data[coordinate.x][coordinate.y]=value
        
    def get(self,coordinate):
        return self.data[coordinate.x][coordinate.y]
    
class FractalHeightmap(object):
    '''populates a 'grid' with a fractal heightmap'''
    def __init__(self,grid,rng_seed,roughness,corner_seeds=[(0,100),(0,100),(0,100),(0,100)]):
        self.grid=grid
        self._set_initial_corners(corner_seeds)
        self.roughness=roughness
        self.generate_heightmap([Coord(0,0),
                                 Coord(self.grid.size_x-1,0),
                                 Coord(0,self.grid.size_y-1),
                                 Coord(self.grid.size_x-1,self.grid.size_y-1)]
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
                self.grid.make(Coord(x,y),val)
                
    def generate_heightmap(self,corners):
        '''corners = (Coord(),Coord(),Coord(),Coord() / tl/tr/bl/br'''
        #as soon as the midpoint overlays a corner (integer maths) we stop recursing
        
        
        #
        tl,tr,bl,br=corners
        center=Coord((tr.x-tl.x)/2,(br.y-tr.y)/2)
        print 'DEBUG: corner=',corners
        print 'DEBUG: ceter=',center
        if center in corners: return
        
        #define edge center coordinates
        top_c=Coord(tl.x+((tr.x-tl.x)/2),tl.y)
        left_c=Coord(tl.x,tl.y+((bl.y-tl.y)/2))
        right_c=Coord(tr.x,tr.y+((br.y-tr.y)/2))
        bot_c=Coord(bl.x+((br.x-bl.x)/2),bl.y)
        
        #calc the center and edge_center heights
        avg=sum([self.grid.get(tl),
                self.grid.get(tr),
                self.grid.get(bl),
                self.grid.get(br)]
                )/4.0  ###NOTE, we can choose to use the current corners, the new edge-centers, or all
                #currenty we use the current corners
                #then do the edge centers
        offset=((random.random())-.5)*self.roughness
        self.grid.make(center,avg+offset)
        
        #top_c
        avg=sum([self.grid.get(tl),
                self.grid.get(tr)]
                )/2.0
        offset=((random.random())-.5)*self.roughness
        self.grid.make(top_c,avg+offset)
        
        #left_c
        avg=sum([self.grid.get(tl),
                 self.grid.get(bl)]
                )/2.0
        offset=((random.random())-.5)*self.roughness
        self.grid.make(left_c,avg+offset)
        
        #right_c        
        avg=sum([self.grid.get(tr),
                 self.grid.get(br)]
                )/2.0
        offset=((random.random())-.5)*self.roughness
        self.grid.make(right_c,avg+offset)
        
        #bot_c
        avg=sum([self.grid.get(bl),
                 self.grid.get(br)]
                )/2.0
        offset=((random.random())-.5)*self.roughness
        self.grid.make(bot_c,avg+offset)

        #Now, call ,yself with each of the new grid coords
        self.grid.render()
        
        #
        self.generate_heightmap((tl,top_c,left_c,center))
        self.generate_heightmap((top_c,tr,center,right_c))
        self.generate_heightmap((left_c,center,bl,bot_c))
        self.generate_heightmap((center,right_c,bot_c,br))



if __name__ == '__main__':
    g=Grid(9,9)
    f=FractalHeightmap(g,1,10)