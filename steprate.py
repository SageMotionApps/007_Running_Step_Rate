"""
Author: Junkai
Data: 2020.11.24

Description: Use the autocorrelation function(ACF) to estimate the step rate based on the
IMU sensor data. It calculates the offset of data with the maxim correlation to get the
most likely period of data.

This algorithm is inspired by:
[1]Pan, Meng-Shiuan, and Hsueh-Wei Lin. "A step counting algorithm for smartphone users:
   Design and implementation." IEEE Sensors Journal 15.4 (2014): 2296-2305.

@output datarate: the data rate of IMU data
@input max_steprate: the max threshold of step rate to calculate
@input min_steprate: the min threshold of step rate to calculate
"""
import numpy as np

class StepRate:
    def __init__(self, datarate = 100,
                       max_steprate = 240,
                       min_steprate = 120):
        self.DATARATE = datarate
        self.MAX_OFFSET = int(datarate/min_steprate*60/2)
        self.MIN_OFFSET = int(datarate/max_steprate*60/2)
        self.steprate = 0

    # Calculate the step rate
    def cal_steprate(self, data):
        data = np.array(data)
        data = data-data.mean()
        datalen = len(data)
        autocorrelation = np.correlate(data, data, mode="full")/(datalen-np.arange(-datalen+1, datalen, 1))
        autocorrelation = autocorrelation[len(data)-1:]/(np.square(np.std(data)))
        maxoffset = np.where(autocorrelation==np.amax(autocorrelation[self.MIN_OFFSET:self.MAX_OFFSET]))[0]
        return self.DATARATE/float(maxoffset)*60*2
