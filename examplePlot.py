import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import spectrogram

# Generate random data for the example
np.random.seed(42)
fs = 500  # Sampling frequency
t = np.linspace(0, 10, fs*10)  # Time vector
signal = np.sin(2*np.pi*10*t) + np.sin(2*np.pi*20*t) + 0.5 * np.random.randn(len(t))  # Simulated signal

# Compute the spectrogram
frequencies, times, Sxx = spectrogram(signal, fs)

# Simulated probability line for spike detection
probability = 0.3 + 0.4 * np.sin(2*np.pi*0.5*t) + 0.1 * np.random.randn(len(t))

# Apply a cutoff to detect spikes
cutoff = 0.43
spikes = probability > cutoff
spike_times = t[spikes]

# Create the plot
fig, axs = plt.subplots(3, 1, figsize=(10, 8), sharex=True)

# Plot the spectrogram
axs[0].pcolormesh(times, frequencies, 10 * np.log10(Sxx), shading='gouraud')
axs[0].set_ylabel('Frequency [Hz]')
axs[0].set_title('Spectrogram')

# Plot the probability line with spikes
axs[1].plot(t, probability, label='Spike Detection Probability')
axs[1].scatter(spike_times, probability[spikes], color='red', label='Detected Spikes', zorder=5)
axs[1].axhline(y=cutoff, color='black', linestyle='--', label='Cutoff = 0.43')
axs[1].set_ylabel('Probability')
axs[1].legend()
axs[1].set_title('Spike Detection')

# Add some example annotations
axs[2].plot(t, signal)
axs[2].annotate('Event A', xy=(2, 1), xytext=(3, 1.5), arrowprops=dict(facecolor='black', arrowstyle='->'))
axs[2].annotate('Event B', xy=(7, -1), xytext=(8, -1.5), arrowprops=dict(facecolor='black', arrowstyle='->'))
axs[2].set_ylabel('Signal Amplitude')
axs[2].set_xlabel('Time [s]')
axs[2].set_title('Signal with Annotations')

plt.tight_layout()
plt.show()
