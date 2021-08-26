import numpy as np
import matplotlib.pyplot as plt
import os, sys, json
from math import sqrt, floor
from rvms import idfStudent


batchMeanTemplate = {
  "interarrival" : 0,
  "servers" : 0,
  "seed" : 0,
  "GLOBAL AVG WAIT" : {"mean":0.0,"half_confidence_interval":0.0,"stdev":0.0,"confidence":95},
  "GLOBAL AVG DELAY" : {"mean":0.0,"half_confidence_interval":0.0,"stdev":0.0,"confidence":95},
  "GLOBAL AVG NUMBER":{"mean":0.0,"half_confidence_interval":0.0,"stdev":0.0,"confidence":95},
  "QUEUE1 AVG WAIT" : {"mean":0.0,"half_confidence_interval":0.0,"stdev":0.0,"confidence":95},
  "QUEUE1 AVG DELAY" : {"mean":0.0,"half_confidence_interval":0.0,"stdev":0.0,"confidence":95},
  "QUEUE1 AVG NUMBER" : {"mean":0.0,"half_confidence_interval":0.0,"stdev":0.0,"confidence":95},
  "QUEUE2 AVG WAIT" : {"mean":0.0,"half_confidence_interval":0.0,"stdev":0.0,"confidence":95},
  "QUEUE2 AVG DELAY" : {"mean":0.0,"half_confidence_interval":0.0,"stdev":0.0,"confidence":95},
  "QUEUE2 AVG NUMBER" : {"mean":0.0,"half_confidence_interval":0.0,"stdev":0.0,"confidence":95},
  "QUEUE3 AVG WAIT" : {"mean":0.0,"half_confidence_interval":0.0,"stdev":0.0,"confidence":95},
  "QUEUE3 AVG DELAY" : {"mean":0.0,"half_confidence_interval":0.0,"stdev":0.0,"confidence":95},
  "QUEUE3 AVG NUMBER" : {"mean":0.0,"half_confidence_interval":0.0,"stdev":0.0,"confidence":95},
  "UTILIZATION1" : {"mean":0.0,"half_confidence_interval":0.0,"stdev":0.0,"confidence":95},
  "UTILIZATION2" : {"mean":0.0,"half_confidence_interval":0.0,"stdev":0.0,"confidence":95},
  "UTILIZATION3" : {"mean":0.0,"half_confidence_interval":0.0,"stdev":0.0,"confidence":95},
  "UTILIZATION4" : {"mean":0.0,"half_confidence_interval":0.0,"stdev":0.0,"confidence":95},
  "UTILIZATION5" : {"mean":0.0,"half_confidence_interval":0.0,"stdev":0.0,"confidence":95},
  "UTILIZATION6" : {"mean":0.0,"half_confidence_interval":0.0,"stdev":0.0,"confidence":95}
}

transientTemplate = {
  "interarrival" : 0,
  "servers" : 0,
  "seed" : 0,
  "GLOBAL AVG WAIT" : {"mean":0.0,"half_confidence_interval":0.0,"stdev":0.0,"confidence":95},
  "GLOBAL AVG DELAY" : {"mean":0.0,"half_confidence_interval":0.0,"stdev":0.0,"confidence":95},
  "GLOBAL AVG NUMBER":{"mean":0.0,"half_confidence_interval":0.0,"stdev":0.0,"confidence":95},
  "QUEUE1 AVG WAIT" : {"mean":0.0,"half_confidence_interval":0.0,"stdev":0.0,"confidence":95},
  "QUEUE1 AVG DELAY" : {"mean":0.0,"half_confidence_interval":0.0,"stdev":0.0,"confidence":95},
  "QUEUE1 AVG NUMBER" : {"mean":0.0,"half_confidence_interval":0.0,"stdev":0.0,"confidence":95},
  "QUEUE2 AVG WAIT" : {"mean":0.0,"half_confidence_interval":0.0,"stdev":0.0,"confidence":95},
  "QUEUE2 AVG DELAY" : {"mean":0.0,"half_confidence_interval":0.0,"stdev":0.0,"confidence":95},
  "QUEUE2 AVG NUMBER" : {"mean":0.0,"half_confidence_interval":0.0,"stdev":0.0,"confidence":95},
  "QUEUE3 AVG WAIT" : {"mean":0.0,"half_confidence_interval":0.0,"stdev":0.0,"confidence":95},
  "QUEUE3 AVG DELAY" : {"mean":0.0,"half_confidence_interval":0.0,"stdev":0.0,"confidence":95},
  "QUEUE3 AVG NUMBER" : {"mean":0.0,"half_confidence_interval":0.0,"stdev":0.0,"confidence":95},
  "UTILIZATION1" : {"mean":0.0,"half_confidence_interval":0.0,"stdev":0.0,"confidence":95},
  "UTILIZATION2" : {"mean":0.0,"half_confidence_interval":0.0,"stdev":0.0,"confidence":95},
  "UTILIZATION3" : {"mean":0.0,"half_confidence_interval":0.0,"stdev":0.0,"confidence":95},
  "UTILIZATION4" : {"mean":0.0,"half_confidence_interval":0.0,"stdev":0.0,"confidence":95},
  "UTILIZATION5" : {"mean":0.0,"half_confidence_interval":0.0,"stdev":0.0,"confidence":95},
  "UTILIZATION6" : {"mean":0.0,"half_confidence_interval":0.0,"stdev":0.0,"confidence":95}
}


