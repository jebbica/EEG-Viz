import sys
from PyQt5 import QtCore, QtGui, QtWidgets
import pyqtgraph as pg # We will try using pyqtgraph for plotting
import numpy as np
import time
import mne
# from superqt import QDoubleRangeSlider
from tqdm import tqdm
import os
from src.mini_hfo_app import HFO_App
import random

curr_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.dirname(curr_dir))


class PlotWaveform(QtWidgets.QGraphicsView):
    def __init__(self, plot_loc:pg.PlotWidget, backend: HFO_App):

        super().__init__()

        self.waveform_display = plot_loc 
        self.waveform_display.setMouseEnabled(x=False, y=False)
        self.waveform_display.getPlotItem().hideAxis('bottom')
        self.waveform_display.getPlotItem().hideAxis('left')
        self.plot_loc = plot_loc
        self.waveform_display.setBackground('w')

        self.time_window = 20 #20 second time window
        self.time_increment =20
        self.old_size = (self.plot_loc.x(),self.plot_loc.y(),self.plot_loc.width(),self.plot_loc.height())
        self.t_start = 0
        self.first_channel_to_plot = 0
        self.n_channels_to_plot = 10
        self.backend = backend
        self.filtered = False
        self.time_window_increment = 100 #in percent
        self.normalize_vertical = False

    def update_backend(self,new_backend:HFO_App,init_eeg_data:bool=True):
        self.backend = new_backend
        if init_eeg_data:
            self.init_eeg_data()

    def init_eeg_data(self):
        # print("reinit eeg data")
        self.filtered = False
        self.waveform_display.clear()
        eeg_data,self.channel_names=self.backend.get_eeg_data()

        self.channel_names = list(self.channel_names)
        self.edf_info=self.backend.get_edf_info()

        self.sample_freq = self.edf_info['sfreq']
        self.time = np.arange(0,eeg_data.shape[1]/self.sample_freq,1/self.sample_freq) # time in seconds
        self.n_channels = len(self.channel_names)
        self.n_channels_to_plot = min(self.n_channels,self.n_channels_to_plot)
        self.channels_to_plot = self.channel_names.copy()
        self.channel_indices_to_plot = np.arange(self.n_channels)
        self.waveform_display.getPlotItem().showAxis('bottom')
        self.waveform_display.getPlotItem().showAxis('left')


    def get_n_channels(self):
        return self.n_channels
    
    def get_n_channels_to_plot(self):
        return self.n_channels_to_plot

    def get_total_time(self):
        return self.time[-1]

    def get_time_window(self): #returns length of window in seconds
        return self.time_window
    
    def get_time_increment(self):
        return self.time_increment
    
    def set_normalize_vertical(self,normalize_vertical:bool):
        self.normalize_vertical = normalize_vertical

    def set_time_window(self,time_window:float):
        self.time_window = time_window

    def set_time_increment(self,time_increment:float):
        self.time_increment = time_increment
        
    def set_n_channels_to_plot(self,n_channels_to_plot:int):
        self.n_channels_to_plot = n_channels_to_plot

    def get_channels_to_plot(self):
        return self.channels_to_plot
    
    def get_channel_indices_to_plot(self):
        return self.channel_indices_to_plot
    
    def set_channels_to_plot(self,channels_to_plot:list):
        self.channels_to_plot = channels_to_plot
        # print(self.channels_to_plot)
        self.channel_indices_to_plot = [self.channel_names.index(channel) for channel in channels_to_plot]


    def set_channel_indices_to_plot(self,channel_indices_to_plot:list):
        self.channel_indices_to_plot = channel_indices_to_plot
        self.channels_to_plot = [self.channel_names[index] for index in channel_indices_to_plot]


    def plot(self,t_start:float = None,first_channel_to_plot:int = None, empty=False, update_hfo=False):
        if empty:
            self.waveform_display.clear()
            return
        if t_start is None:
            t_start = self.t_start
        else:
            self.t_start = t_start #this allows us to keep track of the start time of the plot and thus replot when the time window changes or when the number of channels
        if first_channel_to_plot is None:
            first_channel_to_plot = self.first_channel_to_plot
        else:
            self.first_channel_to_plot = first_channel_to_plot
        self.waveform_display.clear()

        t_end = min(t_start+self.time_window,self.time[-1])

        eeg_data_to_display,_=self.backend.get_eeg_data(int(t_start*self.sample_freq),int(t_end*self.sample_freq), self.filtered)
        #normalize each to 0-1
        eeg_data_to_display = eeg_data_to_display[self.channel_indices_to_plot,:]
        if self.normalize_vertical:
            eeg_data_to_display = (eeg_data_to_display-eeg_data_to_display.min(axis = 1,keepdims = True))
            eeg_data_to_display = eeg_data_to_display/np.max(eeg_data_to_display)
        else:
            eeg_data_to_display = (eeg_data_to_display-eeg_data_to_display.min(axis = 1,keepdims = True))/(np.ptp(eeg_data_to_display,axis = 1,keepdims = True))
            #replace nans with 0
            eeg_data_to_display[np.isnan(eeg_data_to_display)] = 0
        #shift the ith channel by 1.1*i
        eeg_data_to_display = eeg_data_to_display-1.1*np.arange(eeg_data_to_display.shape[0])[:,None]
        
        time_to_display = self.time[int(t_start*self.sample_freq):int(t_end*self.sample_freq)]
        top_value=eeg_data_to_display[first_channel_to_plot].max()

        for i in range(first_channel_to_plot,first_channel_to_plot+self.n_channels_to_plot):
            channel = self.channels_to_plot[i]
            self.waveform_display.plot(time_to_display,eeg_data_to_display[i],pen = pg.mkPen(color = (0,0,255),width=0.5))

        #set y ticks to channel names
        channel_names_locs = -1.1*np.arange(eeg_data_to_display.shape[0])[:, None]+1.1/2
        self.waveform_display.getAxis('left').setTicks([[(channel_names_locs[i], self.channels_to_plot[i])
                 for i in range(first_channel_to_plot,first_channel_to_plot+self.n_channels_to_plot)]])
        #set the max and min of the x axis
        self.waveform_display.setXRange(t_start,t_end)
