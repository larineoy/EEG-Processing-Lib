import mne
import pandas as pd
import matplotlib.pyplot as plt

# edf = mne.io.read_raw_edf('Downloads/sub-01_task-run1_eeg.edf', preload=True)

# # Print the annotations if they exist
# if edf.annotations:
#     print(pd.DataFrame(edf.annotations))
# else:
#     print("No annotations found.")

# # Plot the raw EEG data
# edf.plot(duration=10, n_channels=30, scalings='auto')
# plt.show()

# Load the EEG data
raw = mne.io.read_raw_edf('Downloads/sub-01_task-run1_eeg.edf', preload=True)

# Plot the raw EEG data
raw.plot(duration=10, n_channels=30, scalings='auto')
plt.show()

# # View basic information
# raw.info

# # Load the participants' responses
# # responses = pd.read_csv('path_to_responses_file.csv')

# # View basic information
# # responses.head()

# events = mne.find_events(raw, stim_channel='STI 014')

# # View events
# events[:5]

# # Define the event IDs
# event_id = {'music': 1}  # Example: event code for music onset

# # Extract epochs
# epochs = mne.Epochs(raw, events, event_id, tmin=-3, tmax=15, baseline=None)

# # View basic information
# epochs.info

# # Extract data from epochs
# data = epochs.get_data()

# # Example: Combine data with responses
# # combined_data = pd.concat([pd.DataFrame(data), responses], axis=1)

# # View combined data
# # combined_data.head()
