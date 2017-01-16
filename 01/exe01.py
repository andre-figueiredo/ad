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
seedVal = 123456
# Time spended to attend a Customer (M/G/1 - fixed time)
serviceTime = [0.1, 0.2, 0.3, 0.4, 0.5]
# Maximum simulation time
maxTime = float("inf")
# How many time repeat simulation?
numberOfSim = 10
# [[customerName, arrival time, time in queue, time been served, total time, end time]]
customersData = []
customers1Data = []
customers2Data = []

### Customer one ------------------------------------------
#lamb1 = 1.0		# rate of Customer one
NCustomer1 = 100000 	# Number of Customers type one
priority1 = 0		# Priority number for Customer one
### Customer two ------------------------------------------
#lamb2 = 1.0		# rate of Customer two
NCustomer2 = 100000	# Number of Customers type two
priority2 = 0 		# Priority number foR Customer two

###########################################################
## Model components
###########################################################

class Source(Process):
    """ Source generates customers randomly """

    residual_time = []

    def generate(self, number, interval, typeOfClient, priority):
        for i in range(number):
            c = Customer(name="Customer%02d_%02d" % (typeOfClient, i,), sim=self.sim)
            self.sim.activate(c, c.visit(timeInBank=serviceTime[randrange(0, len(serviceTime))], counter=self.sim.counter, P=priority))
            t = expovariate(interval)
            yield hold, self, t


class Customer(Process):
    """ Customer arrives, is served and leaves """
        
    def visit(self, timeInBank=0, counter=0, P=0):
        customerName = self.name
        # arrival time
        arrive = self.sim.now()
        queuelen = len(self.sim.counter.waitQ)
        #print ("%8.3f %s: Queue is %d on arrival"%(self.sim.now(),self.name,queuelen))
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
        self.activate(s1, s1.generate(number=NCustomer1, interval=1.0/lamb1, typeOfClient=1, priority=priority1))
        self.activate(s2, s2.generate(number=NCustomer2, interval=1.0/lamb2, typeOfClient=2, priority=priority2))
        self.simulate(until=maxTime)

        avgwait = self.counter.waitMon.mean()
        avgqueue = self.counter.waitMon.timeAverage()
        avgutilization = self.counter.actMon.timeAverage()
        endOfSim = self.now()

        return [avgwait, avgqueue, avgutilization, endOfSim]


############################################################
## Experiment
############################################################
# To get general information from a specific simulation
bankreception = []

# To iterate lambda value
ilambda = 0.1

