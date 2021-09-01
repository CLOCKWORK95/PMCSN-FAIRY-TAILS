from rngs import selectStream
from probabilityDistributions import Exponential


def GetArrivalExpo():
    # ---------------------------------------------
    # * generate the next arrival time from an Exponential distribution.
    # * --------------------------------------------

    selectStream(0)
    return Exponential()
