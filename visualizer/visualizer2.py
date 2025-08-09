import mne
import matplotlib.pyplot as plt

# Path to your EDF file
edf_file = "/Users/larineouyang/bdsp-bids/I0003/sub-I0003175730170/ses-1/eeg/sub-I0003175730170_ses-1_task-psg_eeg.edf"

# Load the EDF file
raw = mne.io.read_raw_edf(edf_file, preload=True)

# Print channel info and sampling rate
print("Channels:", raw.ch_names)
print("Sampling rate:", raw.info['sfreq'])

# Pick EEG channels only (in case there are other types)
raw.pick_types(eeg=True)

# Plot a 10-second window of EEG data
start_time = 0  # in seconds
duration = 10   # in seconds

raw.plot(start=start_time, duration=duration, scalings='auto', title="EEG Signal")

# Optional: Save a static image of the plot
fig = raw.plot(start=start_time, duration=duration, scalings='auto', show=False)
fig.savefig("eeg_plot.png", dpi=300)
