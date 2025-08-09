import os
import re
import mne
import numpy as np
import matplotlib.pyplot as plt
from mne.time_frequency import psd_array_multitaper

# === User Configuration ===
edf_path = "/Users/larineouyang/bdsp-bids/I0003/sub-I0003175623676(372days)/ses-1/eeg/sub-I0003175623676_ses-1_task-psg_eeg.edf"
save_dir = "/Users/larineouyang/GitHub/EEG-Processing-Lib/visualizer/I0003 Spectrogram"
epoch_duration = 30  # seconds
fmin, fmax = 0.5, 30  # frequency range for EEG in Hz

# === Load EEG ===
raw = mne.io.read_raw_edf(edf_path, preload=True)
raw.pick_types(eeg=True)
channel_name = raw.ch_names[0]  # or specify like 'C3'
data, sfreq = raw.get_data(picks=channel_name), raw.info['sfreq']
signal = data[0] * 1e6

# === Segment signal into 30s epochs ===
samples_per_epoch = int(epoch_duration * sfreq)
n_epochs = len(signal) // samples_per_epoch

# === Compute PSD per epoch ===
epochs = []
for i in range(n_epochs):
    segment = signal[i * samples_per_epoch:(i + 1) * samples_per_epoch]
    epochs.append(segment)
epochs = np.array(epochs)  # shape = (#epochs, #sample points)

psd_list, freqs = psd_array_multitaper(epochs, sfreq=sfreq, fmin=fmin, fmax=fmax,
            bandwidth=0.5, adaptive=True, normalization='full', verbose=False)
# psd_list.shape = (n_epochs, n_freqs)

psd_array = psd_list.T  # shape: (n_freqs, n_epochs)
psd_db = 10 * np.log10(psd_array + 1e-12)

# === Plot spectrogram ===
plt.figure(figsize=(12, 5))
plt.imshow(psd_db, aspect='auto', origin='lower', vmin=-5, vmax = 20,
           extent=[0, n_epochs * epoch_duration/3600, freqs[0], freqs[-1]],
           cmap='turbo')
plt.colorbar(label='Power (dB)')
plt.xlabel('Time (h)')
plt.ylabel('Frequency (Hz)')
plt.title(f'Spectrogram of EEG Channel: {channel_name}')
plt.tight_layout()

# === Parse session number from file path ===
filename = os.path.basename(edf_path).replace('.edf', '.png')

# === Save plot ===
os.makedirs(save_dir, exist_ok=True)
save_path = os.path.join(save_dir, filename)
plt.savefig(save_path)
plt.close()

print(f"✅ Spectrogram saved to: {save_path}")
