""" Exercice 1: M/G/1 queue, two types of clients,
    no priority queue and FIFO. """

from SimPy.Simulation import Simulation, Process, Resource, Monitor, PriorityQ, hold, request, release
from random import expovariate, seed, randrange
import numpy as np
import csv

###########################################################
## Experiment data
###########################################################

### General values ----------------------------------------
# Seed to start simulation
seedVal = 99998
# Time spended to attend a Customer (M/G/1 - fixed time)
serviceTime = [0.1, 0.2, 0.3, 0.4, 0.5]
# Maximum simulation time
maxTime = 10000000.0
# How many time repeat simulation?
numberOfSim = 1

### Customer one ------------------------------------------
lamb1 = 0.1		# rate of Customer one
NCustomer1 = 50000		# Number of Customers type one
priority1 = 0		# Priority number for Customer one
### Customer two ------------------------------------------
lamb2 = 0.1		# rate of Customer two
NCustomer2 = 50000		# Number of Customers type two
priority2 = 0		# Priority number foR Customer two

# [[customerName, arrival time, time in queue, time been served, total time, end time]]
customersData = []

###########################################################
## Model components
###########################################################

class Source(Process):
    """ Source generates customers randomly """

    def generate(self, number, interval, typeOfClient, priority):
        for i in range(number):
            c = Customer(name="Customer%02d_%02d" % (typeOfClient, i,), sim=self.sim)
            self.sim.activate(c, c.visit(timeInBank=serviceTime[randrange(0,len(serviceTime))], counter=self.sim.counter, P=priority))
            t = expovariate(interval)
            yield hold, self, t


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
    def run(self, aseed):
        self.initialize()
        seed(aseed)
        self.counter = Resource(name="Counter", unitName="John Doe", monitored=True, monitorType=Monitor,
                                qType=PriorityQ, sim=self, capacity=1)
        s1 = Source('Source1', sim=self)
        s2 = Source('Source2', sim=self)
        self.activate(s1, s1.generate(number=NCustomer1, interval=lamb1, typeOfClient=1, priority=priority1))
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

############################################################
## Results
############################################################

totalServiceTime = 0.0
totalTimeSystemInUse = 0.0
totalTimeWaitCustomer = 0.0
totalAttendedCustomers = float(len(customersData))
customers1Data = []
customers2Data = []

# Para facilitar saber qual a posicao no array de cada coisa
# [[customer name, arrival time, queue length ,time in queue, time been served, total time, end time]]
name = 0
arrive = 1
queueLen = 2
wait = 3
timeInBank = 4
totalTime = 5
finished = 6

for i in range(len(customersData)):
    totalServiceTime += customersData[i][timeInBank]
    totalTimeWaitCustomer += customersData[i][wait]
    totalTimeSystemInUse += customersData[i][totalTime]

    if customersData[i][name].startswith("Customer01"):
        customers1Data.append(customersData[i])
    else:
        customers2Data.append(customersData[i])

serviceTimeAverage = totalServiceTime / totalAttendedCustomers
pendingService = totalTimeWaitCustomer / totalAttendedCustomers

# Calculando a variancia para poder usar como segundo momento vulgo E[X^2]
# e assim conseguir calcular o x residual = E[X^2] / (2 * E[X])
total = 0
for i in range(len(customersData)):
    total += ((customersData[i][timeInBank] - serviceTimeAverage) ** 2)

variancia = total / (totalAttendedCustomers - 1)
mi = 1.0 / serviceTimeAverage

# Rho eh o percentual de uso do sistema. Logo estou calculando atraves dos dados.
rho = (lamb1+lamb2)/mi
rho1 = lamb1/mi
rho2 = lamb2/mi
expResidualTime = variancia / (2 * serviceTimeAverage)
expU = (rho * expResidualTime) / (1.0 - rho)

############################################################
## Prints
############################################################

####### Questao 1
print("\n\n###### Questao 1 #######")
print("E[X^2] = %0.8f" % (variancia))
print("E[X] = %0.8f" % (serviceTimeAverage))
print("Mi = %0.8f" % (mi))
print("Rho = %0.8f" % (rho))
print("E[Xr] = %0.8f" % (expResidualTime))
print("E[U] calculado = %0.8f" % (expU))
print("E[U] simulado = %0.8f" % (pendingService))
print("Erro = %0.8f"%(pendingService-expU))
####### Questao 2
