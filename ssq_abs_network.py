# # --------------------------------------------------------------------------------------------------------------------
#  * This program is a next-event simulation of an open network made of more nodes, indipendent from each other.
#  * Each node is a single server queue with abstract scheduling policy. The arrival rate at the system is driven by
#  * a specified probability distribution, the same holds for the service rate. As a job arrives at the system, the 
#  * specific node/subsystem the job enters is chosen by a 'selection function', according to the specified policy
#  * (in this case, the node with minimum number of enqueued jobs is chosen).
#  *
#  * Name            : ssq_abs_network.c  
#  * Author          : A.Pontis & G.Bencivenni
#  # Language        : Python 3.9
#  # Latest Revision : 10/08/21
#  * -------------------------------------------------------------------------------------------------------------------

from statisticsTools import batchMeans, finiteHorizon, steadyStatePlotter, transientPlotter, transientPlotter2
from probabilityDistributions import getLambda, setLambda
from rngs import getSeed, plantSeeds, selectStream
from serviceCalls import GetServicePareto
from arrivalCalls import GetArrivalExpo
import sys, os, json
from rngs import random

START = 0.0  # initial time of the observation period      [minutes]
STOP = 840.0  # terminal (close the door) time              [minutes]
replicas = int(sys.argv[1])
STEADYLAMBDA = 2
TRANSIENTLAMBDA = 2
NODES = 3  # number of nodes (subsystems) in the network
turn = 0

LAMBDA = 0.0
SIMULATION_SEED = 0
transientList = list()

batchmean = {
    "seed": 0,
    "arrival_stream": 0,
    "service_stream": 1,
    "observation_period": 0,
    "interarrivals": 0.0,
    "batch_size": 0,
    "k": 0,
    "servers": 0,
    "acquisition_time": [],
    "avg_utilization1": [],
    "avg_utilization2": [],
    "avg_utilization3": [],
    "avg_utilization4": [],
    "avg_utilization5": [],
    "avg_utilization6": [],
    "global": {"avg_wait": [], "avg_delay": [], "avg_number": []},
    "c1": {"avg_wait": [], "avg_delay": [], "avg_number": []},
    "c2": {"avg_wait": [], "avg_delay": [], "avg_number": []},
    "c3": {"avg_wait": [], "avg_delay": [], "avg_number": []},
    "c4": {"avg_wait": [], "avg_delay": [], "avg_number": []},
    "c5": {"avg_wait": [], "avg_delay": [], "avg_number": []},
    "c6": {"avg_wait": [], "avg_delay": [], "avg_number": []},
    "mean_conditional_slowdown": {"(1.24)": [], "(2.65)": [], "(4.42)": [], "(8.26)": []},
    "index": []
}

output_dictionary = {
    "0": "Average Waiting Time (global)",
    "1": "Average Waiting Time (queue 1)",
    "2": "Average Delay (queue 1)",
    "3": "Average Waiting Time (queue 2)",
    "4": "Average Delay (queue 2)",
    "5": "Average Waiting Time (queue 3)",
    "6": "Average Delay (queue 3)"
}

batch_index = 0

transientStatistics = batchmean

''' ----------------------------- Next Event Data Structures and functions ----------------------------------------- '''


def indexUniformSelection(min, max):
    randomNumber = (min + (max - min) * random())
    indx = round(randomNumber)
    return indx


def resetTransientStatisticsdict():
    global transientStatistics

    transientStatistics = {
        "seed": 0,
        "arrival_stream": 0,
        "service_stream": 1,
        "observation_period": 0,
        "interarrivals": 0.0,
        "batch_size": 0,
        "k": 0,
        "servers": 0,
        "acquisition_time": [],
        "avg_utilization1": [],
        "avg_utilization2": [],
        "avg_utilization3": [],
        "avg_utilization4": [],
        "avg_utilization5": [],
        "avg_utilization6": [],
        "global": {"avg_wait": [], "avg_delay": [], "avg_number": []},
        "c1": {"avg_wait": [], "avg_delay": [], "avg_number": []},
        "c2": {"avg_wait": [], "avg_delay": [], "avg_number": []},
        "c3": {"avg_wait": [], "avg_delay": [], "avg_number": []},
        "c4": {"avg_wait": [], "avg_delay": [], "avg_number": []},
        "c5": {"avg_wait": [], "avg_delay": [], "avg_number": []},
        "c6": {"avg_wait": [], "avg_delay": [], "avg_number": []},
        "mean_conditional_slowdown": {"(1.24)": [], "(2.65)": [], "(4.42)": [], "(8.26)": []},
        "index": []
    }
    return True


