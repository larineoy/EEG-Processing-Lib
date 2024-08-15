import mne
import matplotlib.pyplot as plt
import numpy as np
from pyedflib import EdfWriter
#import mne_connectivity

# Path to your EDF file
edf_file = "ASD/12460549_20220608_150447_fil.edf"

# Read the EDF file with preload=True
edf = mne.io.read_raw_edf(edf_file, preload=True)

# Apply notch filter at 50Hz
edf.notch_filter(freqs=50)

# Apply bandpass filter from 0.3 to 35 Hz
edf.filter(l_freq=0.3, h_freq=35)

# Create EdfWriter instance
output_edf_file = "12460549_20220608_150447_fil-clean.edf"

# Get the channel names from the edf object
channels = edf.ch_names

# Define signal headers
signal_headers = []
for i, ch in enumerate(channels):
    signal_headers.append({
        'label': ch,
        'dimension': 'uV',
        'sample_rate': int(edf.info['sfreq']),
        'physical_max': 32767,
        'physical_min': -32768,
        'digital_min': -32768,
        'digital_max': 32767,
        'transducer': '',
        'prefilter': ''
    })

eeg = edf.get_data()
# convert to uV (microvolts)
eeg = eeg*1e6   

with EdfWriter(output_edf_file, len(channels), file_type=1) as writer:
    # Set signal headers
    writer.setSignalHeaders(signal_headers)
    # Set start datetime
    if edf.info['meas_date'] is not None:
        start_datetime = edf.info['meas_date'].strftime('%d %b %Y %H:%M:%S')
        writer.setStartdatetime(start_datetime)
    # Write samples (ensure data is in correct format)
    writer.writeSamples(eeg)  # Transpose back to channels x samples

print(f"Filtered data has been written to {output_edf_file}")

exit()






# get signal length in sample points
len = eeg.shape[1]  

# get sampling frequency in Hz
fs = edf.info['sfreq']   

# window is 30 seconds long, convert to number of sample points
window_size = int(30*fs)   

# get the starting point of each window
seg_start_ids = np.arange(0, len-window_size+1, window_size)  
segs = []

for start_idx in seg_start_ids:
    seg = eeg[:, start_idx:start_idx+window_size]  # get a segment, containing all channels
    segs.append(seg)
segs = np.array(segs)  # convert to numpy array
# segs.shape = (#seg, #channel, #sample points in one window)

spec, freq = mne.time_frequency.psd_array_multitaper(segs, fs, fmin=0.5, fmax=30, bandwidth=0.5, normalization='full')
spec_db = 10*np.log10(spec)   # convert from uV^2/Hz to decibel (dB)
# spec_db.shape = (#seg, #channel, #frequency bins)
# freq.shape = (#frequency bins,)

np.savez_compressed('final_spectrogram.npz', spec_db=spec_db, freq=freq, seg_start_ids=seg_start_ids)

segs.plot()

print()