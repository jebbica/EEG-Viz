# EEG-Viz #

## Window Overview ##

<img src="https://github.com/jebbica/EEG-Viz/blob/main/img/EEG%20Viz%20Window.png" >

## Usage ##
1. Import and load EEG *.edf file 
2. Select channels to plot

### Loading an EDF ###
The user can select a *.edf file to import and load for analysis of the EEG data.

<img src="https://github.com/jebbica/EEG-Viz/blob/main/img/open%20file.png" >

1. To load an edf, click on the `Open EDF` button on the upper left corner of the window.
2. A window will open to select the edf file to open. Only valid files (*.edf) can be loaded into the application. 
3. After the edf is successfully loaded, waveforms for each channel will be plotted in the waveform display window.
   - Information regarding the edf file will be shown in the EDF Information box shown on the right side of the main window.

### Display Settings ###
Options are provided to change the display of the waveforms in the Display box.

<img src="https://github.com/jebbica/EEG-Viz/blob/main/img/display.png" >


Users can choose any channel(s) to display. One or multiple electrodes can be selected for viewing. To include channels to process, click the `Choose Channels` button.

<p align="center">
<img src="https://github.com/jebbica/EEG-Viz/blob/main/img/channel%20selection.png" >
</p>

A window will open, allowing users to select any number of channels. Select which channels to view, and click the OK button.
- To select the number of channels to be displayed, enter or change `Number of Channels to Display`
- To change the number of seconds of the waveform to display, enter or change `Display Time Window`
- To change the time window increment, enter or change the percentage `Display Time Window Increment`
- With any changes of the signal display, click the `Update Plot` button to view the newly updated signal display
- Use the `Normalize Vertically` checkbox to toggle between the normalized and unnormalized signal.
  
<p align="center">
<img src="https://github.com/jebbica/EEG-Viz/blob/main/img/signal%20example.png" >
</p>

### Plotting Time Frequency Graph ###
Users have the option of viewing the time frequency plot of a single electrode at a time. The time interval plotted will be the same as what is viewed in the main window’s waveform display.
1. Use the `Plot Time Frequency` button on the upper right of the main window to open the channel selection window
2. Select which channel’s time frequency plot to view > click OK
3. Use the legend on the right side to change the color palette of the plot
   
<p align="center">
<img src="https://github.com/jebbica/EEG-Viz/blob/main/img/tf%20plot.png" >
</p>

To change the time interval, return to the main window and change the interval of the main waveform, then reopen the time frequency plot.

## Contributors: ##
Department of Electrical and Computer Engineering, University of California, Los Angeles

- [Jessica Lin](https://www.linkedin.com/in/jessica4903/)
- [Lawrence Liu](https://www.linkedin.com/in/lawrence-liu-0a01391a7/)
- [Yipeng Zhang](https://zyp5511.github.io/)

Division of Pediatric Neurology, Department of Pediatrics, UCLA Mattel Children’s Hospital David Geffen School of Medicine

- [Hiroki Nariai](https://www.uclahealth.org/providers/hiroki-nariai)

EEG Visualizer references code from pyHFO

EEG Viz Document: https://docs.google.com/document/d/15jOJMiTojdR5mPBSyjdPqwLrKEg-ShcGIPCz6Vux0mM/edit?usp=sharing