def analyticalResults( interarrivals ):

  LAMBDA = 1/interarrivals

  utilization =  ( LAMBDA / 3 ) * 4.42 

  delay = ( ( LAMBDA / 6 ) * 32.2791123 ) / ( 1 - utilization )

  wait = delay + 4.42

  return delay, wait, utilization


def estimate( valuesArray ):

  if len(valuesArray) == 0:
    mean = 0.0
    stdev = 0.0
    w = 0.0
    return mean, stdev, w

  LOC = 0.95                                                            # level of confidence, use 0.95 for 95% confidence                                                     
  n    = 0                                                              # counts data points 
  sum  = 0.0
  mean = 0.0
 
  data = valuesArray[n]

  for i in range( 1, len(valuesArray) ):                                # use Welford's one-pass method                                   
    n += 1                                                              # to calculate the sample mean   
    diff  = float(data) - mean                                          # and standard deviation        
    sum  += diff * diff * (n - 1.0) / n
    mean += diff / n
    data = valuesArray[i]

  stdev  = sqrt(sum / n)

  if (n > 1): 
    u = 1.0 - 0.5 * (1.0 - LOC)                                         # interval parameter  
    t = idfStudent(n - 1, u)                                            # critical value of t 
    w = t * stdev / sqrt(n - 1)                                         # interval half width 

    return mean, stdev, w

  else:
    print("ERROR - insufficient data\n")


