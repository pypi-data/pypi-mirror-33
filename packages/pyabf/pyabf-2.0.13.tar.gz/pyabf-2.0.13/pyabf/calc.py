"""
Code here performs calculations on data from ABF objects.
"""
import numpy as np

def sweepNumbersByTime(abf, timeSec1, timeSec2):
    """
    Returns a list of sweeps containing data between the two times.
    """
    raise NotImplementedError
    return [1, 2, 3]


def averageSweep(abf, sweepNumbers=None, baselineTimeSec1=False, baselineTimeSec2=False, stdErr=True):
    """
    Returns the average of the given sweeps. 
    This returns a whole sweep, not just a single number.
    """
    raise NotImplementedError
    return abf.dataY

def averageValue(abf, timeSec1, timeSec2, sweepNumbers=None, channel=0, stdErr=True):
    """
    Return [AVs, ERs] between two time points for the given sweeps.
    """
    if sweepNumbers is None:
        sweepNumbers = abf.sweepList
    sweepNumbers = list(sweepNumbers)
    assert len(sweepNumbers) > 0

    avs = np.full(len(sweepNumbers), np.nan)
    ers = np.full(len(sweepNumbers), np.nan)

    for sweepNumber in sweepNumbers:
        abf.setSweep(sweepNumber=sweepNumber, channel=channel)
        avs[sweepNumber] = abf.sweepAverage(timeSec1, timeSec2)
        ers[sweepNumber] = abf.sweepError(timeSec1, timeSec2, stdErr)
    if stdErr:
        ers = ers / np.sqrt(len(sweepNumbers))

    return [avs, ers]