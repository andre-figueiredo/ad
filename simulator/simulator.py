
from SimPy.Simulation import Simulation,Process,Resource,Monitor,PriorityQ,hold,request,release
from random import expovariate, seed

###########################################################
## Experiment data
###########################################################

### General values ----------------------------------------
seedVal = 99999        # Seed to start simulation
# Time spended to attend a Customer (M/G/1 - fixed time)
serviceTime = 12.0
# Maximum simulation time
maxTime = 400.0

### Customer one ------------------------------------------
lamb1 = 1.0        # rate of Customer one
NCustomer1 = 1     # Number of Customers type one
### Customer two ------------------------------------------
lamb2 = 10.0       # rate of Customer two
NCustomer2 = 10    # Number of Customers type two

###########################################################
## Customer
###########################################################

class Customer(Process):
    """ Customer arrives, is served and leaves """
        
    def visit(self, timeInBank=0, counter=0, P=0):
        # arrival time
        arrive = self.sim.now()
        Nwaiting = len(self.sim.counter.waitQ)
        print ("%8.3f %s: Queue is %d on arrival"%(self.sim.now(),self.name,Nwaiting))

        yield request,self,self.sim.counter,P
        # waiting time
        wait = self.sim.now() - arrive
        print ("%8.3f %s: Waited %6.3f"%(self.sim.now(),self.name,wait))
        yield hold,self,timeInBank
        yield release,self,self.sim.counter                             

        print ("%8.3f %s: Completed"%(self.sim.now(),self.name))
        

############################################################
## Sources
############################################################

class BasicSource(Process):
    """ Source generates customers randomly """

    def generate(self, number, interval, typeOfClient, priority):       
        for i in range(number):
            c = Customer(name = "Customer%02d_%02d"%(typeOfClient,i,), sim=self.sim)
            self.sim.activate(c, self.get_generator(c, priority))
            t = expovariate(1.0/interval)
            yield hold,self,t
            
    def get_generator(self, c, priority):
        pass


class FCFSSource(BasicSource):
            
    def get_generator(self, c, priority):
            return c.visit(timeInBank=serviceTime, counter=self.sim.counter, P=priority)

class LCFSSource(BasicSource):
        
    def get_generator(self, c, priority):
            return c.visit(timeInBank=serviceTime, counter=self.sim.counter, P=self.sim.now())

############################################################
## Queue Models
############################################################

class BasicQueueModel(Simulation):
        
    def __init__(self):
        self.priority1 = 0
        self.priority2 = 0

    def run(self,aseed):
        self.initialize()
        seed(aseed)
        self.counter = self.get_resource()
        [s1, s2] = self.get_sources();
        self.activate(s1, s1.generate(number=NCustomer1, interval=lamb1, typeOfClient=1 ,priority=self.priority1))
        self.activate(s2, s2.generate(number=NCustomer2, interval=lamb2, typeOfClient=2, priority=self.priority2))
        self.simulate(until=maxTime)
        
        return

    def get_sources(self):
        pass

    def get_resource(self):
        pass
        
# M/D/1 queue, two types of clients, no priority and FIFO
class Queue1(BasicQueueModel):
        
    def get_sources(self):
        return [FCFSSource('Source1', sim=self), FCFSSource('Source2', sim=self)];
    
    def get_resource(self):
        return Resource(name="Counter", unitName="John Doe", monitored=True, qType=PriorityQ, preemptable=True, sim=self)
        
# M/D/1 queue, LIFO, two types of clients, no priority, no preemption, no differences between Customer 1 and 2
class Queue2(BasicQueueModel):
        
    def get_sources(self):
        return [LCFSSource('Source1', sim=self), LCFSSource('Source2', sim=self)];
    
    def get_resource(self):
        return Resource(name="Counter", unitName="John Doe", monitored=True, qType=PriorityQ, sim=self)
        
# M/D/1 queue, LIFO, two types of clients, no priority, no preemption, no differences between Customer 1 and 2
class Queue3(BasicQueueModel):
        
    def get_sources(self):
        return [LCFSSource('Source1', sim=self), LCFSSource('Source2', sim=self)];
    
    def get_resource(self):
        return Resource(name="Counter", unitName="John Doe", monitored=True, qType=PriorityQ, preemptable=True, sim=self)
        
# M/D/1 queue, two types of clients (Customer2 with less priority) one queue without preemption
class Queue4(BasicQueueModel):
        
    def __init__(self):
        super(Queue4, self).__init__()
        self.priority1 = 1
        
    def get_sources(self):
        return [FCFSSource('Source1', sim=self), FCFSSource('Source2', sim=self)];
    
    def get_resource(self):
        return Resource(name="Counter", unitName="John Doe", monitored=True, qType=PriorityQ, sim=self)

# M/G/1 queue, FIFO, two types of clients (Customer2 with less priority), one queue with preemption
class Queue5(BasicQueueModel):
        
    def __init__(self):
        super(Queue5, self).__init__()
        self.priority1 = 1
        
    def get_sources(self):
        return [FCFSSource('Source1', sim=self), FCFSSource('Source2', sim=self)];
    
    def get_resource(self):
        return Resource(name="Counter", unitName="John Doe", monitored=True, qType=PriorityQ, preemptable=True, sim=self)
     
        
############################################################
## Experiment
############################################################

modl = Queue1()
modl.run(aseed=seedVal)

nrwaiting = modl.counter.waitMon.timeAverage()
print ("----------\nAverage waiting = %6.4f\n"%(nrwaiting))
