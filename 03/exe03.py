""" Exercice 2: M/G/1 queue, LIFO, two types of clients, no priority,
    no preemption, no differences between Customer 1 and 2 """

from SimPy.Simulation import Simulation,Process,Resource,Monitor,PriorityQ,hold,request,release
from random import expovariate, seed

###########################################################
## Experiment data
###########################################################

### General values ----------------------------------------
seedVal = 99999		# Seed to start simulation
# Time spended to attend a Customer (M/G/1 - fixed time)
serviceTime = 5.0
# Maximum simulation time
maxTime = 400.0

### Customer one ------------------------------------------
lamb1 = 1.0		# rate of Customer one
NCustomer1 = 5		# Number of Customers type one
priority1 = 0		# Priority number for Customer one
### Customer two ------------------------------------------
lamb2 = 10.0		# rate of Customer two
NCustomer2 = 5		# Number of Customers type two
priority2 = 0		# Priority number foR Customer two

###########################################################
## Model components
###########################################################

class Source(Process):
	""" Source generates customers randomly """

	def generate(self, number, interval, typeOfClient, priority):
		for i in range(number):
		    c = Customer(name = "Customer%02d_%02d"%(typeOfClient,i,), sim=self.sim)
		    self.sim.activate(c,c.visit(timeInBank=serviceTime, counter=self.sim.counter, P=self.sim.now()))
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

class BankModel(Simulation):

	def run(self,aseed):
		self.initialize()
		seed(aseed)
		self.counter = Resource(name="Counter", unitName="John Doe", monitored=True, qType=PriorityQ, preemptable=True, sim=self)
		s1 = Source('Source1', sim=self)
		s2 = Source('Source2', sim=self)
		self.activate(s1, s1.generate(number=NCustomer1, interval=lamb1, typeOfClient=1 ,priority=priority1))
		self.activate(s2, s2.generate(number=NCustomer2, interval=lamb2, typeOfClient=2, priority=priority2))
		self.simulate(until=maxTime)

		return

############################################################
## Experiment
############################################################

modl = BankModel()
modl.run(aseed=seedVal)

nrwaiting = modl.counter.waitMon.timeAverage()
print ("----------\nAverage waiting = %6.4f\n"%(nrwaiting))
