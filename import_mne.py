import mne
from mne.datasets import sample
import matplotlib.pyplot as plt

# Replace this with the path to your EDF file
file_path = 'Downloads/SC4001E0-PSG.edf'

# Load the EDF file
raw = mne.io.read_raw_edf(file_path, preload=True)

# Plot the raw data
raw.plot(duration=10, n_channels=30, scalings='auto')
plt.show()

# Apply a bandpass filter
raw.filter(1., 30., fir_design='firwin')

# Pick specific channels (e.g., EEG channels only)
picks = mne.pick_types(raw.info, meg=False, eeg=True, eog=False, stim=False)

# Plot the filtered data for the picked channels
raw.plot(duration=10, n_channels=10, picks=picks, scalings='auto')
plt.show()

# Apply a bandpass filter
raw.filter(1., 30., fir_design='firwin')

# Pick specific channels (e.g., EEG channels only)
picks = mne.pick_types(raw.info, meg=False, eeg=True, eog=False, stim=False)

# Plot the filtered data for the picked channelsMM                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      bnb
raw.plot(duration=10, n_channels=10, picks=picks, scalings='auto')
plt.show()
