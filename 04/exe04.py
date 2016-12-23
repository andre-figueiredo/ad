""" 1 and 4"""
from SimPy.Simulation import Simulation,Process,Resource,Monitor,PriorityQ,hold,request,release
from random import expovariate, seed

## Experiment data -------------------------

# Just a seed to start the simulation
seedVal = 99999
# Time aways in minutes
#
# Time spended to attend a Customer (M/G/1 - fixed time)
serviceTime = 12.0
# Maximum simulation time
maxTime = 400.0
# rate of Customer one
lamb1 = 1.0
# rate of Customer two
lamb2 = 10.0
# Number of Customers type one
NCustomer1 = 10
# Number of Customers type two
NCustomer2 = 100

## Model components ------------------------

class Source(Process):
    """ Source generates customers randomly """

    def generate(self, number, interval, typeOfClient, priority):       
        for i in range(number):
            c = Customer(name = "Customer%02d_%02d"%(typeOfClient,i,), sim=self.sim)
            self.sim.activate(c,c.visit(timeInBank=serviceTime, counter=self.sim.counter, P=priority))
            t = expovariate(1.0/interval)
            yield hold,self,t

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


## Model ------------------------------
class BankModel(Simulation):

	def run(self,aseed):
	    self.initialize()
	    seed(aseed)
	    self.counter = Resource(name="Counter", unitName="John Doe", monitored=True, qType=PriorityQ, sim=self)
	    s1 = Source('Source1', sim=self)
	    s2 = Source('Source2', sim=self)
	    self.activate(s1, s1.generate(number=NCustomer1, interval=lamb1, typeOfClient=1 ,priority=100))
	    self.activate(s2, s2.generate(number=NCustomer2, interval=lamb2, typeOfClient=2, priority=0))
	    self.simulate(until=maxTime)
	
	    return

## Experiment ------------------------------

modl = BankModel()
modl.run(aseed=seedVal)

nrwaiting = modl.counter.waitMon.timeAverage()
print ("----------\nAverage waiting = %6.4f\n"%(nrwaiting))