def resetSteadyStateStatisticsdict():
    global batchmean

    batchmean = {
        "seed": 0,
        "arrival_stream": 0,
        "service_stream": 1,
        "observation_period": 0,
        "interarrivals": 0.0,
        "batch_size": 0,
        "k": 0,
        "servers": 0,
        "acquisition_time": [],
        "avg_utilization1": [],
        "avg_utilization2": [],
        "avg_utilization3": [],
        "avg_utilization4": [],
        "avg_utilization5": [],
        "avg_utilization6": [],
        "avg_utilization7": [],
        "avg_utilization8": [],
        "avg_utilization9": [],
        "global": {"avg_wait": [], "avg_delay": [], "avg_number": []},
        "c1": {"avg_wait": [], "avg_delay": [], "avg_number": []},
        "c2": {"avg_wait": [], "avg_delay": [], "avg_number": []},
        "c3": {"avg_wait": [], "avg_delay": [], "avg_number": []},
        "c4": {"avg_wait": [], "avg_delay": [], "avg_number": []},
        "c5": {"avg_wait": [], "avg_delay": [], "avg_number": []},
        "c6": {"avg_wait": [], "avg_delay": [], "avg_number": []},
        "mean_conditional_slowdown": {"(1.24)": [], "(2.65)": [], "(4.42)": [], "(8.26)": []}
    }
    return True


def resetTransientStatistics():
    # Reset the transient statistics when variable arrival time is chosen everytime we change the arrival time
    global START
    global area, index, number, sum
    global batchmean, r
    global simulationtype, transient_index

    area = 0
    for j in range(0, NODES):
        areas[j].node = 0.0
        areas[j].queue = 0.0
        nodes[j].index = 0

    sum = [accumSum() for i in range(0, NODES + 1)]

    for s in range(1, NODES + 1):
        sum[s].service = 0.0
        sum[s].served = 0

    START = t.current
    transient_index = index


def selectNode(nodes):
    # -------------------------------------------------
    # * return the index of the node with the minimum
    #   number of jobs in queue
    # * -----------------------------------------------
    i = 0
    choices = []
    choices.append(0)

    while (i < NODES - 1):  # check which is the node with the
        i += 1  # minimum number of enqueued jobs
        if (nodes[choices[0]].number > nodes[i].number):
            while (len(choices) != 0):
                choices.pop()
            choices.append(i)
        elif nodes[choices[0]].number == nodes[i].number:
            choices.append(i)
    # EndWhile

    candidates = len(choices)
    winner = indexUniformSelection(0, candidates - 1)

    return choices[winner]


def selectNodeUniform(nodes):
    # -------------------------------------------------
    # * return the index of the next node to be used.
    # * -----------------------------------------------
    selectStream(2)
    r = random()
    s = 0

    if r <= 0.33333333333333:
        s = 0
    else:
        if r <= 0.66666666666666:
            s = 1
        else:
            s = 2

    return s


def NextEvent(events):
    # ---------------------------------------
    # * return the index of the next event type
    # * ---------------------------------------

    i = 0

    while events[i].x == 0:  # find the index of the first 'active'
        i += 1  # element in the event list
    e = i

    while i < NODES:  # now, check the others to find which
        i += 1  # event type is most imminent
        if (events[i].x == 1) and (events[i].t < events[e].t):
            e = i

    return e


