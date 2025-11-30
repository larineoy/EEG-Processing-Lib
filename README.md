# EEG-Processing-Lib

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Status](https://img.shields.io/badge/status-Active-brightgreen.svg)
![Python](https://img.shields.io/badge/python-3.7+-blue.svg)

A comprehensive Python toolkit for preprocessing, analyzing, and visualizing EEG (electroencephalography) data, with specialized support for sleep EEG/polysomnography (PSG) studies. This library provides tools for bandpower extraction, spectrogram generation, spike detection, and visualization of EEG data in BIDS format.

## Features

### Core Functionality

- **EEG Data Loading & Processing**
  - Support for EDF file format (European Data Format)
  - BIDS (Brain Imaging Data Structure) format support
  - MATLAB HDF5 file reading capabilities
  - Memory-efficient chunked processing for large datasets

- **Spectral Analysis**
  - Multitaper power spectral density (PSD) computation
  - Spectrogram generation with configurable epochs
  - Frequency band power extraction (delta, theta, alpha, beta, sigma, slow wave)
  - Sleep stage-specific bandpower analysis

- **Visualization**
  - Interactive EEG signal plotting
  - Spectrogram visualization with time-frequency representations
  - Spike detection probability plots
  - Multi-channel EEG display

- **Sleep EEG Analysis**
  - Sleep stage annotation loading and processing
  - Sleep stage-specific feature extraction
  - Integration with PSG metadata
  - Support for standard 10-20 electrode montage

- **Spike Detection**
  - Probability-based spike detection
  - Spike visualization overlayed on spectrograms
  - Configurable detection thresholds

## Installation

### Prerequisites

- Python 3.7 or higher
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone https://github.com/larineoy/EEG-Processing-Lib.git
cd EEG-Processing-Lib
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

### Dependencies

The library relies on the following key packages:

- **mne** (0.23.4): MNE-Python for EEG/MEG data processing
- **numpy** (1.21.0): Numerical computing
- **scipy** (1.7.0): Scientific computing and signal processing
- **pandas** (1.3.0): Data manipulation and analysis
- **matplotlib** (3.4.2): Plotting and visualization
- **pyedflib** (0.1.22): EDF file I/O operations

## Project Structure

```
EEG-Processing-Lib/
├── bandpower_extraction/       # Frequency band power extraction tools
│   ├── extract_bandpower.py    # Standard bandpower extraction
│   ├── extract_bandpower_scaled.py  # Scaled bandpower extraction
│   ├── check_units.py          # Unit verification utilities
│   ├── bdsp-bids/              # BIDS format data directory
│   └── results/                # Extracted feature outputs
│
├── visualizer/                 # Visualization and analysis tools
│   ├── visualizer.py           # Basic spectrogram visualization
│   ├── visualizer2.py          # Enhanced visualization with chunking
│   ├── visualizer3.py          # Memory-efficient large file processing
│   ├── data_loading_helpers.py # Data loading utilities
│   ├── matlab_visualizer_fixed.py    # MATLAB file visualization
│   ├── read_matlab_files_fixed.py    # MATLAB file reading
│   └── read_matlab_h5py_fixed.py     # HDF5 file reading
│
├── plotting/                   # Basic plotting utilities
│   ├── plot_EEG.py            # EEG signal plotting
│   └── examplePlot.py         # Example plotting scripts
│
├── spikes/                     # Spike detection tools
│   └── spike_detection_plot.py # Spike detection and visualization
│
├── requirements.txt            # Python dependencies
├── LICENSE                     # MIT License
└── README.md                   # This file
```

## Usage

### Basic EEG Data Loading

```python
import mne

# Load an EDF file
raw = mne.io.read_raw_edf('path/to/eeg_file.edf', preload=True)

# Pick only EEG channels
raw.pick_types(eeg=True)

# Get basic information
print(raw.info)
```

### Generating Spectrograms

The visualizer modules can create spectrograms from EEG data:

```python
# Example: Using visualizer3.py for large files
# Configure your EDF path and output directory
edf_path = "path/to/your/eeg_file.edf"
save_dir = "output/spectrograms/"

# The script will:
# - Load EEG data in chunks for memory efficiency
# - Compute PSD using multitaper method
# - Generate spectrogram plots
# - Save results to the specified directory
```

### Extracting Bandpower Features

For sleep EEG analysis with bandpower extraction:

```python
# Run bandpower extraction script
python bandpower_extraction/extract_bandpower.py

# Or for scaled version
python bandpower_extraction/extract_bandpower_scaled.py

# Results will be saved to bandpower_extraction/results/
```

### Spike Detection

```python
# Use spike detection visualization
from spikes.spike_detection_plot import process_and_plot

# Load spike probability data and corresponding spectrogram
spike_prob_file = "path/to/spike_prob.npz"
spectrogram_file = "path/to/spectrogram.png"
output_file = "output/spike_detection.png"

process_and_plot(spike_prob_file, spectrogram_file, output_file)
```

## Data Format Support

### BIDS Format

The library works with BIDS-structured EEG data:

```
sub-<participant_id>/
  ses-<session_id>/
    eeg/
      sub-<participant_id>_ses-<session_id>_task-<task>_eeg.edf
      sub-<participant_id>_ses-<session_id>_task-<task>_eeg.json
      sub-<participant_id>_ses-<session_id>_task-<task>_channels.tsv
      sub-<participant_id>_ses-<session_id>_sleepannotations.csv
      sub-<participant_id>_ses-<session_id>_eventannotations.csv
```

### Sleep Stage Annotations

Sleep annotations are expected in CSV format with a `sleep_stage` column containing values:
- `WAKE` or `W`: Wake stage
- `REM`: REM sleep
- `N1`, `N2`, `N3`, `N4`: NREM sleep stages
- `UNSCORED`: Unscored epochs

## Frequency Bands

The library supports extraction of standard EEG frequency bands:

- **Slow wave**: < 1 Hz
- **Delta**: 1-4 Hz
- **Theta**: 4-8 Hz
- **Alpha**: 8-12 Hz
- **Sigma**: 12-15 Hz (sleep spindles)
- **Beta**: 15-30 Hz

## Channel Configuration

Standard 10-20 electrode montage channels are supported:
- Frontal: F3, F4
- Central: C3, C4
- Occipital: O1, O2

## Examples

### Example 1: Quick Spectrogram Generation

```python
import mne
import numpy as np
import matplotlib.pyplot as plt
from mne.time_frequency import psd_array_multitaper

# Load EEG
raw = mne.io.read_raw_edf('example.edf', preload=True)
raw.pick_types(eeg=True)

# Get data for a channel
channel_name = 'C3'
data, sfreq = raw.get_data(picks=channel_name), raw.info['sfreq']
signal = data[0] * 1e6  # Convert to microvolts

# Segment into 30s epochs
epoch_duration = 30
samples_per_epoch = int(epoch_duration * sfreq)
n_epochs = len(signal) // samples_per_epoch

epochs = []
for i in range(n_epochs):
    segment = signal[i * samples_per_epoch:(i + 1) * samples_per_epoch]
    epochs.append(segment)
epochs = np.array(epochs)

# Compute PSD
psd_list, freqs = psd_array_multitaper(
    epochs, sfreq=sfreq, fmin=0.5, fmax=30,
    bandwidth=0.5, adaptive=True, normalization='full'
)

# Create spectrogram
psd_array = psd_list.T
psd_db = 10 * np.log10(psd_array + 1e-12)

plt.figure(figsize=(12, 5))
plt.imshow(psd_db, aspect='auto', origin='lower',
           extent=[0, n_epochs * epoch_duration/3600, freqs[0], freqs[-1]],
           cmap='turbo')
plt.colorbar(label='Power (dB)')
plt.xlabel('Time (h)')
plt.ylabel('Frequency (Hz)')
plt.title(f'Spectrogram: {channel_name}')
plt.show()
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

This library is built on top of excellent open-source tools:
- [MNE-Python](https://mne.tools/stable/index.html) for EEG/MEG processing
- [NumPy](https://numpy.org/) and [SciPy](https://scipy.org/) for scientific computing
- The BIDS community for data format standards

## Citation

If you use this library in your research, please consider citing:

```bibtex
@software{eeg_processing_lib,
  title = {EEG-Processing-Lib: A Python Toolkit for EEG Data Analysis},
  author = {Your Name},
  url = {https://github.com/larineoy/EEG-Processing-Lib},
  year = {2024}
}
```

## Contact

For questions, issues, or feature requests, please open an issue on the [GitHub repository](https://github.com/larineoy/EEG-Processing-Lib/issues).
