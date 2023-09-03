import os
import re
import sys
import traceback
from pathlib import Path
from queue import Queue

from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import pyqtSignal

import pyqtgraph as pg

from src.mini_hfo_app import HFO_App
from src.ui.plot_waveform import *
from src.utils.utils_gui import *
from src.ui.channels_selection import ChannelSelectionWindow
from src.ui.tf_channels_selection import TFChannelSelectionWindow



ROOT_DIR = Path(__file__).parent


class miniHFOWindow(QMainWindow):
    close_signal = pyqtSignal()
    def __init__(self):
        super(miniHFOWindow, self).__init__()
        self.ui = uic.loadUi(os.path.join(ROOT_DIR, 'src/ui/miniHFO.ui'), self)
        self.setWindowIcon(QtGui.QIcon(os.path.join(ROOT_DIR, 'src/ui/brain3.jpg')))

        self.setWindowTitle("EEG Viz")
        self.width = self.frameGeometry().width()
        self.height = self.frameGeometry().height()

        self.mini_hfo_app = HFO_App()
        self.threadpool = QThreadPool()


        self.waveform_plot_widget = pg.PlotWidget()
        self.widget.layout().addWidget(self.waveform_plot_widget, 0, 1)
        self.widget.layout().setRowStretch(0, 9)
        self.widget.layout().setRowStretch(1, 1)
        self.waveform_plot = PlotWaveform(self.waveform_plot_widget, self.mini_hfo_app)

        ## top toolbar buttons
        self.actionOpen_EDF_toolbar.triggered.connect(self.open_file)

        #channel select/plot buttons
        self.Choose_Channels_Button.setEnabled(False)
        self.waveform_plot_button.setEnabled(False)
        self.plot_time_frequency_button.setEnabled(False)

        
    def get_window_size(self):
        return self.width, self.height
    
    def set_channels_to_plot(self, channels_to_plot):
        self.waveform_plot.set_channels_to_plot(channels_to_plot)
        # print(f"Channels to plot: {self.channels_to_plot}")
        self.n_channel_input.setMaximum(len(channels_to_plot))
        self.n_channel_input.setValue(len(channels_to_plot))
        self.waveform_plot_button_clicked()
    
    def open_channel_selection(self):
        self.channel_selection_window = ChannelSelectionWindow(self.mini_hfo_app, self, self.close_signal)
        self.channel_selection_window.show()
    
    def channel_selection_update(self):
        self.channel_scroll_bar.setValue(0)
        self.waveform_time_scroll_bar.setValue(0)
        is_empty = self.n_channel_input.maximum() == 0
        self.waveform_plot.plot(0,0,empty=is_empty,update_hfo=True)

    def open_tf_channel_selection(self):
        self.tf_channel_selection_window = TFChannelSelectionWindow(hfo_app=self.mini_hfo_app, main_window=self, close_signal=self.close_signal)
        self.tf_channel_selection_window.show()

    def waveform_plot_button_clicked(self):
        time_window=self.display_time_window_input.value()
        self.waveform_plot.set_time_window(time_window)
        n_channels_to_plot=self.n_channel_input.value()
        self.waveform_plot.set_n_channels_to_plot(n_channels_to_plot)
        time_increment = self.Time_Increment_Input.value()
        self.waveform_plot.set_time_increment(time_increment)
        normalize_vertical = self.normalize_vertical_input.isChecked()
        self.waveform_plot.set_normalize_vertical(normalize_vertical)
        is_empty = self.n_channel_input.maximum() == 0
        start = self.waveform_plot.t_start
        first_channel_to_plot = self.waveform_plot.first_channel_to_plot
        
        t_value = int(start//(self.waveform_plot.get_time_window()*self.waveform_plot.get_time_increment()/100))
        self.waveform_time_scroll_bar.setMaximum(int(self.waveform_plot.get_total_time()/(self.waveform_plot.get_time_window()*self.waveform_plot.get_time_increment()/100)))
        self.waveform_time_scroll_bar.setValue(t_value)
        c_value = self.channel_scroll_bar.value()
        self.channel_scroll_bar.setMaximum(len(self.waveform_plot.get_channels_to_plot())-n_channels_to_plot)
        self.channel_scroll_bar.setValue(c_value)
        self.waveform_plot.plot(start,first_channel_to_plot,empty=is_empty,update_hfo=True)


    def get_window_time_and_length(self):
        t_start = self.scroll_time_waveform_plot()
        length = self.waveform_plot.get_time_window()
        return t_start, length

    def scroll_time_waveform_plot(self):
        t_start=self.waveform_time_scroll_bar.value()*self.waveform_plot.get_time_window()*self.waveform_plot.get_time_increment()/100
        self.waveform_plot.plot(t_start) #t_start in seconds
        # print(t_start)
        return t_start
    
    def scroll_channel_waveform_plot(self, event):
        channel_start=self.channel_scroll_bar.value()
        self.waveform_plot.plot(first_channel_to_plot=channel_start, update_hfo=True)

    def get_channels_to_plot(self):
        return self.waveform_plot.get_channels_to_plot()
    
    def get_channel_indices_to_plot(self):
        return self.waveform_plot.get_channel_indices_to_plot()

    def open_file(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Open File", "", "EDF Files (*.edf)")
        if fname:
            worker = Worker(self.read_edf, fname)
            worker.signals.result.connect(self.update_edf_info)
            self.threadpool.start(worker)

    def read_edf(self, fname, progress_callback):
        # self.reinitialize()
        self.mini_hfo_app.load_edf(fname)
        # print(self.mini_hfo_app.channel_names)
        eeg_data,channel_names=self.mini_hfo_app.get_eeg_data()
        edf_info=self.mini_hfo_app.get_edf_info()
        self.waveform_plot.init_eeg_data()
        filename = os.path.basename(fname)
        sample_freq = str(self.mini_hfo_app.sample_freq)
        num_channels = str(len(self.mini_hfo_app.channel_names))
        length = str(self.mini_hfo_app.eeg_data.shape[1])
        return [filename, sample_freq, num_channels, length]
    
    @pyqtSlot(list)
    def update_edf_info(self, results):
        self.filename.setText(results[0])
        self.sampfreq.setText(results[1])
        self.sample_freq = float(results[1])
        self.numchannels.setText(results[2])
        # print("updated")
        self.length.setText(str(round(float(results[3])/(60*float(results[1])),3))+" min")
        self.waveform_plot.plot(0, update_hfo=True)
        # print("plotted")
        #connect buttons
        self.waveform_time_scroll_bar.valueChanged.connect(self.scroll_time_waveform_plot)
        self.channel_scroll_bar.valueChanged.connect(self.scroll_channel_waveform_plot)
        self.waveform_plot_button.clicked.connect(self.waveform_plot_button_clicked)
        self.Choose_Channels_Button.clicked.connect(self.open_channel_selection)
        self.plot_time_frequency_button.clicked.connect(self.open_tf_channel_selection)
        #set the display time window spin box
        self.display_time_window_input.setValue(self.waveform_plot.get_time_window())
        self.display_time_window_input.setMaximum(self.waveform_plot.get_total_time())
        self.display_time_window_input.setMinimum(0.1)
        #set the n channel spin box
        self.n_channel_input.setValue(self.waveform_plot.get_n_channels_to_plot())
        self.n_channel_input.setMaximum(self.waveform_plot.get_n_channels())
        self.n_channel_input.setMinimum(1)
        #set the time scroll bar range
        self.waveform_time_scroll_bar.setMaximum(int(self.waveform_plot.get_total_time()/(self.waveform_plot.get_time_window()*self.waveform_plot.get_time_increment()/100)))
        self.waveform_time_scroll_bar.setValue(0)
        #set the channel scroll bar range
        self.channel_scroll_bar.setMaximum(self.waveform_plot.get_n_channels()-self.waveform_plot.get_n_channels_to_plot())
        self.normalize_vertical_input.stateChanged.connect(self.waveform_plot_button_clicked)
        #enable buttons after choosing edf
        self.Choose_Channels_Button.setEnabled(True)
        self.waveform_plot_button.setEnabled(True)
        self.plot_time_frequency_button.setEnabled(True)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = miniHFOWindow()
    mainWindow.show()
    sys.exit(app.exec_())
    