def NextBatch():
    # Get statistics for infinite horizon simulation
    global START
    global area, index, number, sum
    global batchmean, r

    wait = [0.0 for i in range(NODES)]
    delay = [0.0 for i in range(NODES)]
    queue_population = [0.0 for i in range(NODES)]

    for j in range(0, NODES):
        wait[j] = areas[j].node / nodes[j].index
        delay[j] = areas[j].queue / nodes[j].index
        queue_population[j] = areas[j].queue / (t.current - START)

    global_wait = area / b
    global_number = area / (t.current - START)

    d = 0.0

    for j in range(0, NODES):
        percentage = nodes[j].index / b
        if nodes[j].index != 0:
            d += (areas[j].queue / nodes[j].index) * percentage

    global_delay = d

    batchmean["global"]["avg_wait"].append(global_wait)
    batchmean["global"]["avg_delay"].append(global_delay)
    batchmean["global"]["avg_number"].append(global_number)

    if NODES >= 1: batchmean["c1"]["avg_wait"].append(wait[0])
    if NODES >= 2: batchmean["c2"]["avg_wait"].append(wait[1])
    if NODES >= 3: batchmean["c3"]["avg_wait"].append(wait[2])
    if NODES >= 4: batchmean["c4"]["avg_wait"].append(wait[3])
    if NODES >= 5: batchmean["c5"]["avg_wait"].append(wait[4])
    if NODES >= 6: batchmean["c6"]["avg_wait"].append(wait[5])

    if NODES >= 1: batchmean["c1"]["avg_delay"].append(delay[0])
    if NODES >= 2: batchmean["c2"]["avg_delay"].append(delay[1])
    if NODES >= 3: batchmean["c3"]["avg_delay"].append(delay[2])
    if NODES >= 4: batchmean["c4"]["avg_delay"].append(delay[3])
    if NODES >= 5: batchmean["c5"]["avg_delay"].append(delay[4])
    if NODES >= 6: batchmean["c6"]["avg_delay"].append(delay[5])

    if NODES >= 1: batchmean["c1"]["avg_number"].append(queue_population[0])
    if NODES >= 2: batchmean["c2"]["avg_number"].append(queue_population[1])
    if NODES >= 3: batchmean["c3"]["avg_number"].append(queue_population[2])
    if NODES >= 4: batchmean["c4"]["avg_number"].append(queue_population[3])
    if NODES >= 5: batchmean["c5"]["avg_number"].append(queue_population[4])
    if NODES >= 6: batchmean["c6"]["avg_number"].append(queue_population[5])

    batchmean["mean_conditional_slowdown"]["(1.24)"].append(1 + (area / b) / 1.24)
    batchmean["mean_conditional_slowdown"]["(2.65)"].append(1 + (area / b) / 2.65)
    batchmean["mean_conditional_slowdown"]["(4.42)"].append(1 + (area / b) / 4.42)
    batchmean["mean_conditional_slowdown"]["(8.26)"].append(1 + (area / b) / 8.26)

    for s in range(1, NODES + 1):
        batchmean["avg_utilization" + str(s)].append(sum[s].service / (t.current - START))

    area = 0

    for j in range(0, NODES):
        areas[j].node = 0.0
        areas[j].queue = 0.0
        nodes[j].index = 0

    sum = [accumSum() for i in range(0, NODES + 1)]

    for s in range(1, NODES + 1):
        sum[s].service = 0.0
        sum[s].served = 0

    START = t.current


