from mypyosc import *
from FractalDat import FractalHeightmap, Grid
import threading
from math import sqrt,log
import datetime


Coord=namedtuple('Coord','x y')
Corners=namedtuple('Corners','tl tr bl br')

class OSCFractgrid(threading.Thread):
    def __init__(self,
                 grid_size,
                 roughness,
                 zoom,
                 inter_grid_gap,
                 osc_rate,
                 osc_emitters,
                 zoom_steps=4,
                 center_val_range=None,
                 corner_seed_ranges=None):
        
        threading.Thread.__init__(self)
        
        self.osc_rate=osc_rate
        #make sleep_time a calculated attribute
        #self.sleep_time=(1000.0/self.osc_rate)/1000.0
        
        self.zoom=zoom
        self.inter_grid_sleep=inter_grid_gap
        self.grid_size=grid_size
        self.grid=Grid(grid_size+1,grid_size+1)
        self.osc_emitters=osc_emitters
        self.corner_seed_ranges=corner_seed_ranges
        self.center_val_range=center_val_range
        self.roughness=roughness
        self.fractal_heightmap=FractalHeightmap(self.grid,1,self.roughness,max_depth=sqrt(self.grid_size),
                                        center_val_range=self.center_val_range,corner_seed_ranges=self.corner_seed_ranges)#sqrt because spatial doubling of point data
        self.zoom_steps=zoom_steps
        
    
    @property
    def sleep_time(self):
        return (1000.0/self.osc_rate)/1000.0
    
    def run(self):
        ctr=1
        while True:
            #init
            start=datetime.datetime.now()
            if ctr % self.zoom_steps==0:
                print 'NEW HEIGHTMAP'
                before=datetime.datetime.now()
                self.fractal_heightmap=FractalHeightmap(self.grid,1,self.roughness,max_depth=sqrt(self.grid_size),
                                                        corner_seed_ranges=self.corner_seed_ranges,center_val_range=self.center_val_range,
                                                        )#sqrt because spatial doubling of point data
                after=datetime.datetime.now()
                print "FINISHED HEIGHTMAP",(after-before)
            else:
                print "ZOOMING"
                before=datetime.datetime.now()
                self.fractal_heightmap.zoom(self.zoom)#parameter is perecnt size of original grid, zoom is a stretched subgrid of that size, centered, and scaled out to fit the
                                                      #base grid with gaps generated fractally from the points that did exist :::::::::::: generated fractally from the points that did exist  NNEEDDS MOOREE EXPLAANATION
                after=datetime.datetime.now()
                print "FINISHED ZOOMING",(after-before)
                
                self.fractal_heightmap.grid.render()
            print "SENDING"
            before=datetime.datetime.now()
            for y in xrange(0,self.fractal_heightmap.grid.size_y):
                for x in xrange(0,self.fractal_heightmap.grid.size_x):
                    #a fault line of flow
                    #(...) is a generator comprehension NOT an expression
                    [ osc_emitter.message.clearData() for osc_emitter in self.osc_emitters ]
                    [ ( osc_emitter.message.append(n)
                        for n in
                            ( x,y,self.fractal_heightmap.grid.get(Coord(x,y)) ) )#named tuples are slow 
                                                                                 #TODO: change it
                        for osc_emitter in 
                            self.osc_emitters ]
                    
                    [ osc_emitter.send() for osc_emitter in self.osc_emitters ]
                    sleep(self.sleep_time)#roughly approximates target_rate considering sleep is approximate and other execution time. real rate will always be a little slower
            after=datetime.datetime.now()
            print "FINISHED SENDING",(after-before)
            
            #render
            self.fractal_heightmap.grid.render()
            ctr+=1
            ##
            print "SLEEPING"
            before=datetime.datetime.now()
            sleep(self.inter_grid_sleep)
            after=datetime.datetime.now()
            print "FINISHED SLEEPING",(after-before)
            end=datetime.datetime.now()
            print '(estimated) Init+Calc+Send+Render+grid_sleep time',end-start
            print '\n\n'
            
            
