import mne
import numpy as np
import scipy.signal as signal

from src.utils.utils_io import get_edf_info, read_eeg_data


class HFO_App(object):
    def __init__(self):
        self.version = "1.0.0"
        self.n_jobs = 4
        ## eeg related
        self.filename = None
        self.eeg_data = None
        self.raw = None
        self.channel_names = None
        self.sample_freq = 0 # Hz
        self.edf_param = None


    def load_edf(self, file_path):
        print("Loading edf: " + file_path)
        self.filename = file_path
        self.raw = mne.io.read_raw_edf(file_path, verbose = 0)
        self.edf_param = get_edf_info(self.raw)
        self.sample_freq = int(self.edf_param['sfreq'])
        self.edf_param["edf_fn"] = file_path
        self.eeg_data, self.channel_names = read_eeg_data(self.raw)
        self.eeg_data_un60 = self.eeg_data.copy()

        print("Loading Complete.")
    

    def get_edf_info(self):
        return self.edf_param

    def get_sample_freq(self):
        return self.sample_freq
    
    def get_eeg_data_shape(self):
        return self.eeg_data.shape

    def get_eeg_data(self,start:int=None, end:int=None, filtered:bool=False):
        data = self.eeg_data if not filtered else self.filter_data
        if start is None and end is None:
            return data, self.channel_names
        elif start is None:
            return data[:, :end], self.channel_names
        elif end is None:
            return data[:, start:], self.channel_names
        else:
            return data[:, start:end], self.channel_names