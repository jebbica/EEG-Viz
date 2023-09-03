from PyQt5.QtWidgets import QDialog, QApplication, QGridLayout
import pyqtgraph as pg
import sys
from src.ui.plot_waveform import *
from src.mini_hfo_app import HFO_App
from src.utils.utils_feature import *
from scipy.signal import butter, sosfiltfilt

class PlotTimeFrequency(QDialog):
    def __init__(self, hfo_app=None, main_window=None, close_signal = None, channel_to_plot = None):
        super().__init__()
        self.hfo_app = hfo_app
        self.channel_to_plot = channel_to_plot
        self.main_window = main_window
        self.setWindowTitle(self.channel_to_plot[0])
        self.initUI()

    def initUI(self):

        #adjust size of window to match main window
        self.main_window_width, self.main_window_height = self.main_window.get_window_size()
        # print(self.main_window_width)
        self.resize(int(self.main_window_width*(8/9)), int(self.main_window_height*(1/2)))

        layout = QGridLayout(self)
        pg.setConfigOptions(antialias=True)
        pg.setConfigOptions(imageAxisOrder='row-major')
        pg.setConfigOption('background', 'w')
        spectrum_layout = pg.GraphicsLayoutWidget()
        pg_plt = spectrum_layout.addPlot()
        pg_plt.setMouseEnabled(x = False, y = False)
        img = pg.ImageItem()
        pg_plt.addItem(img)
        pg_plt.invertY()
        hist = pg.HistogramLUTItem()
        hist.setImageItem(img)
        spectrum_layout.addItem(hist)

        # get data
        filename = self.hfo_app.filename #or os.path.basename(fname)?

        #get data and sample freq, and time data
        data, channels, sf = self.read_edf(filename)
        data = data[np.where(channels == self.channel_to_plot)][0]
        t_start, length = self.main_window.get_window_time_and_length()
        # print(t_start, length)

        #get new boundary and compute time freq
        start, end, start_index, end_index  = self.calcuate_boundary(t_start * sf, (t_start + length) * sf, length)
        start_index = t_start*sf
        end_index = (t_start + length)*sf
        start_index = int(start_index)
        end_index = int(end_index)

        data_1c = data[start_index:end_index]
        time_frequency = compute_spectrum(data_1c)
        img.setImage(time_frequency)


        hist.setLevels(np.min(time_frequency), np.max(time_frequency))
        hist.gradient.restoreState(
            {'mode': 'rgb',
            'ticks': [(0.5, (0, 182, 188, 255)),
                    (1.0, (246, 111, 0, 255)),
                    (0.0, (75, 0, 113, 255))]})

        pg_plt.setLabel('bottom', "Time (s)")
        pg_plt.setLabel('left', "Frequency", units='Hz')

        #set ticks for plot
        freq_ticks = np.linspace(0, time_frequency.shape[0], 5)
        freq_ticks_label = freq_ticks[::-1]
        freq_label = [(v, str(l)) for v, l in zip(freq_ticks, freq_ticks_label)]
        pg_plt.getAxis('left').setTicks([freq_label])

        time_ticks = np.linspace(0,sf*(length), 11)
        rounded_time = np.round(np.linspace(t_start, t_start + length, 11), 0)
        time_label = [(v, str(l)) for v, l in zip(time_ticks, rounded_time)]
        pg_plt.getAxis('bottom').setTicks([time_label])

        layout.addWidget(spectrum_layout, 0, 0)
        self.setLayout(layout)


    def read_edf(self, fname):
        # self.hfo_app.load_edf(fname)
        eeg_data, channel_names = self.hfo_app.get_eeg_data()
        # print(eeg_data)
        # print(channel_names)
        edf_info = self.hfo_app.get_edf_info()
        sample_freq = edf_info['sfreq']
        return eeg_data, channel_names, sample_freq
    
    def calcuate_boundary(self, start:int, end:int, length:int, win_len=2000)->tuple:
        """_summary_

        Args:
            start (int): the start of the window
            end (int): the end of the window
            length (int): the length of the signal
            win_len (int, optional): the length of the window we want to extend the signal to . Defaults to 2000.

        Returns:
            tuple: the start and end of the extended window, and the new shifted start and end of the window
        """
        if start < win_len: 
            return 0, int(win_len*2),start, end
        if end > length - win_len:
            #in this case int(length-win_len*2) is the new start, so minus the start and end by that
            return int(length - win_len*2), -1, start-int(length-win_len*2), end-int(length-win_len*2)
        return int(0.5*(start + end) - win_len), int(0.5*(start + end) + win_len), start-int(0.5*(start + end) - win_len), end-int(0.5*(start + end) - win_len)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    dialog = PlotTimeFrequency()
    dialog.show()
    sys.exit(app.exec_())