def batchMeans( path, batchDictionary, model ):
    # -----------------------------------------------------------
    # This technique is used to compute Steady-State statistics 
    # ( "infinite horizon" point and interval estimations ).
    # -----------------------------------------------------------
    global batchMeanTemplate

    SERVERS = int ( batchDictionary["servers"] )

    B = batchDictionary["batch_size"]

    batchMeanTemplate["interarrival"] = batchDictionary["interarrivals"]
    batchMeanTemplate["seed"] = batchDictionary["seed"]
    batchMeanTemplate["servers"] = batchDictionary["servers"]

    avg_wait_global = batchDictionary["global"]["avg_wait"][1:]
    avg_delay_global = batchDictionary["global"]["avg_delay"][1:]
    avg_number_global = batchDictionary["global"]["avg_number"][1:]

    avg_utilizations = []

    for j in range( SERVERS ):
      avg_utilizations.append(  batchDictionary["avg_utilization"+str(j+1)][1:] )

    if model == 0:
      avg_wait_queues = [ batchDictionary["q1"]["avg_wait"][1:], batchDictionary["q2"]["avg_wait"][1:], batchDictionary["q3"]["avg_wait"][1:] ]
      avg_delay_queues = [ batchDictionary["q1"]["avg_delay"][1:], batchDictionary["q2"]["avg_delay"][1:], batchDictionary["q3"]["avg_delay"][1:] ]
      avg_number_queues = [ batchDictionary["q1"]["avg_number"][1:], batchDictionary["q2"]["avg_number"][1:], batchDictionary["q3"]["avg_number"][1:]]

    if model == 1:

      avg_wait_queues = []
      avg_delay_queues = []
      avg_number_queues = []

      if SERVERS >= 1 : 
        avg_wait_queues.append( batchDictionary["c1"]["avg_wait"][1:] )
        avg_delay_queues.append( batchDictionary["c1"]["avg_delay"][1:] )
        avg_number_queues.append( batchDictionary["c1"]["avg_number"][1:] )
      
      if SERVERS >= 2 : 
        avg_wait_queues.append( batchDictionary["c2"]["avg_wait"][1:] )
        avg_delay_queues.append( batchDictionary["c2"]["avg_delay"][1:] )
        avg_number_queues.append( batchDictionary["c2"]["avg_number"][1:] )

      if SERVERS >= 3 : 
        avg_wait_queues.append( batchDictionary["c3"]["avg_wait"][1:] )
        avg_delay_queues.append( batchDictionary["c3"]["avg_delay"][1:] )
        avg_number_queues.append( batchDictionary["c3"]["avg_number"][1:] )

      

    with open( path + "/steadystate.json" , "a") as results:

        res = batchMeanTemplate

        res["interarrival"] = batchDictionary["interarrivals"]
        res["seed"] = batchDictionary["seed"]
        res["servers"] = batchDictionary["servers"]

        mean, stdev, half_interval = estimate( avg_wait_global )
        res["GLOBAL AVG WAIT"]["mean"] = mean
        res["GLOBAL AVG WAIT"]["stdev"] = stdev
        res["GLOBAL AVG WAIT"]["half_confidence_interval"] = half_interval

        mean, stdev, half_interval = estimate( avg_delay_global )
        res["GLOBAL AVG DELAY"]["mean"] = mean
        res["GLOBAL AVG DELAY"]["stdev"] = stdev
        res["GLOBAL AVG DELAY"]["half_confidence_interval"] = half_interval

        mean, stdev, half_interval = estimate( avg_number_global )
        res["GLOBAL AVG NUMBER"]["mean"] = mean
        res["GLOBAL AVG NUMBER"]["stdev"] = stdev
        res["GLOBAL AVG NUMBER"]["half_confidence_interval"] = half_interval

        
        for j in range( 1, 4 ):
          mean, stdev, half_interval = estimate( avg_wait_queues[j-1] )
          res["QUEUE" + str(j) + " AVG WAIT"]["mean"] = mean
          res["QUEUE" + str(j) + " AVG WAIT"]["stdev"] = stdev
          res["QUEUE" + str(j) + " AVG WAIT"]["half_confidence_interval"] = half_interval

          mean, stdev, half_interval = estimate( avg_delay_queues[j-1] )
          res["QUEUE" + str(j) + " AVG DELAY"]["mean"] = mean
          res["QUEUE" + str(j) + " AVG DELAY"]["stdev"] = stdev
          res["QUEUE" + str(j) + " AVG DELAY"]["half_confidence_interval"] = half_interval
          
          mean, stdev, half_interval = estimate( avg_number_queues[j-1] )
          res["QUEUE" + str(j) + " AVG NUMBER"]["mean"] = mean
          res["QUEUE" + str(j) + " AVG NUMBER"]["stdev"] = stdev
          res["QUEUE" + str(j) + " AVG NUMBER"]["half_confidence_interval"] = half_interval


        for j in range( 1, SERVERS + 1 ):

          mean, stdev, half_interval = estimate( avg_utilizations[j-1] )
          res["UTILIZATION"+ str(j) ]["mean"] = mean
          res["UTILIZATION"+ str(j) ]["stdev"] = stdev
          res["UTILIZATION"+ str(j) ]["half_confidence_interval"] = half_interval
        
        json.dump( res, results, indent = 4  )

    results.close()


