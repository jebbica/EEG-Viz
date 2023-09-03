import numpy as np

def get_edf_info(raw):
    res = {
            "channels": raw.info['ch_names'],
            "sfreq": raw.info['sfreq'],
            "nchan": raw.info['nchan'],
            "meas_date": raw.info['meas_date'],
            "highpass": raw.info['highpass'],
            "lowpass": raw.info['lowpass'],
        }
    return res

def read_eeg_data(raw):
    raw_channels = raw.info['ch_names']
    data = []

    for raw_ch in raw_channels:
        ch_data = raw.get_data(raw_ch) * 1E6
        data.append(ch_data)

    eeg_data = np.squeeze(data)
    channel_names = np.array(raw_channels)
    #sort channel_names
    indexs = sorted(range(len(channel_names)), key=lambda x: int("".join([i for i in channel_names[x] if i.isdigit()])))
    eeg_data = eeg_data[indexs]
    channel_names = sorted(channel_names, key=lambda x: int("".join([i for i in x if i.isdigit()])))
    channel_names = np.array(channel_names)
    return eeg_data, channel_names