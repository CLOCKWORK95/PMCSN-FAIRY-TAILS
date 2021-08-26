# ------------------------------------------------------------------------------------------------------------------------ 
# * This program is a next-event simulation of a multi-server, multi-queue service node.
# * The service node is assumed to be initially idle, no arrivals are permitted after the terminal
# * time STOP and the node is then purged by processing any remaining jobs. Scheduling policy is considered 
# * to be size-based without preeption.
# *
# * Name              : msmq_sb.py (Multi-Server Multi-Queue, Size Based policy)
# * Authors           : A.Pontis & G.Bencivenni
# * Language          : Python 3.9.0
# * Latest Revision   : 7/27/2021
# * ---------------------------------------------------------------------------------------------------------------------- 
# */

from statisticsTools import batchMeans, finiteHorizon, steadyStatePlotter, transientPlotter
from probabilityDistributions import getLambda, setLambda
from rngs import getSeed, plantSeeds
from arrivalCalls import GetArrivalExpo
from serviceCalls import GetServicePareto, GetServiceUniform
import sys, json, os


START =   0.0                                                         # initial (open the door) time       [ minutes ] 
STOP  =   840.0                                                       # terminal (close the door) time     [ minutes ]
replicas = int(sys.argv[1])

QUEUES = 3                                                            # number of queues in the node
SERVERS = 3                                                           # number of servers in the node      
multiqueue = None                                                     # multi queues size-based structure 
X1 = 1.5                                                              # first size boundary                [ minutes ]
X2 = 4.5                                                              # second size boundary               [ minutes ]

batchmean = {
  "seed" : 0,
  "arrival_stream" : 0,
  "service_stream" : 1,
  "observation_period" : 0,
  "interarrivals" : 0.0,
  "batch_size" : 0,
  "k" : 0,
  "servers" : 0,
  "acquisition_time" : [],
  "avg_utilization1" : [],
  "avg_utilization2" : [],
  "avg_utilization3" : [],
  "avg_utilization4" : [],
  "avg_utilization5" : [],
  "avg_utilization6" : [],
  "avg_utilization7" : [],
  "avg_utilization8" : [],
  "avg_utilization9" : [],
  "global" : { "avg_wait": [] , "avg_delay":[], "avg_number" : []  },
  "q1" : { "avg_wait": [] , "avg_delay": [] , "avg_number" : [] },
  "q2" : { "avg_wait": [] , "avg_delay": [] , "avg_number" : []  },
  "q3" : { "avg_wait": [] , "avg_delay": [] , "avg_number" : []  },
  "mean_conditional_slowdown" : { "(1.24)": [] , "(2.65)": [] , "(4.42)": [] , "(8.26)": []  }
}

transientStatistics = batchmean

batch_index = 0

LAMBDA = 0.0
SIMULATION_SEED = 0

output_dictionary = {
  "0" : "Average Waiting Time (global)",
  "1" : "Average Waiting Time (queue 1)",
  "2" : "Average Delay (queue 1)",
  "3" : "Average Waiting Time (queue 2)",
  "4" : "Average Delay (queue 2)",
  "5" : "Average Waiting Time (queue 3)",
  "6" : "Average Delay (queue 3)"
}

''' ----------------- Next Event Data Structures --------------------------------------------------------------------------------------- '''

def NextEvent(events):
# ---------------------------------------
# * return the index of the next event type
# * ---------------------------------------

  i = 0

  while (events[i].x == 0):                                           # find the index of the first 'active' 
    i += 1                                                            # element in the event list             
  #EndWhile
  e = i

  while (i < SERVERS):                                                # now, check the others to find which  
    i += 1                                                            # event type is most imminent          
    if ((events[i].x == 1) and (events[i].t < events[e].t)):
      e = i
  #EndWhile
  
  return (e)


