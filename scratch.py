'''
Created on 17 Jul 2014

@author: matthew
'''

'''
bare handed attack by a man is attack 10


'''

#'things' need to be able to deal with requests to 'reduce' their effectivness,
# or 'enhance' it, generically or based on some other context
        
class basic_armor(object): #(armor interface)
    def __init__(self):
        
        #expressed as a percentage
        #essentially expresses a high tech collection of generated fields
        #lsyerd into/over skin/cloth/metal/builings/planets/starships etc..
        self.resists={'mass':25, #getting hit by shit
                      'em':5, #electromagnetic. heat/lasers/cold/xray/gamme etc..
                      'rad':25, #any high energy paticle beams too
                      'grav':0, #gravitational distortion
                      'quant':0, #quantum level events
                      'psi':0, #psionic
                      'exo':0 #other exotics (magic/new physics/religious etc...}
                      } #turn these and other dict keys into enumerations
        
        
        #
        # enumerable_dict()??
        #
        #
        
        self.requirements={'electrical_standard':1} #describes energy reqs needed and quantity of 'standard' units. formatted type_(charge_type)
        #TODO: ^^^^^That line needs improving...self
        self.condition=100  #             0-100 / general use condition. applicable any usable thing.
                            # 0=cant use irreparable,
                            # 5=almost impossible repair
                            # 10=very difficult specialist repair / requires large equiment+mats
                            # 25=very difficult skilled repair / not possible unskilled
                            # 35=almost impossible uksilled /  difficult skilled
                            # 45=fairly hard repait if uskilled / easy if skilled
                            # 50-inoperable/needs_simple_repair / working if skilled
                            # 51-working 
                            # 98-+1 shiny bonus. 
                            # 100=+1.5 shiny bonus
        self.penalties={'move':lambda m: m-(m*.2)} 
        
    def reduce(self,dict_of_tagged_functions):
        

class bare_hand(object): #could be used as base melle object interface
    
    def __init__(self):
        self.damage={'mass':7,
                    'em':0,
                    'rad':0,
                    'grav':0,
                    'quant':0,
                    'psi':0,
                    'exo':0}
        
        
        #because we can use map and filter and listcomprehensions etc..
        self.restrictions={'health':lambda h:h>0,
                           'agi':lambda a: a>0,
                           'str':lambda s: s>0,
                           'pres':lambda p: p>0
                           }
    def strike(self,thing): #srike/generic_homaoind_attack
        #get releveant defensive shit from thing,
        #return difficulty number for action
        #
        #self is the entity using thin to doing the sriking
        
        
        pass
    
#with current model , a magical bare hand of a certain type would need its own class.
#hierarchy gone mad, or factory classes?

class man(object):
    
    def __init__(self):
        #some of these char attribs should be shadow attribes=s, producing visiblle ttribs tht seem disconnected?
        self.attributes=dict()
        #all attrs here are refered to as base_x elsewhere
        self.attributes={'health':int,
                         'armor':basic_armor,
                         'str':int, #muscles MAX_LOAD
                         'agi':int, #muscles AVG_RESPONSE
                         'pres':int, #mind SITUATIONAL AWARENESS / physical + mental
                         'int':int, # CLEVERNESS (readyness of association of concepts) 
                                    # DEPTH OF THOUGHT (complexity of intuition) 
                                    # ACCURACY OF CONCLUSION  (get it right)
                         'move':3.0, #metres per second
                         'move_fast':lambda __s: __s['move']*2} #mutiplier of normal speed / __s = give self as input to lambda
        self.modifiers={#as above absolute modifiers to the values
                        
                        
                        }
        self.using_equipment={'right_hand':bare_hand}
        self.equipment=list()
        self.current_attack='right_hand'
        
        
        
        ####this combat model assumes 'choosing to attack' is always the currently imperative action
    def attack(target):
        #attempt my attack, get modified copy of me back 
        self=target.defend(self)
        
    def defend(self,atacker):
        #get incomig attack particulars
        atacker.using_equipment[atacker.current_attack].strike(self)
        
def attack(atacker,attacked):
    #alters in_place theobjects given
    #sp is like a world managment level function included here for shortcuts and fun
        
    atacker.attack(attacked)