def transientStats():
    # Get statistics for transient simulation
    global START
    global area, index, number, sum
    global transientStatistics
    global transientList

    wait = [0.0 for i in range(NODES)]
    delay = [0.0 for i in range(NODES)]
    queue_population = [0.0 for i in range(NODES)]

    if simulationtype == 0:
    # Fixed Interarrival rate
        for j in range(0, NODES):
            if nodes[j].index != 0:
                wait[j] = areas[j].node / nodes[j].index
                delay[j] = areas[j].queue / nodes[j].index
                queue_population[j] = areas[j].queue / t.current

        global_wait = area / index
        global_number = area / t.current

        d = 0.0

        for j in range(0, NODES):
            percentage = nodes[j].index / index
            if nodes[j].index != 0:
                d += (areas[j].queue / nodes[j].index) * percentage

        global_delay = d

        transientStatistics["global"]["avg_wait"].append(global_wait)
        transientStatistics["global"]["avg_delay"].append(global_delay)
        transientStatistics["global"]["avg_number"].append(global_number)

        if NODES >= 1: transientStatistics["c1"]["avg_wait"].append(wait[0])
        if NODES >= 2: transientStatistics["c2"]["avg_wait"].append(wait[1])
        if NODES >= 3: transientStatistics["c3"]["avg_wait"].append(wait[2])
        if NODES >= 4: transientStatistics["c4"]["avg_wait"].append(wait[3])
        if NODES >= 5: transientStatistics["c5"]["avg_wait"].append(wait[4])
        if NODES >= 6: transientStatistics["c6"]["avg_wait"].append(wait[5])

        if NODES >= 1: transientStatistics["c1"]["avg_delay"].append(delay[0])
        if NODES >= 2: transientStatistics["c2"]["avg_delay"].append(delay[1])
        if NODES >= 3: transientStatistics["c3"]["avg_delay"].append(delay[2])
        if NODES >= 4: transientStatistics["c4"]["avg_delay"].append(delay[3])
        if NODES >= 5: transientStatistics["c5"]["avg_delay"].append(delay[4])
        if NODES >= 6: transientStatistics["c6"]["avg_delay"].append(delay[5])

        if NODES >= 1: transientStatistics["c1"]["avg_number"].append(queue_population[0])
        if NODES >= 2: transientStatistics["c2"]["avg_number"].append(queue_population[1])
        if NODES >= 3: transientStatistics["c3"]["avg_number"].append(queue_population[2])
        if NODES >= 4: transientStatistics["c4"]["avg_number"].append(queue_population[3])
        if NODES >= 5: transientStatistics["c5"]["avg_number"].append(queue_population[4])
        if NODES >= 6: transientStatistics["c6"]["avg_number"].append(queue_population[5])

        transientStatistics["acquisition_time"].append(t.current)
        transientStatistics["index"].append(index)

        if NODES >= 1:
            if nodes[0].index != 0: transientStatistics["mean_conditional_slowdown"]["(1.24)"].append(
                1 + (areas[0].queue / nodes[0].index) / 1.24)
        if NODES >= 2:
            if nodes[1].index != 0: transientStatistics["mean_conditional_slowdown"]["(2.65)"].append(
                1 + (areas[1].queue / nodes[1].index) / 2.65)
        if NODES >= 3:
            if nodes[1].index != 0: transientStatistics["mean_conditional_slowdown"]["(4.42)"].append(
                1 + (areas[1].queue / nodes[1].index) / 4.42)
        if NODES >= 4:
            if nodes[2].index != 0: transientStatistics["mean_conditional_slowdown"]["(8.26)"].append(
                1 + (areas[2].queue / nodes[2].index) / 8.26)

        for s in range(1, NODES + 1):
            transientStatistics["avg_utilization" + str(s)].append(sum[s].service / t.current)

    else:
        # Variable Interarrival rate
        for j in range(0, NODES):
            if nodes[j].index != 0:
                wait[j] = areas[j].node / nodes[j].index
                delay[j] = areas[j].queue / nodes[j].index
            if t.current != START: queue_population[j] = areas[j].queue / (t.current - START)

        if index != transient_index:
            global_wait = area / (index - transient_index)
        else:
            global_wait = 0
        if t.current != START:
            global_number = area / (t.current - START)
        else:
            global_number = 0

        d = 0.0
        for j in range(0, NODES):
            if index == transient_index: break
            percentage = nodes[j].index / (index - transient_index)
            if nodes[j].index != 0:
                d += (areas[j].queue / nodes[j].index) * percentage
        global_delay = d

        transientStatistics["global"]["avg_wait"].append(global_wait)
        transientStatistics["global"]["avg_delay"].append(global_delay)
        transientStatistics["global"]["avg_number"].append(global_number)

        if NODES >= 1: transientStatistics["c1"]["avg_wait"].append(wait[0])
        if NODES >= 2: transientStatistics["c2"]["avg_wait"].append(wait[1])
        if NODES >= 3: transientStatistics["c3"]["avg_wait"].append(wait[2])
        if NODES >= 4: transientStatistics["c4"]["avg_wait"].append(wait[3])
        if NODES >= 5: transientStatistics["c5"]["avg_wait"].append(wait[4])
        if NODES >= 6: transientStatistics["c6"]["avg_wait"].append(wait[5])

        if NODES >= 1: transientStatistics["c1"]["avg_delay"].append(delay[0])
        if NODES >= 2: transientStatistics["c2"]["avg_delay"].append(delay[1])
        if NODES >= 3: transientStatistics["c3"]["avg_delay"].append(delay[2])
        if NODES >= 4: transientStatistics["c4"]["avg_delay"].append(delay[3])
        if NODES >= 5: transientStatistics["c5"]["avg_delay"].append(delay[4])
        if NODES >= 6: transientStatistics["c6"]["avg_delay"].append(delay[5])

        if NODES >= 1: transientStatistics["c1"]["avg_number"].append(queue_population[0])
        if NODES >= 2: transientStatistics["c2"]["avg_number"].append(queue_population[1])
        if NODES >= 3: transientStatistics["c3"]["avg_number"].append(queue_population[2])
        if NODES >= 4: transientStatistics["c4"]["avg_number"].append(queue_population[3])
        if NODES >= 5: transientStatistics["c5"]["avg_number"].append(queue_population[4])
        if NODES >= 6: transientStatistics["c6"]["avg_number"].append(queue_population[5])

        transientStatistics["acquisition_time"].append(t.current)
        transientStatistics["index"].append(index)

        if NODES >= 1:
            if nodes[0].index != 0: transientStatistics["mean_conditional_slowdown"]["(1.24)"].append(
                1 + (areas[0].queue / nodes[0].index) / 1.24)
        if NODES >= 2:
            if nodes[1].index != 0: transientStatistics["mean_conditional_slowdown"]["(2.65)"].append(
                1 + (areas[1].queue / nodes[1].index) / 2.65)
        if NODES >= 3:
            if nodes[1].index != 0: transientStatistics["mean_conditional_slowdown"]["(4.42)"].append(
                1 + (areas[1].queue / nodes[1].index) / 4.42)
        if NODES >= 4:
            if nodes[2].index != 0: transientStatistics["mean_conditional_slowdown"]["(8.26)"].append(
                1 + (areas[2].queue / nodes[2].index) / 8.26)

        for s in range(1, NODES + 1):
            if t.current != START:
                transientStatistics["avg_utilization" + str(s)].append(sum[s].service / (t.current - START))
            else:
                transientStatistics["avg_utilization" + str(s)].append(transientStatistics["avg_utilization" + str(s)][
                                                                           len(transientStatistics[
                                                                                   "avg_utilization" + str(s)]) - 1])