def FindOne(events):
# -----------------------------------------------------
# * return the index of the available server idle longest
# * -----------------------------------------------------

  i = 1

  while (events[i].x == 1):                                           # find the index of the first available 
    i += 1                                                            # (idle) server                         
  #EndWhile
  s = i
  while (i < SERVERS):                                                # now, check the others to find which   
    i += 1                                                            # has been idle longest                 
    if ((events[i].x == 0) and (events[i].t < events[s].t)):
      s = i
  #EndWhile 

  return (s)


def NextBatch():

  global START
  global area, index, number, sum
  global area_queues, index_queues, number_queues, tot_services_for_queue
  global batchmean

  wait = [0.0, 0.0, 0.0]
  delay = [0.0, 0.0, 0.0]
  queue_population = [0.0, 0.0, 0.0]

  for j in range ( 0, QUEUES ):

    wait[j] = area_queues[j] / index_queues[j] + tot_services_for_queue[j] / index_queues[j]
    delay[j] = area_queues[j] / index_queues[j]
    queue_population[j] = area_queues[j] / t.current

  d = 0.0 

  for j in range( 0, QUEUES ):
     percentage = index_queues[j] / b
     if index_queues[j] != 0:
      d += ( area_queues[j] / index_queues[j] ) * percentage
  
  global_wait = area / b
  global_delay = d
  global_number = area / t.current

  batchmean["global"]["avg_wait"].append(global_wait)
  batchmean["global"]["avg_delay"].append(global_delay)
  batchmean["global"]["avg_number"].append(global_number)

  batchmean["q1"]["avg_wait"].append(wait[0])
  batchmean["q2"]["avg_wait"].append(wait[1])
  batchmean["q3"]["avg_wait"].append(wait[2])

  batchmean["q1"]["avg_delay"].append(delay[0])
  batchmean["q2"]["avg_delay"].append(delay[1])
  batchmean["q3"]["avg_delay"].append(delay[2])

  batchmean["q1"]["avg_number"].append(queue_population[0])
  batchmean["q2"]["avg_number"].append(queue_population[1])
  batchmean["q3"]["avg_number"].append(queue_population[2])

  batchmean["mean_conditional_slowdown"]["(1.24)"].append( 1 + (area_queues[0] / index_queues[0]) / 1.24 )
  batchmean["mean_conditional_slowdown"]["(2.65)"].append( 1 + (area_queues[1] / index_queues[1]) / 2.65 )
  batchmean["mean_conditional_slowdown"]["(4.42)"].append( 1 + (area_queues[1] / index_queues[1]) / 4.42 )
  batchmean["mean_conditional_slowdown"]["(8.26)"].append( 1 + (area_queues[2] / index_queues[2]) / 8.26 )

  for s in range( 1,  SERVERS + 1 ):
    batchmean["avg_utilization" + str(s)].append( sum[s].service / (t.current-START) )

  area = 0

  #number_queues = [ 0, 0, 0 ]                                                       
  index_queues  = [ 0, 0, 0 ]                                           
  area_queues   = [ 0.0, 0.0, 0.0 ]                                    
  tot_services_for_queue = [ 0.0, 0.0, 0.0 ]

  sum = [ accumSum() for i in range( 0, SERVERS + 1 ) ]

  for s in range( 1, SERVERS + 1 ):  
    sum[s].service = 0.0
    sum[s].served  = 0

  START = t.current


