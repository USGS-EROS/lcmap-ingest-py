import numpy as np
import numpy.linalg as al
import time
import matplotlib
import matplotlib.pyplot as plt
import datetime
import time

def D(year, day):
    return datetime.datetime(year, 1, 1) + datetime.timedelta(int(day) - 1)

def ccdc(timeseries):
    """
    """
    # solve coefficients for ccdc function
    # a0 + a1*cos(x) + b1*sin(x) + c1*x
    start = time.perf_counter()
    V = [ [1, np.cos((2*np.pi*x)/365), np.sin((2*np.pi*x)/365), x] for x, _ in timeseries ]
    t = [ t for _, t in timeseries ]
    xs, _, _, _ = al.lstsq(V,t)
    a0 = np.mean([val for _, val in timeseries])
    _, a1, b1, c1 = xs
    stop = time.perf_counter()
    f = lambda x: a0 + a1*np.cos((2*np.pi*x)/365) + b1*np.sin((2*np.pi*x)/365) + c1*x;
    return f, (a0,a1,b1,c1)

def simple(timeseries, samples=15):
    """calculate simple CCDC model coefficients
    """
    # Todo:
    # start with timeseries[-15,-3]
    # step "left" and try again if things don't look right...
    # 1. abs(c1) > 1.0 ...
    # 2. something else?
    #
    V = [ [1, np.cos((2*np.pi*x)/365), np.sin((2*np.pi*x)/365), x] for x, _ in timeseries ]
    t = [ t for _, t in timeseries ]
    xs, _, _, _ = al.lstsq(V,t)
    a0 = np.mean([val for _, val in timeseries])
    _, a1, b1, c1 = xs
    return [ a0, a1, b1, c1 ]

def fsimple(coefficients, x):
    a0, a1, b1, c1 = coefficients
    return a0 + a1*np.cos((2*np.pi*x)/365) + b1*np.sin((2*np.pi*x)/365) + c1*x;