class FractalDat_Controller(threading.Thread):
    
    def __init__(self,send_targets,receive_port,bind_ip):
        threading.Thread.__init__(self)
        self.bind_ip=bind_ip
        self.send_targets=send_targets
        self.receive_port=receive_port
        
        self.setup_server()
        self.osc_emitters=list()
        self.setup_emitters()
        self.setup_defaults()

        
    def setup_defaults(self):
        self.g_size=32 #controllerd
        self.roughness=0#80 ##controllerd
        self.osc_rate=300 #controlerd
        self.corner_seed_ranges=[( 0,360),(360,360),
                            (0,360),(360,360)] #all controllerd
        self.zoom=.75
        self.inter_grid_sleep=30
        self.center_val_range=(0,0)#controllered
        self.zoom_steps=2
              
        
    def setup_server(self):

        #this func is a bit kooky 'cause its from the early days
        def ctrl_roughness_handler(_a,_b,c,_d):
            print "Setting roughness to ",c[0]
            self.osc_fgrid.fractal_heightmap.roughness=float(c[0])
            self.osc_fgrid.roughness=float(c[0])
    
        def ctrl_tl_min(_a,_b,data,_d):
            print "Setting tl_min to ",data[0]
            tl,tr,bl,br=self.osc_fgrid.corner_seed_ranges
            tl=(float(data[0]),tl[1])
            self.osc_fgrid.corner_seed_ranges=(tl,tr,bl,br)
    
        def ctrl_osc_rate(_a,_b,data,_d):
            print "Setting osc_rate to ",data[0]
            self.osc_fgrid.osc_rate=int(data[0])
    
        def ctrl_g_size(_a,_b,data,_d):
            val=float(data[0])
            n=pow(2, int(log(val, 2) + 0.5))
            print "Setting g_size to ",n
            self.osc_fgrid.grid_size=n
            
        def ctrl_tl_max(_a,_b,data,_d):
            print "Setting tl_max to ",data[0]
            tl,tr,bl,br=self.osc_fgrid.corner_seed_ranges
            tl=(tl[0],float(data[0]))
            self.osc_fgrid.corner_seed_ranges=(tl,tr,bl,br)
            
        def ctrl_tr_min(_a,_b,data,_d):
            print "Setting tr_min to ",data[0]
            tl,tr,bl,br=self.osc_fgrid.corner_seed_ranges
            tr=(float(data[0]),tr[1])
            self.osc_fgrid.corner_seed_ranges=(tl,tr,bl,br)
            
        def ctrl_tr_max(_a,_b,data,_d):
            print "Setting tr_max to ",data[0]
            tl,tr,bl,br=self.osc_fgrid.corner_seed_ranges
            tr=(tr[0],float(data[0]))
            self.osc_fgrid.corner_seed_ranges=(tl,tr,bl,br)
            
        def ctrl_bl_min(_a,_b,data,_d):
            print "Setting bl_min to ",data[0]
            tl,tr,bl,br=self.osc_fgrid.corner_seed_ranges
            bl=(float(data[0]),bl[1])
            self.osc_fgrid.corner_seed_ranges=(tl,tr,bl,br)
            
        def ctrl_bl_max(_a,_b,data,_d):
            print "Setting bl_max to ",data[0]
            tl,tr,bl,br=self.osc_fgrid.corner_seed_ranges
            bl=(bl[0],float(data[0]))
            self.osc_fgrid.corner_seed_ranges=(tl,tr,bl,br)
        
        def ctrl_br_min(_a,_b,data,_d):
            print "Setting br_min to ",data[0]
            tl,tr,bl,br=self.osc_fgrid.corner_seed_ranges
            br=(float(data[0]),br[1])
            self.osc_fgrid.corner_seed_ranges=(tl,tr,bl,br)
            
        def ctrl_br_max(_a,_b,data,_d):
            print "Setting br_max to ",data[0]
            tl,tr,bl,br=self.osc_fgrid.corner_seed_ranges
            br=(br[0],float(data[0]))
            self.osc_fgrid.corner_seed_ranges=(tl,tr,bl,br)        
        
        def ctrl_ctr_min(_a,_b,data,_d):
            print "Setting ctr_min to ",data[0]
            #eclipse doesn't like this pattern of access but is easier to read than; cmax=self.osc_fgrid.center_val_range[1]
            cmin,cmax=self.osc_fgrid.center_val_range
            cmin=float(data[0])
            self.osc_fgrid.center_val_range=(cmin,cmax)
            
        def ctrl_ctr_max(_a,_b,data,_d):
            print "Setting ctr_max to ",data[0]
            cmin,cmax=self.osc_fgrid.center_val_range
            cmax=float(data[0])
            self.osc_fgrid.center_val_range=(cmin,cmax)
 
        controllers={'ctrl_roughness_handler':ctrl_roughness_handler,
                     'ctrl_tl_min':ctrl_tl_min,
                     'ctrl_tr_max':ctrl_tr_min,
                     'ctrl_bl_min':ctrl_bl_min,
                     'ctrl_br_max':ctrl_br_min,
                     'ctrl_tl_min':ctrl_tl_min,
                     'ctrl_tr_max':ctrl_tr_min,
                     'ctrl_bl_min':ctrl_bl_min,
                     'ctrl_br_max':ctrl_br_min,
                     'ctrl_ctr_min':ctrl_tl_min,
                     'ctrl_ctr_max':ctrl_tl_min,
                     'ctrl_g_size':ctrl_g_size,
                     'ctrl_osc_rate':ctrl_osc_rate,                     
                     }
 
        controllers=[('/'+controller, controllers[controller])
                       for controller in controllers]
        osc_srv=OSCReceiver(self.receive_port, controllers,self.bind_ip)    
        osc_srv.start()
        print "setup server"

    def setup_emitters(self):
        for ip,port,target in self.send_targets:
            self.osc_emitters.append(OSCSender(target,(ip,port)))
        print "setup emitters"
        
    def run(self):
        print "starting fractgrid"
        self.osc_fgrid=OSCFractgrid(self.g_size,
                                    self.roughness,
                                    self.zoom,
                                    self.inter_grid_sleep,
                                    self.osc_rate,
                                    self.osc_emitters,
                                    zoom_steps=self.zoom_steps,
                                    center_val_range=self.center_val_range,
                                    corner_seed_ranges=self.corner_seed_ranges)
        print "actualyll starting"
        self.osc_fgrid.start()
      
        
if __name__ == '__main__': 
        print "Creating the_machine."
        the_machine=FractalDat_Controller([('10.114.171.146',8002,'FractGrid'),
                                           ],
                                          13579,'127.0.0.1')
        print "the_machine is created. I will start it now."
        the_machine.start()
        print "the_machine has started."
        print "I am ending."