def transientStats():

  global START
  global area, index, number, sum
  global area_queues, index_queues, number_queues, tot_services_for_queue
  global transientStatistics

  wait = [0.0, 0.0, 0.0]
  delay = [0.0, 0.0, 0.0]
  queue_population = [0.0, 0.0, 0.0]

  for j in range ( 0, QUEUES ):

    try:
      wait[j] = area_queues[j] / index_queues[j] + tot_services_for_queue[j] / index_queues[j]
      delay[j] = area_queues[j] / index_queues[j]
      queue_population[j] = area_queues[j] / t.current
    except:
      wait[j] = 0.0
      delay[j] = 0.0
      queue_population[j] = 0.0
  
  d = 0.0
  for j in range( 0, QUEUES ):
    try:
      d += ( area_queues[j] / index_queues[j] ) * ( index_queues[j] / index )
    except:
      d = 0.0
  try: 
    global_wait = area / index
    global_delay = d
    global_number = area / t.current
  except:
    global_wait = 0.0
    global_number = 0.0

  transientStatistics["global"]["avg_wait"].append(global_wait)
  transientStatistics["global"]["avg_delay"].append(global_delay)
  transientStatistics["global"]["avg_number"].append(global_number)

  transientStatistics["q1"]["avg_wait"].append(wait[0])
  transientStatistics["q2"]["avg_wait"].append(wait[1])
  transientStatistics["q3"]["avg_wait"].append(wait[2])

  transientStatistics["q1"]["avg_delay"].append(delay[0])
  transientStatistics["q2"]["avg_delay"].append(delay[1])
  transientStatistics["q3"]["avg_delay"].append(delay[2])

  transientStatistics["q1"]["avg_number"].append(queue_population[0])
  transientStatistics["q2"]["avg_number"].append(queue_population[1])
  transientStatistics["q3"]["avg_number"].append(queue_population[2])

  transientStatistics["acquisition_time"].append(t.current)

  try:
    transientStatistics["mean_conditional_slowdown"]["(1.24)"].append( 1 + (area_queues[0] / index_queues[0]) / 1.24 )
    transientStatistics["mean_conditional_slowdown"]["(2.65)"].append( 1 + (area_queues[1] / index_queues[1]) / 2.65 )
    transientStatistics["mean_conditional_slowdown"]["(4.42)"].append( 1 + (area_queues[1] / index_queues[1]) / 4.42 )
    transientStatistics["mean_conditional_slowdown"]["(8.26)"].append( 1 + (area_queues[2] / index_queues[2]) / 8.26 )
  except :
    transientStatistics["mean_conditional_slowdown"]["(1.24)"].append( 0.0 )
    transientStatistics["mean_conditional_slowdown"]["(2.65)"].append( 0.0 )
    transientStatistics["mean_conditional_slowdown"]["(4.42)"].append( 0.0 )
    transientStatistics["mean_conditional_slowdown"]["(8.26)"].append( 0.0 )

  for s in range( 1,  SERVERS + 1 ):
    transientStatistics["avg_utilization" + str(s)].append( sum[s].service / (t.current-START) )
  
 


class event:

  t = None                                                            # next event time
  x = None                                                            # event status, 0 or 1
  size = None                                                         # size of the incoming job, (if event is an arrival)
  priority = None                                                     # from which queue the job has come (if event is a completion)

class time:

  current = None                                                      # current time                     
  next = None                                                         # next (most imminent) event time   

class accumSum:
                                                                      # accumulated sums of:               
  service = None                                                      # service times                    
  served = None                                                       # number served                



''' ------------------------ Multi Queues Structures and Methods ----------------------------------------------------------------- '''

class block:

  # each block represents an element (job) in the queue 

  arrival_time = None
  size = None
  priority = None

  def __init__( self, event ):

    global X1, X2

    self.arrival_time = event.t
    self.size = event.size

    if self.size <= X1 : 
      # Max Priority
      self.priority = 0
    elif self.size > X1 and self.size <= X2 : 
      # Middle Priority
      self.priority = 1
    else : 
      # Lowest Priority
      self.priority = 2


def initialize_queue_structure():

  global multiqueue
  
  multiqueue = [ [] for i in range( QUEUES ) ]


def enqueue( event ):

  global multiqueue

  new_block = block( event )

  multiqueue[ new_block.priority ].append( new_block )

  return new_block.priority


def serve():

  global multiqueue

  for queue in multiqueue:

    if len( queue ) > 0:
      b = queue.pop( 0 )
      return b.size, b.priority

  return -1


''' ---------------------------------------------- Simulation settings ---------------------------------------------------------------------- '''

