from mypyosc import *

class FractalDat_Controller(threading.Thread):
    def __init__(self,send_targets,receive_port):
        self.send_targets=send_targets
        self.receive_port=receive_port
        self.setup_server()
        self.osc_emitters=list()
        self.setup_emitters()
        self.setup_defaults()
        
    def setup_defaults(self):
        self.g_size=32
        self.roughness=0#80 ##controllerd
        self.osc_rate=300
        self.corner_seed_ranges=[( 0,360),(360,360),
                            (0,360),(360,360)] #all controllerd
        self.zoom=.75
        self.inter_grid_sleep=30
        self.center_val_range=(0,0)#controllered
        self.zoom_steps=2
              
        
    def setup_server(self):
        self.controllers=dir(self)
        controllers=[('/'+controller[5:], getattr(self,controller))
                       for controller in controllers if controller.startswith("ctrl_")]
        osc_srv=OSCReceiver(self.receive_port, controllers,bind_ip)    
        osc_srv.start()

    def setup_emitters(self):
        for ip,port,target in send_targets:
            self.osc_emitters.append(OSCSender(target,(ip,port)))
    
    def run(self):
        self.osc_fgrid=OSCFractgrid(self.g_size,
                                    self.roughness,
                                    self.zoom,
                                    self.inter_grid_sleep,
                                    self.osc_rate,
                                    self.osc_emitters,
                                    zoom_steps=self.zoom_steps,
                                    center_val_range=self.center_val_range,
                                    corner_seed_ranges=self.corner_seed_ranges)
        self.osc_fgrid.start()



    ##########
    #
    # CONTROLLERS
    #
    ##########
    
    #functions starting with ctrl_ will be turned into OSC receiver address handlers
    #ctrl_something becomes /something

    def ctrl_roughness_handler(a,b,c,d):
        print "Setting roughness to ",c[0]
        self.osc_fgrid.fractal_heightmap.roughness=float(c[0])
        self.osc_fgrid.roughness=float(c[0])

    def ctrl_tl_min(a,b,data,d):
        print "Setting tl_min to ",data[0]
        tl,tr,bl,br=osc_fgrid.corner_seed_ranges
        tl=(float(data[0]),tl[1])
        self.osc_fgrid.corner_seed_ranges=(tl,tr,bl,br)
        
    def ctrl_tl_max(a,b,data,d):
        print "Setting tl_max to ",data[0]
        tl,tr,bl,br=osc_fgrid.corner_seed_ranges
        tl=(tl[0],float(data[0]))
        self.osc_fgrid.corner_seed_ranges=(tl,tr,bl,br)
        
    def ctrl_tr_min(a,b,data,d):
        print "Setting tr_min to ",data[0]
        tl,tr,bl,br=osc_fgrid.corner_seed_ranges
        tr=(float(data[0]),tr[1])
        self.osc_fgrid.corner_seed_ranges=(tl,tr,bl,br)
        
    def ctrl_tr_max(a,b,data,d):
        print "Setting tr_max to ",data[0]
        tl,tr,bl,br=osc_fgrid.corner_seed_ranges
        tr=(tr[0],float(data[0]))
        self.osc_fgrid.corner_seed_ranges=(tl,tr,bl,br)
        
    def ctrl_bl_min(a,b,data,d):
        print "Setting bl_min to ",data[0]
        tl,tr,bl,br=osc_fgrid.corner_seed_ranges
        bl=(float(data[0]),bl[1])
        self.osc_fgrid.corner_seed_ranges=(tl,tr,bl,br)
        
    def ctrl_bl_max(a,b,data,d):
        print "Setting bl_max to ",data[0]
        tl,tr,bl,br=osc_fgrid.corner_seed_ranges
        bl=(bl[0],float(data[0]))
        self.osc_fgrid.corner_seed_ranges=(tl,tr,bl,br)
    
    def ctrl_br_min(a,b,data,d):
        print "Setting br_min to ",data[0]
        tl,tr,bl,br=osc_fgrid.corner_seed_ranges
        br=(float(data[0]),br[1])
        self.osc_fgrid.corner_seed_ranges=(tl,tr,bl,br)
        
    def ctrl_br_max(a,b,data,d):
        print "Setting br_max to ",data[0]
        tl,tr,bl,br=osc_fgrid.corner_seed_ranges
        br=(br[0],float(data[0]))
        self.osc_fgrid.corner_seed_ranges=(tl,tr,bl,br)        
    
    def ctrl_ctr_min(a,b,data,d):
        print "Setting ctr_min to ",data[0]
        cmin,cmax=osc_fgrid.center_val_range
        cmin=float(data[0])
        self.osc_fgrid.center_val_range=(cmin,cmax)
        
    def ctrl_ctr_max(a,b,data,d):
        print "Setting ctr_max to ",data[0]
        cmin,cmax=osc_fgrid.center_val_range
        cmax=float(data[0])
        self.osc_fgrid.center_val_range=(cmin,cmax)