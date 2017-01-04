""" Exercice 5: M/G/1 queue, FIFO, two types of clients 
    (Customer2 with less priority), one queue with preemption """

from SimPy.Simulation import Simulation,Process,Resource,Monitor,PriorityQ,hold,request,release
from random import expovariate, seed, randrange
import csv

###########################################################
## Experiment data
###########################################################

### General values ----------------------------------------
seedVal = 99998		# Seed to start simulation
# Time spended to attend a Customer (M/G/1 - fixed time)
serviceTime = [0.1, 0.2, 0.3, 0.4, 0.5]
# Maximum simulation time
maxTime = 10000000.0
numberOfSim = 1

### Customer one ------------------------------------------
lamb1 = 0.5		# rate of Customer one
NCustomer1 = 50000	# Number of Customers type one
priority1 = 100		# Priority number for Customer one
### Customer two ------------------------------------------
lamb2 = 0.3		# rate of Customer two
NCustomer2 = 50000	# Number of Customers type two
priority2 = 0		# Priority number foR Customer two

# [[customerName, arrival time, queue length ,time in queue, time been served, total time, end time]]
customersData = []
###########################################################
## Model components
###########################################################

class Source(Process):
    """ Source generates customers randomly """

    def generate(self, number, interval, typeOfClient, priority):       
        for i in range(number):
            c = Customer(name = "Customer%02d_%02d"%(typeOfClient,i,), sim=self.sim)
            self.sim.activate(c,c.visit(timeInBank=serviceTime[randrange(0,len(serviceTime))], counter=self.sim.counter, P=priority))
            t = expovariate(1.0/interval)
            yield hold,self,t

class Customer(Process):
    """ Customer arrives, is served and leaves """
        
    def visit(self, timeInBank=0, counter=0, P=0):
        customerName = self.name
        # arrival time
        arrive = self.sim.now()
        queuelen = len(self.sim.counter.waitQ)
        #print ("%8.3f %s: Queue is %d on arrival"%(self.sim.now(),self.name,Nwaiting))
        yield request,self,self.sim.counter,P

        # waiting time
        wait = self.sim.now() - arrive
        #print ("%8.3f %s: Waited %6.3f"%(self.sim.now(),self.name,wait))
        yield hold,self,timeInBank
        yield release,self,self.sim.counter                             

        finished = self.sim.now()
        #print ("%8.3f %s: Completed"%(self.sim.now(),self.name))

        totalTime = finished - arrive
        customersData.append([customerName,arrive,queuelen,wait,timeInBank,totalTime,finished])

class BankModel(Simulation):

    def run(self,aseed):
        self.initialize()
        seed(aseed)
        self.counter = Resource(name="Counter", unitName="John Doe", monitored=True, qType=PriorityQ, preemptable=True, sim=self)
        s1 = Source('Source1', sim=self)
        s2 = Source('Source2', sim=self)
        self.activate(s1, s1.generate(number=NCustomer1, interval=lamb1, typeOfClient=1 ,priority=priority1), at=10.0)
        self.activate(s2, s2.generate(number=NCustomer2, interval=lamb2, typeOfClient=2, priority=priority2))
        self.simulate(until=maxTime)

        avgwait = self.counter.waitMon.mean()
        avgqueue = self.counter.waitMon.timeAverage()
        avgutilization = self.counter.actMon.timeAverage()
        endOfSim = self.now()

        return [avgwait, avgqueue, avgutilization, endOfSim]

############################################################
## Experiment
############################################################
bankreception = []
for i in range(numberOfSim):
    mg1 = BankModel()
    mg1.startCollection(when=maxTime, monitors=mg1.allMonitors)
    result = mg1.run(seedVal + i)
    bankreception.append(result)

with open("traces.csv", "w") as f:
    writer = csv.writer(f)
    writer.writerows(customersData)