# Array to hold information about variation of E[U]
finalPlot = []
for i in range(numberOfSim):
    lamb1 = lamb2 = ilambda
    mg1 = BankModel()
    mg1.startCollection(when=maxTime, monitors=mg1.allMonitors)
    result = mg1.run(seedVal + i)
    bankreception.append(result)

    ############################################################
    ## Results
    ############################################################

    # Separating Customers1 and Customers2
    for i in range(len(customersData)):
        if customersData[i][0].startswith("Customer01"):
            customers1Data.append(customersData[i])
        else:
            customers2Data.append(customersData[i])

    # Organizing data to numPy array
    customersData = np.array(customersData)
    customers1Data = np.array(customers1Data)
    customers2Data = np.array(customers2Data)
    customersDataNoNames = customersData[:, 1:].astype(float)
    customers1DataNoNames = customers1Data[:, 1:].astype(float)
    customers2DataNoNames = customers2Data[:, 1:].astype(float)

    # To help index
    # [[arrival time, queue length ,time in queue, time been served, total time, end time]]
    arrive = 0
    queueLen = 1
    wait = 2
    timeInBank = 3
    totalTime = 4
    finished = 5

    # Usefull informations
    avgs = np.mean(customersDataNoNames, axis=0)
    variances = np.var(customersDataNoNames, axis=0)
    avgsCustomers1 = np.mean(customers1DataNoNames, axis=0)
    variancesCustomers1 = np.var(customers1DataNoNames, axis=0)
    avgsCustomers2 = np.mean(customers2DataNoNames, axis=0)
    variancesCustomers2 = np.var(customers2DataNoNames, axis=0)
    sumAllValues = np.sum(customersDataNoNames, axis=0)
    sumAllValuesCustomer1 = np.sum(customers1DataNoNames, axis=0)
    sumAllValuesCustomer2 = np.sum(customers2DataNoNames, axis=0)

    # End of Simulation in minutes
    endOfSim = bankreception[0][3]

    # E[X_r] = E[X^2] / 2*E[X]. With E[X^2] = Var(X) + (E[X])^2
    expResidualTime = (variances[timeInBank] + (avgs[timeInBank] ** 2)) / (2.0 * avgs[timeInBank])
    # E[X_r1] = E[X1^2] / 2*E[X1]. With E[X1^2] = Var(X1) + (E[X1])^2
    expResidualTimeCustomer1 = (variancesCustomers1[timeInBank] + (avgsCustomers1[timeInBank] ** 2)) / (2.0 * avgsCustomers1[timeInBank])
    # E[X_r2] = E[X2^2] / 2*E[X2]. With E[X2^2] = Var(X2) + (E[X2])^2
    expResidualTimeCustomer2 = (variancesCustomers2[timeInBank] + (avgsCustomers2[timeInBank] ** 2)) / (2.0 * avgsCustomers2[timeInBank])

    # pendingService hold the E[U] calculated by simulation
    pendingService = avgs[wait]

    # mu, rho etc
    mi = 1.0 / avgs[timeInBank]
    rho = sumAllValues[timeInBank] / endOfSim
    rho1 = sumAllValuesCustomer1[timeInBank] / endOfSim
    rho2 = sumAllValuesCustomer2[timeInBank] / endOfSim
    pendingServiceCalc = rho * expResidualTime / (1.0 - rho)
    pendingServiceCalcQ2 = (expResidualTimeCustomer1 * rho1) +\
                           (expResidualTimeCustomer2 * rho2) +\
                           ((rho ** 2 * expResidualTime) / (1.0 - rho))

    finalPlot.append([lamb1, lamb2, lamb1+lamb2, pendingService, pendingServiceCalcQ2])

    ############################################################
    ## Prints
    ############################################################
    ####### Questao 1
    """print("###### Questao 1 #######\n")
    print("###### Informacoes gerais #########")
    print("X => v.a que mede o tempo de atendimento de um cliente")
    print("Simulacao finalizada no minuto: %0.8f" % (endOfSim))
    print("Numero total de clientes atendidos: %d"% (len(customersData)))
    print("Lambda1 = %0.8f; Lambda2 = %0.8f; Lambda = %0.8f" % (lamb1, lamb2, lamb1+lamb2))
    print("Mi = %0.8f" % (mi))
    print("E[X] = %0.8f" % (avgs[timeInBank]))
    print("Var(X) = %0.8f " % (variances[timeInBank]))
    print("E[X_r] = %0.8f " % (expResidualTime))
    print("(sim) Rho1 = %0.8f" % (rho1))
    print("(sim) Rho2 = %0.8f" % (rho2))
    print("(sim) Rho = %0.8f" % (rho))
    print("\n##### Resposta #######")
    print("(sim) E[U] = %0.8f"%(pendingService))
    print("(calc) E[U] = %0.8f"%(pendingServiceCalc))
    print("\n\n")"""
    ####### Questao 2
    print("###### Questao 2 #######\n")
    print("(sim) Rho1 = %0.8f" % (rho1))
    print("(sim) Rho2 = %0.8f" % (rho2))
    print("(sim) Rho = %0.8f" % (rho))
    print("E[X_r1] = %0.8f " % (expResidualTimeCustomer1))
    print("E[X_r2] = %0.8f " % (expResidualTimeCustomer2))
    print("E[X_r] = %0.8f " % (expResidualTime))
    print("(sim) E[U] = %0.8f" % (pendingService))
    print("(calc) E[U] = %0.8f" % (pendingServiceCalcQ2))
    print("\n\n")
    # Clear customersData to the next iteration
    customersData = []
    customers1Data = []
    customers2Data = []
    ilambda += 0.1

with open("traces1.2.csv", "w") as f:
    writer = csv.writer(f)
    writer.writerows(finalPlot)
