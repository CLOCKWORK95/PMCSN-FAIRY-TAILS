from rngs import selectStream
from probabilityDistributions import BoundedPareto, Uniform


def GetServicePareto():
    # --------------------------------------------
    # * generate the next service time from a Bounded Pareto distribution.
    # * --------------------------------------------

    selectStream(1)
    return BoundedPareto()


''' --------------------------------------------------------- '''


def GetServiceUniform():
    # --------------------------------------------
    # * generate the next service time from a Uniform distribution.
    # * --------------------------------------------

    selectStream(1)
    return Uniform()