def finiteHorizon(path, finiteHorizonDictionary, model):
    # -----------------------------------------------------------
    # This technique is used to compute Steady-State statistics
    # ( "infinite horizon" point and interval estimations ).
    # -----------------------------------------------------------
    global transientTemplate

    SERVERS = int(finiteHorizonDictionary["servers"])

    transientTemplate["interarrival"] = finiteHorizonDictionary["interarrivals"]
    transientTemplate["seed"] = finiteHorizonDictionary["seed"]
    transientTemplate["servers"] = finiteHorizonDictionary["servers"]

    avg_wait_global = finiteHorizonDictionary["global"]["avg_wait"][1:]
    avg_delay_global = finiteHorizonDictionary["global"]["avg_delay"][1:]
    avg_number_global = finiteHorizonDictionary["global"]["avg_number"][1:]

    avg_utilizations = []

    for j in range(SERVERS):
        avg_utilizations.append(finiteHorizonDictionary["avg_utilization" + str(j + 1)][1:])

    if model == 0:
        avg_wait_queues = [finiteHorizonDictionary["c1"]["avg_wait"][1:], finiteHorizonDictionary["c2"]["avg_wait"][1:],
                           finiteHorizonDictionary["c3"]["avg_wait"][1:]]
        avg_delay_queues = [finiteHorizonDictionary["c1"]["avg_delay"][1:], finiteHorizonDictionary["c2"]["avg_delay"][1:],
                            finiteHorizonDictionary["c3"]["avg_delay"][1:]]
        avg_number_queues = [finiteHorizonDictionary["c1"]["avg_number"][1:], finiteHorizonDictionary["c2"]["avg_number"][1:],
                             finiteHorizonDictionary["c3"]["avg_number"][1:]]

    with open(path + "/finiteHorizon.json", "a") as results:

        res = batchMeanTemplate

        res["interarrival"] = finiteHorizonDictionary["interarrivals"]
        res["seed"] = finiteHorizonDictionary["seed"]
        res["servers"] = finiteHorizonDictionary["servers"]

        mean, stdev, half_interval = estimate(avg_wait_global)
        res["GLOBAL AVG WAIT"]["mean"] = mean
        res["GLOBAL AVG WAIT"]["stdev"] = stdev
        res["GLOBAL AVG WAIT"]["half_confidence_interval"] = half_interval

        mean, stdev, half_interval = estimate(avg_delay_global)
        res["GLOBAL AVG DELAY"]["mean"] = mean
        res["GLOBAL AVG DELAY"]["stdev"] = stdev
        res["GLOBAL AVG DELAY"]["half_confidence_interval"] = half_interval

        mean, stdev, half_interval = estimate(avg_number_global)
        res["GLOBAL AVG NUMBER"]["mean"] = mean
        res["GLOBAL AVG NUMBER"]["stdev"] = stdev
        res["GLOBAL AVG NUMBER"]["half_confidence_interval"] = half_interval

        if model == 0:
            for j in range(1, 4):
                mean, stdev, half_interval = estimate(avg_wait_queues[j - 1])
                res["QUEUE" + str(j) + " AVG WAIT"]["mean"] = mean
                res["QUEUE" + str(j) + " AVG WAIT"]["stdev"] = stdev
                res["QUEUE" + str(j) + " AVG WAIT"]["half_confidence_interval"] = half_interval

                mean, stdev, half_interval = estimate(avg_delay_queues[j - 1])
                res["QUEUE" + str(j) + " AVG DELAY"]["mean"] = mean
                res["QUEUE" + str(j) + " AVG DELAY"]["stdev"] = stdev
                res["QUEUE" + str(j) + " AVG DELAY"]["half_confidence_interval"] = half_interval

                mean, stdev, half_interval = estimate(avg_number_queues[j - 1])
                res["QUEUE" + str(j) + " AVG NUMBER"]["mean"] = mean
                res["QUEUE" + str(j) + " AVG NUMBER"]["stdev"] = stdev
                res["QUEUE" + str(j) + " AVG NUMBER"]["half_confidence_interval"] = half_interval

        for j in range(1, SERVERS + 1):
            mean, stdev, half_interval = estimate(avg_utilizations[j - 1])
            res["UTILIZATION" + str(j)]["mean"] = mean
            res["UTILIZATION" + str(j)]["stdev"] = stdev
            res["UTILIZATION" + str(j)]["half_confidence_interval"] = half_interval

        json.dump(res, results, indent=4)

    results.close()