class event:
    t = None  # next event time
    x = None  # event status, 0 or 1
    node_position = None  # selected node


class subsystem:
    index = 0  # number of total completion from this specific node
    number = 0  # number of total jobs currently inside this node


class track:
    node = 0.0  # time integrated number in the node
    queue = 0.0  # time integrated number in the queue
    service = 0.0  # time integrated number in service


class time:
    arrival = -1  # next arrival time
    completion = -1  # next completion time
    current = -1  # current time
    next = -1  # next (most imminent) event time
    last = -1  # last arrival time


class accumSum:
    # accumulated sums of:
    service = None  # service times
    served = None  # number served


''' ------------------------------------------ Simulation settings ------------------------------------------------- '''

simulationtype = 0
choice = 0
type = 0
b = 512
k = 0
validation = 0
TRANSIENT_INDEX = 1.2
previous_index = 0

print(" Which type of simulation do you want to perform?\n")
print(" Finite Horizon ( Transient Statistics ) ............................. 0")
print(" Infinite Horizon ( Steady-State Statistics - Batch Means)  .......... 1")
choice = int(input("\n Please, type your choice here: "))

if choice == 1:
    b =             int(input("\n Type a size for the batch  (b)                 : "))
    k =             int(input("\n Type the number of batches (k)                 : "))
    STEADYLAMBDA =  float(input("\n Type a value for the interarrival time         : "))
    NODES =         int(input("\n Type the number of nodes [min:1, max:6]        : "))
    validation =    int(input("\n Are you validating the system? [yes:1 / no: 0] : "))