choice = 0
print(" Do you want to record a track of an output statistics?\n")
print(" Finite Horizon ( Transient Statistics ) ............................. 0")
print(" Infinite Horizon ( Steady-State Statistics - Batch Means)  .......... 1")
choice = int( input("\n Please, type your choice here: ") )

b = 512
k = 0

if choice == 1:
  b = int( input("\n Type a size for the batch : ") )
  k = int( input("\n Type a number of batches : "))

f = open("MSMQ_sb/id.txt", "r")
old_id = f.readline()
new_id = 1 + int(old_id)
f.close()
f = open("MSMQ_sb/id.txt", "w")
f.write(str(new_id))
f.close

# Create an ensemble directory for this instance
dirName = "MSMQ_sb/ensemble"+ str(new_id)
try:
    # Create target Directory
    os.mkdir( dirName )
    print("Directory " , dirName ,  " Created ") 
except FileExistsError:
    print("Directory " , dirName ,  " already exists")

if len(sys.argv) == 3:
  STOP = float( sys.argv[2] )

''' ---------------------------------------------- Main Program ---------------------------------------------------------------------------- '''

plantSeeds(0)

r = 0

for i in range( 0, replicas ):
  
  r += 1
  
  try:
      # Create target Directory
      replName = dirName + "/repl" + str(i+1)
      os.mkdir( replName )
      print("Directory " , replName ,  " Created ") 
  except FileExistsError:
      print("Directory " , replName ,  " already exists")
  stat = output_dictionary[str(choice)]

  START = 0.0

  arrivalTemp = START

  t = time()

  events = [ event() for i in range( SERVERS + 1 ) ]                    # this list represents all event types, each specified by index

  number = 0
  index = 0
  area = 0

  number_queues = [ 0, 0, 0 ]                                           # number in the queues                      
  index_queues  = [ 0, 0, 0 ]                                           # used to count number of total processed jobs in the queues       
  area_queues   = [ 0.0, 0.0, 0.0 ]                                     # time integrated number in the queues
  tot_services_for_queue = [ 0.0, 0.0, 0.0 ]

  sum = [ accumSum() for i in range( 0, SERVERS + 1 ) ]                 # this list is used to represent each server status at the current time

  #initialization of multiqueue structure
  initialize_queue_structure()

  SIMULATION_SEED = getSeed()

  if choice == 0:
    LAMBDA = 4
    setLambda( LAMBDA )
  else:
    LAMBDA = 2
    setLambda( LAMBDA )

  t.current    = START

  # initialization of the first arrival event
  arrivalTemp += GetArrivalExpo()
  events[0].t   = arrivalTemp
  events[0].size = GetServicePareto()              
  events[0].x   = 1


  for s in range( 1, SERVERS + 1 ):
    events[s].t     = START                                             # this value is arbitrary because 
    events[s].x     = 0                                                 # all servers are initially idle  
    sum[s].service = 0.0
    sum[s].served  = 0

  period = 0
  disp = 0
  mod = 30
  old_index = 0
  batch_index = 0

  while ( ( events[0].x != 0 ) or ( number != 0 ) ):
    
    # ---These commands are used to produce the series of output statistics at runtime--------------------------------------------
    if ( index % b == 0 and choice == 1  and index != 0 ) :
      if not ( batch_index == k or old_index == index ) :  
        NextBatch()
        batch_index += 1
        old_index = index
    
    if ( choice == 0 and t.current >= 120 and period == 0):
      period += 1
      setLambda( 3   )
      LAMBDA = getLambda()
    if ( choice == 0 and t.current >= 300 and period == 1):
      period += 1
      setLambda( 4 )
      LAMBDA = getLambda()
    if ( choice == 0 and t.current >= 420 and period == 2):
      period += 1
      setLambda( 2  )
      LAMBDA = getLambda()
    if ( choice == 0 and t.current >= 720 and period == 3):
      period += 1
      setLambda( 5 )
      LAMBDA = getLambda()

    disp += 1
    if ( choice == 0 and disp % mod == 0 ):
      transientStats()
    #------------------------------------------------------------------------------------------------------------------------------

    e = NextEvent(events)                                               # next event index 

    t.next    = events[e].t                                             # next event time  
    
    area += ( t.next - t.current ) * number                             # update integral 

    for i in range( 0, QUEUES ):
      area_queues[i] += ( t.next - t.current ) * number_queues[i]       # update integral for each specific queue
    
    t.current = t.next                                                  # advance the clock

    if ( e == 0 ):    
      # process an ARRIVAL
      events[0].priority = enqueue( events[0] )                         # enqueue the current arrival into the respective queue defined by 'priority'
      number_queues[ events[0].priority ] += 1
      number += 1

      # schedule the next arrival event
      arrivalTemp += GetArrivalExpo()
      events[0].t   = arrivalTemp                                       # get the arrival time           
      events[0].size = GetServicePareto()                               # get the service time
      
      if ( events[0].t > STOP ):
        # end of observation time
        events[0].x      = 0
      #EndIf

      if ( number <= SERVERS ):
        # assign the highest priority event to the server which has been idle for the longest time
        service, prio  = serve()
        s = FindOne( events )
        # update the selected server's state
        sum[s].service += service
        sum[s].served += 1
        events[s].t      = t.current + service
        events[s].x      = 1
        events[s].priority  = prio
        # update the services sum for the respective queue
        number_queues[ events[s].priority  ] -= 1                       # decrease the number of jobs in the specific queue
        tot_services_for_queue[ prio ] += service
      #EndIf

    #EndIf

    else:            
      # process a COMPLETION                                                    
      s = e        
      number -= 1     
      index  += 1                                                       # increase the number of processed jobs in the node  
      index_queues[ events[s].priority  ]  += 1                         # increase the number of processed jobs in the specific queue 

      if ( number >= SERVERS ): 
        # schedule the next completion event
        service, prio   = serve()
        # update the selected server's state
        sum[s].service += service
        sum[s].served  += 1
        events[s].t     = t.current + service
        events[s].priority  = prio
        # update the services sum for the respective queue
        number_queues[ events[s].priority  ] -= 1                       # decrease the number of jobs in the specific queue
        tot_services_for_queue[ prio ] += service
      else:
        events[s].x      = 0
    
    #EndElse

  #EndWhile

  f.close()

  if ( index_queues[0] != 0 and index_queues[1] != 0 and index_queues[2] != 0 and index != 0):

    print("\n MULTISERVER MULTIQUEUE SIZE-BASED SCHEDULING - SEED : "+ str(SIMULATION_SEED) +" \n")
    print("\n for {0:1d} jobs the service node statistics are:\n".format(index))
    print("  avg interarrivals .. = {0:6.2f}".format((events[0].t-START) / index))
    print("  avg wait ........... = {0:6.2f}".format(area / index))
    d = 0.0
    for j in range( 0, QUEUES ):
      d += ( area_queues[j] / index_queues[j] ) * ( index_queues[j] / index )
    print("  avg delay .......... = {0:6.2f}".format( d ))
    print("  avg # in node ...... = {0:6.2f}".format(area / (t.current - START) ) )
      

    for j in range ( 0, QUEUES ):
      print("\n  QUEUE N° : " + str(j+1) + "  [avg job size = {0:6.2f}".format(tot_services_for_queue[j]/index_queues[j]) + " minutes | served clients = {0:6.2f}".format(index_queues[j]/(index_queues[0]+index_queues[1]+index_queues[2])) + " %]")
      print("  avg wait ........... = {0:6.2f}".format(area_queues[j] / index_queues[j] + tot_services_for_queue[j] / index_queues[j]))
      print("  avg delay .......... = {0:6.2f}".format(area_queues[j] / index_queues[j]))
      print("  avg # in queue ..... = {0:6.2f}".format(area_queues[j] / (t.current-START)))

    print("\n  MEAN CONDITIONAL SLOWDOWN " )
    print("  x = 1.24 minutes ... = {0:6.2f}".format( 1 + (area_queues[0] / index_queues[0]) / 1.24 ))
    print("  x = 2.65 minutes ... = {0:6.2f}".format( 1 + (area_queues[1] / index_queues[1]) / 2.65 ))
    print("  x = 4.42 minutes ... = {0:6.2f}".format( 1 + (area_queues[1] / index_queues[1]) / 4.42 ))
    print("  x = 8.26 minutes ... = {0:6.2f}".format( 1 + (area_queues[2] / index_queues[2]) / 8.26 ))

    print("\n The server statistics are:\n")
    print("    server     utilization     avg service        share\n")

    try:
      for s in range(1,SERVERS+1):
        print("{0:8d} {1:14.3f} {2:15.2f} {3:15.3f}".format(s, sum[s].service / (t.current-START), sum[s].service / sum[s].served,float(sum[s].served) / index))
    except:
      print("")
    
  # Record simulation results on a header JSON file

  if (choice == 0 ):

    transientStatistics["seed"] = SIMULATION_SEED
    transientStatistics["interarrivals"] = LAMBDA
    transientStatistics["observation_period"] = STOP
    transientStatistics["servers"] = SERVERS
    transientStatistics["batch_size"] = 0

    with open( replName + "/transientStatistics"+ str(r) +".json" , 'w') as json_file:
      json.dump( transientStatistics, json_file, indent = 4  )
    json_file.close()

    finiteHorizon( replName, transientStatistics, 0)

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
      "avg_utilization7": [],
      "avg_utilization8": [],
      "avg_utilization9": [],
      "global": {"avg_wait": [], "avg_delay": [], "avg_number": []},
      "q1": {"avg_wait": [], "avg_delay": [], "avg_number": []},
      "q2": {"avg_wait": [], "avg_delay": [], "avg_number": []},
      "q3": {"avg_wait": [], "avg_delay": [], "avg_number": []},
      "mean_conditional_slowdown": {"(1.24)": [], "(2.65)": [], "(4.42)": [], "(8.26)": []}
    }

  else:

    batchmean["seed"] = SIMULATION_SEED
    batchmean["interarrivals"] = LAMBDA
    batchmean["observation_period"] = STOP
    batchmean["servers"] = SERVERS   
    batchmean["k"] = batch_index
    batchmean["batch_size"] = b

    with open( replName + "/batchMeans"+ str(batch_index) +".json" , 'w') as json_file:
      json.dump( batchmean, json_file, indent = 4 )
    json_file.close()

    batchMeans( replName, batchmean, 0 )

    batchmean = {
      "seed" : 0,
      "arrival_stream" : 0,
      "service_stream" : 1,
      "observation_period" : 0,
      "interarrivals" : 0.0,
      "batch_size" : 0,
      "k":0,
      "servers" : 0,
      "acquisition_time" : [],
      "avg_utilization1" : [],
      "avg_utilization2" : [],
      "avg_utilization3" : [],
      "avg_utilization4" : [],
      "avg_utilization5" : [],
      "avg_utilization6" : [],
      "avg_utilization7" : [],
      "avg_utilization8" : [],
      "avg_utilization9" : [],
      "global" : { "avg_wait": [] , "avg_delay" : [], "avg_number" : []  },
      "q1" : { "avg_wait": [] , "avg_delay": [] , "avg_number" : [] },
      "q2" : { "avg_wait": [] , "avg_delay": [] , "avg_number" : []  },
      "q3" : { "avg_wait": [] , "avg_delay": [] , "avg_number" : []  },
      "mean_conditional_slowdown" : { "(1.24)": [] , "(2.65)": [] , "(4.42)": [] , "(8.26)": []  }
    }

if choice == 1:
  steadyStatePlotter( dirName, 0 )
else:
  transientPlotter( dirName, 0 )