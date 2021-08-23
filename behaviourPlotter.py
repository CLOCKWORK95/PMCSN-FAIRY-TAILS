import numpy as np
import matplotlib.pyplot as plt
import sys, os, json

MEANVALUE = 0.0
TITLE = ""
SEED = 0
JOBS = 0

path = sys.argv[1]

directories = os.listdir( path )
directories = directories[ 1 : len(directories)]

for d in directories:

    files = os.listdir( path + "/" + d )

    for f in files:

        if f.endswith(".png"):
            continue

        if f.endswith(".json"):
            with open( path + "/" + d + "/" + f ) as jsonHeader:
                data = json.load( jsonHeader )
            TITLE = path + " - " + data["target"]
            SEED = data["initial_seed"]
            JOBS = data["jobs"]
            MEANVALUE = data["avg_values"][ data["target"] ]

    for f in files:

        if f.endswith(".dat"):
            with open( path + "/" + d + "/" + f ) as series:
                values = [ line.rstrip() for line in series ]
            values = [ float(v) for v in values ]
            lenx = len( values )
            y2 = [ MEANVALUE for y in values ]

            Y2 = np.array( y2 )
            Y1 = np.array( values )
            X = np.arange( 0, lenx, 1 )


            # red dashes, blue squares and green triangles
            plt.plot(  X, Y1, 'bs', X, Y2, 'rs', markersize = 1 )
            plt.title( TITLE + "\nInitial Seed : " + data["initial_seed"] + " - Theoretical Mean : " + "{0:6.2f}".format(MEANVALUE) )
            plt.legend( [ data["target"] , "real mean value" ] )
            plt.savefig( path + "/" + d + "/" + f[:len(f)-4] + ".png" )
            plt.close()




    











