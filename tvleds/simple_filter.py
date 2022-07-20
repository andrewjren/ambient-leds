import numpy as np

class SimpleFilter():

    def __init__(self, gains, num_channels):

        # FIR filter gains
        self.gains = gains
        self.num_gains = len(gains)

        # FIR filter channels
        self.num_channels = num_channels

        # Channels - indexed by channel, gain
        self.values = np.zeros((self.num_channels,self.num_gains))

        # filter index to keep track of which index is the latest
        self.filter_idx = 0 

    # add new value into filter, compute filter output, return values for each channel
    # expects new_values as a vertical numpy array
    def apply(self, new_values):

        # add new column to values
        self.values = np.insert(self.values, 0, new_values, axis=1)

        # delete last (oldest) column
        self.values = np.delete(self.values, self.num_gains, axis=1)

        # apply filter gains to get filter output
        filter_output = np.matmul(self.values, self.gains)

        return filter_output
