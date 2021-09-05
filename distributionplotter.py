import numpy as np
import matplotlib.pyplot as plt


def paretoplotterPDF( alpha, k, p ):

    x = np.arange( k, p, 0.1 )
    y = [ ( ( alpha * pow( k, alpha ) )*( pow( xvalue, -alpha - 1.0 ) ) ) / ( 1.0 - pow( k/p, alpha ) ) for xvalue in x ]

    plt.plot( x, y )
    xcoords = [1.5, 4.5]
    colore = "g"
    for xc in xcoords:
        if xc == 1.5 : colore = 'r'
        if xc == 4.5 : colore = 'g'
        plt.axvline(x=xc, color = colore, linestyle='dashed')

    plt.legend(["PDF", "priority 1 upperbound : 1.5 minutes", "priority 2 upperbound : 4.5 minutes"])
    plt.title("Bounded Pareto Distribution \n alpha : " + str(alpha) + ", k : " + str(k) + ", p : " + str(p))
    plt.xlabel("Service time (minutes)")
    plt.show()

def paretoplotterCDF( alpha, k, p ):

    x = np.arange( k,p, 0.1 )
    y = [ ( 1.0 - (pow(k,alpha)*pow(xvalue,-alpha)) ) / ( 1.0 - pow(k/p,alpha) ) for xvalue in x ]

    plt.plot( x, y )
    xcoords = [1.5, 4.5]
    colore = "g"
    for xc in xcoords:
        if xc == 1.5 : colore = 'r'
        if xc == 4.5 : colore = 'g'
        plt.axvline(x=xc, color = colore, linestyle='dashed')

    plt.legend(["CDF", "priority 1 upperbound : 1.5 minutes", "priority 2 upperbound : 4.5 minutes"])
    plt.title("Bounded Pareto Cumulative Distribution Function \n alpha : " + str(alpha) + ", k : " + str(k) + ", p : " + str(p))
    plt.xlabel("Service time (minutes)")
    plt.show()

paretoplotterPDF( 0.2703, 1.0, 15.0 )