else:
    TRANSIENTLAMBDA =  float(input("\n Type a value for the interarrival time :"))
    NODES =            int(input("\n Type the number of nodes [min:1, max:6]:"))
    print(" Chose a type of Transient Simulation:\n")
    print(" Fixed Interarrival time ............................. 0")
    print(" Variable Interarrival time........................... 1")
    simulationtype = int(input("\n Please, type your choice here: "))

# Reading id from txt file to determine the number of ensamble to create
f = open("MG1_abs_network/id.txt", "r")
old_id = f.readline()
new_id = 1 + int(old_id)
f.close()
f = open("MG1_abs_network/id.txt", "w")
f.write(str(new_id))
f.close

# Create directory
dirName = "MG1_abs_network/ensemble" + str(new_id)
try:
    # Create target Directory
    os.mkdir(dirName)
    print("Directory ", dirName, " Created ")
except FileExistsError:
    print("Directory ", dirName, " already exists")

if len(sys.argv) == 3:
    STOP = float(sys.argv[2])

''' ------------------------------------------- Main Program ------------------------------------------------------- '''

plantSeeds(0)
r = 0

for i in range(0, replicas):
    TRANSIENT_MULTIPLIER = 8
    r += 1
    try:
        # Create target Directory
        replName = dirName + "/repl" + str(i + 1)
        os.mkdir(replName)
        print("Directory ", replName, " Created ")
    except FileExistsError:
        print("Directory ", replName, " already exists")
    stat = output_dictionary[str(choice)]

    index, number, area = 0, 0, 0
    t = time()

    events = [event() for i in range(NODES + 1)]  # this list represents all event types, each specified by index

    nodes = [subsystem() for i in range(NODES)]  # this list represents all nodes of the system

    areas = [track() for i in range(NODES)]  # this list is used to keep track of time integrated numbers in nodes

    sum = [accumSum() for i in
           range(NODES + 1)]  # this list is used to represent each server status at the current time

    START = 0.0
    t.current = START
    arrivalTemp = START  # global temp var for getArrival function     [minutes]

    SIMULATION_SEED = getSeed()

    if choice == 0:
        # Finite Horizon Simulation
        LAMBDA = TRANSIENTLAMBDA
        setLambda(LAMBDA)
    else:
        # Infinite Horizon Simulation
        LAMBDA = STEADYLAMBDA
        setLambda(LAMBDA)

    # initialization of the first arrival event
    arrivalTemp += GetArrivalExpo()
    events[0].t = arrivalTemp
    events[0].x = 1

    for s in range(1, NODES + 1):
        events[s].t = START  # this value is arbitrary because
        events[s].x = 0  # all servers are initially idle
        sum[s].service = 0.0
        sum[s].served = 0

    period = 0
    disp = 0
    mod = 30
    old_index = 0
    batch_index = 0
    transient_index = 0

    while (events[0].x != 0) or (number != 0):
        # ------------------These commands are used to produce the series of output statistics at runtime---------------
        if index % b == 0 and choice == 1 and index != 0:
            if not (batch_index == k or old_index == index):
                NextBatch()
                batch_index += 1
                old_index = index

        if simulationtype == 1:
            # Variation of LAMBDA during the day
            if choice == 0 and t.current >= 120 and period == 0:
                period += 1
                setLambda(1.5)
                LAMBDA = getLambda()
                resetTransientStatistics()

            if choice == 0 and t.current >= 300 and period == 1:
                period += 1
                setLambda(2.0)
                LAMBDA = getLambda()
                resetTransientStatistics()

            if choice == 0 and t.current >= 420 and period == 2:
                period += 1
                setLambda(1)
                LAMBDA = getLambda()
                resetTransientStatistics()

            if choice == 0 and t.current >= 700 and period == 3:
                period += 1
                setLambda(3.0)
                LAMBDA = getLambda()
                resetTransientStatistics()

        disp += 1
        if (choice == 0 and index % (round(TRANSIENT_INDEX * TRANSIENT_MULTIPLIER)) == 0 and index != 0 and simulationtype == 0):
            transientStats()   
            TRANSIENT_MULTIPLIER = TRANSIENT_MULTIPLIER * TRANSIENT_INDEX
        if (choice == 0 and index % (round(5)) == 0 and index != 0 and previous_index !=index and simulationtype == 1):
            transientStats()           
            previous_index = index
        # ------------------------------------------------------------------------------------------------------------------------------

        e = NextEvent(events)  # next event index

        t.next = events[e].t  # next event time

        area += (t.next - t.current) * number  # update integral

        for i in range(0, NODES):
            areas[i].node += (t.next - t.current) * nodes[i].number  # update integral for each specific node
            if nodes[i].number > 0:
                areas[i].queue += (t.next - t.current) * (
                            nodes[i].number - 1)  # update integral for each specific queue

        t.current = t.next  # advance the clock

        if e == 0:
            # process an ARRIVAL
            events[0].node_position = selectNodeUniform(nodes)
            nodes[events[0].node_position].number += 1
            number += 1

            current_node_number = nodes[events[0].node_position].number

            # schedule the next arrival event
            arrivalTemp += GetArrivalExpo()
            events[0].t = arrivalTemp  # get the arrival time

            if events[0].t > STOP:
                # end of observation time
                events[0].x = 0

            if current_node_number == 1:
                # schedule the next completion event for this node
                service = GetServicePareto()
                s = events[0].node_position + 1
                # update the selected server's state
                sum[s].service += service
                sum[s].served += 1
                events[s].t = t.current + service
                events[s].x = 1
        else:
            # process a COMPLETION
            s = e
            number -= 1  # decrease the number of jobs in the system
            index += 1  # increase the number of processed jobs in the system
            nodes[s - 1].number -= 1  # decrease the number of jobs in the node
            nodes[s - 1].index += 1  # increase the number of processed jobs in the node

            current_node_number = nodes[s - 1].number

            if current_node_number >= 1:
                # schedule the next completion event
                service = GetServicePareto()
                # update the selected server's state
                sum[s].service += service
                sum[s].served += 1
                events[s].t = t.current + service
            else:
                events[s].x = 0

    # Record simulation results on a header JSON file
    if choice == 0:
        # Finite Horizon
        transientList.append(transientStatistics)
        transientStatistics["seed"] = SIMULATION_SEED
        transientStatistics["interarrivals"] = LAMBDA
        transientStatistics["observation_period"] = STOP
        transientStatistics["servers"] = NODES
        transientStatistics["batch_size"] = 0

        with open(replName + "/transientStatistics" + str(r) + ".json", 'w') as json_file:
            json.dump(transientStatistics, json_file, indent=4)
        json_file.close()

        finiteHorizon(transientStatistics)

        resetTransientStatisticsdict()
    else:
        # Infinite Horizon
        batchmean["seed"] = SIMULATION_SEED
        batchmean["interarrivals"] = LAMBDA
        batchmean["observation_period"] = STOP
        batchmean["servers"] = NODES
        batchmean["k"] = batch_index
        batchmean["batch_size"] = b

        with open(replName + "/batchMeans" + str(batch_index) + ".json", 'w') as json_file:
            json.dump(batchmean, json_file, indent=4)
        json_file.close()

        batchMeans(replName, batchmean, 1)

        resetSteadyStateStatisticsdict()

# Function to plot table and graph
if choice == 1:
    steadyStatePlotter(dirName, 1, validation)
else:
    #transientPlotter(dirName, 1, transientList, simulationtype)
    transientPlotter2(dirName, 1, transientList, simulationtype)

