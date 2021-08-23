from rngs import random
from math import log

''' ----------------- Distributions Parameters -------------------------------------------------------------- '''

alpha = 0.2703                                              # Pareto parameter
p = 15                                                      # Pareto parameter which represents the maximum value 
k = 1                                                       # Pareto parameter which represents the minimum value 

LAMBDA =  2                                                 # Exponential parameter : average arrival rate [ jobs/minute ]

A = 2.0                                                     # Uniform parameter : minimum value
B = 10.0                                                    # Uniform parameter : maximum value

def getLambda():
  return LAMBDA

def getParetoParams():
  return alpha, p, k

def getUniformParams():
  return A, B

def setLambda( value ):
  global LAMBDA
  LAMBDA = value

''' ----------------- Distributions Functions -------------------------------------------------------------- '''

def BoundedPareto():
# ---------------------------------------------------
# * generate a Bounded Pareto random variate, use m > 0.0 
# * ---------------------------------------------------
  global k, p, alpha  
  N = 1 - pow( k/p, alpha )
  return k / pow( ( 1.0 - random()  * N ), 1/alpha )


def Exponential():
# ---------------------------------------------------
# * generate an Exponential random variate, use m > 0.0 
# * ---------------------------------------------------
  return (-LAMBDA * log(1.0 - random()))


def Uniform(): 
# --------------------------------------------
# * generate a Uniform random variate, use a < b 
# * --------------------------------------------
  global A, B  
  return ( A + ( B - A ) * random() )  