def steadyStatePlotter( path, model ):

  global batchMeanTemplate

  delay, wait, utilization = analyticalResults( batchMeanTemplate["interarrival"] )

  directories = os.listdir( path )

  for t in batchMeanTemplate.keys():

    if t in ["interarrival", "servers", "seed"]:
      continue

    headerbuilder = 0

    if model == 0:
      title = "Size Based MSMQ - " + t 
    elif model == 1:
      title = "SSQ Abstract Network - " + t 

    seeds = []

    values = []

    errors = []

    k = 0

    b = 0

    interarrival = 0

    servers = 0

    for d in directories:

      files = os.listdir( path + "/" + d )

      for f in files:

        if f.startswith("batchMeans"):

          filepath = path + "/" + d + "/" + f

          with open( filepath ) as jsonHeader:
            data = json.load( jsonHeader )
            seeds.append( data["seed"] )
            if headerbuilder == 0:
              interarrival = data["interarrivals"]
              servers = data["servers"]
              b = data["batch_size"]
              k = data["k"]
              title += "\n" + str(servers) + " Servers -  Avg Interarrival time: " + str(interarrival) + "min"
              title += "\n Infinite Horizon Statistics ( Batch Means : b : " + str(b) + "  k : " + str(k) + " )"
              headerbuilder = 1

        elif f.startswith("steadystate"):
          
          filepath = path + "/" + d + "/" + f

          with open( filepath ) as jsonfile:
            data = json.load( jsonfile )
            values.append( data[t]["mean"] )
            errors.append( data[t]["half_confidence_interval"] )
    
    

    x = [ i for i in range( len(values) ) ]
    plt.errorbar( x, values, errors, fmt = '.' )

    realvalue = ""

    '''
     if t.startswith("GLOBAL AVG WAIT"):

      l = [ wait for i in range( len(values) ) ]
      realvalue = "{0:6.2f}".format( wait )
      truevalue = np.array( l )
      plt.plot( truevalue )

    elif t.startswith("GLOBAL AVG DELAY"):

      l = [ delay for i in range( len(values) ) ]
      realvalue = "{0:6.2f}".format( delay )
      truevalue = np.array( l )
      plt.plot( truevalue )

    elif t.startswith("UTILIZATION"):

      l = [ utilization for i in range( len(values) ) ]
      realvalue ="{0:6.2f}".format( utilization )
      truevalue = np.array( l )
      plt.plot( truevalue ) '''

    plt.title( title, fontsize = 10 )
    
    #plt.legend( [ "Analytical Result: " + realvalue, "Initial Seed: "+ str(seeds[0])] )

    if model == 1:
      # CLASSIC MODEL
      if t.startswith("UTILIZATION"):
        plt.ylim(0,1)
      #else:
        #plt.ylim(0, 20)
    else:
      # SIZE BASED MODEL
      if t.startswith("UTILIZATION"):
        maxvalue = np.max(values) + np.max(errors)
        minvalue = np.min(values) - np.max(errors)
        plt.ylim(minvalue-0.1,maxvalue+0.1)
      #else:
        #plt.ylim(0, 14)



    plt.savefig( path + "/" + t + ".png" )


    plt.close()


def transientPlotter(path, model):
    global transientTemplate

    delay, wait, utilization = analyticalResults(transientTemplate["interarrival"])

    directories = os.listdir(path)

    for t in transientTemplate.keys():

        if t in ["interarrival", "servers", "seed"]:
            continue

        headerbuilder = 0

        if model == 0:
            title = "Size Based MSMQ - " + t
        elif model == 1:
            title = "SSQ Abstract Network - " + t

        seeds = []

        values = []

        errors = []

        interarrival = 0

        servers = 0

        for d in directories:

            files = os.listdir(path + "/" + d)

            for f in files:

                if f.startswith("transientStatistics"):

                    filepath = path + "/" + d + "/" + f

                    with open(filepath) as jsonHeader:
                        data = json.load(jsonHeader)
                        seeds.append(data["seed"])
                        if headerbuilder == 0:
                            interarrival = data["interarrivals"]
                            servers = data["servers"]
                            b = data["batch_size"]
                            k = data["k"]
                            title += "\n" + str(servers) + " Servers -  Avg Interarrival time: " + str(
                                interarrival) + "min"
                            title += "\n Finite Horizon Statistics ( Replication Method )"
                            headerbuilder = 1

                elif f.startswith("finiteHorizon"):

                    filepath = path + "/" + d + "/" + f

                    with open(filepath) as jsonfile:
                        data = json.load(jsonfile)
                        values.append(data[t]["mean"])
                        errors.append(data[t]["half_confidence_interval"])

        x = [i for i in range(len(values))]
        plt.errorbar(x, values, errors, fmt='.')

        if t.startswith("GLOBAL AVG WAIT"):

            l = [wait for i in range(len(values))]
            truevalue = np.array(l)
            plt.plot(truevalue)

        elif t.startswith("GLOBAL AVG DELAY"):

            l = [delay for i in range(len(values))]
            truevalue = np.array(l)
            plt.plot(truevalue)

        elif t.startswith("UTILIZATION"):

            l = [utilization for i in range(len(values))]
            truevalue = np.array(l)
            plt.plot(truevalue)

        plt.title(title)
        plt.savefig(path + "/" + t + ".png")
        plt.legend(seeds)
        plt.close()



