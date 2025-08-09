import os
import re
import mne
import numpy as np
import matplotlib.pyplot as plt
from mne.time_frequency import psd_array_multitaper
import gc

# === User Configuration ===
edf_path = "/Users/larineouyang/bdsp-bids/I0003/sub-I0003175473558/ses-1/eeg/sub-I0003175473558_ses-1_task-psg_eeg.edf"
save_dir = "/Users/larineouyang/GitHub/EEG-Processing-Lib/visualizer/spectrograms"
epoch_duration = 30  # seconds
fmin, fmax = 0.5, 30  # frequency range for EEG in Hz
chunk_duration = 1800  # Process 30 minutes at a time to manage memory
preferred_channels = ['C3', 'C4', 'Cz', 'F3', 'F4', 'O1', 'O2']  # Common EEG channels

def extract_patient_id(file_path):
    """Extract patient ID from the file path"""
    match = re.search(r"sub-I0003(\d+)", file_path)
    return match.group(1) if match else "unknown"

def extract_session_num(file_path):
    """Extract session number from the file path"""
    match = re.search(r"ses-(\d+)", file_path)
    return match.group(1) if match else "X"

def find_best_channel(raw, preferred_channels):
    """Find the best available EEG channel from preferred list"""
    available_channels = [ch for ch in preferred_channels if ch in raw.ch_names]
    if available_channels:
        return available_channels[0]
    # If no preferred channels found, use first EEG channel
    eeg_channels = mne.pick_types(raw.info, eeg=True)
    if len(eeg_channels) > 0:
        return raw.ch_names[eeg_channels[0]]
    else:
        raise ValueError("No EEG channels found in the data")

def process_eeg_chunk(signal_chunk, sfreq, epoch_duration, fmin, fmax):
    """Process a chunk of EEG data and return PSD array"""
    samples_per_epoch = int(epoch_duration * sfreq)
    n_epochs = len(signal_chunk) // samples_per_epoch
    
    if n_epochs == 0:
        return None, None
    
    psd_list = []
    freqs = None
    
    for i in range(n_epochs):
        start_idx = i * samples_per_epoch
        end_idx = (i + 1) * samples_per_epoch
        segment = signal_chunk[start_idx:end_idx]
        
        try:
            psd, f = psd_array_multitaper(
                segment, sfreq=sfreq, fmin=fmin, fmax=fmax,
                bandwidth=4, adaptive=True, normalization='full', verbose=False
            )
            if freqs is None:
                freqs = f
            psd_list.append(psd)
        except Exception as e:
            print(f"Warning: Skipping epoch {i} due to error: {e}")
            continue
    
    if not psd_list:
        return None, None
        
    psd_array = np.array(psd_list).T  # shape: (n_freqs, n_epochs)
    return psd_array, freqs

print(f"Loading EDF file: {edf_path}")

# === Load EEG (header only first) ===
try:
    raw = mne.io.read_raw_edf(edf_path, preload=False, verbose=False)
    print(f"EDF loaded successfully. Duration: {raw.times[-1]:.1f} seconds ({raw.times[-1]/3600:.1f} hours)")
    
    # Pick EEG channels only
    raw.pick_types(eeg=True, exclude='bads')
    print(f"Available EEG channels: {raw.ch_names}")
    
    # Find best channel to use
    channel_name = find_best_channel(raw, preferred_channels)
    print(f"Using channel: {channel_name}")
    
    # Get sampling frequency
    sfreq = raw.info['sfreq']
    print(f"Sampling frequency: {sfreq} Hz")
    
    # Calculate total duration and chunks needed
    total_duration = raw.times[-1]
    n_chunks = int(np.ceil(total_duration / chunk_duration))
    print(f"Processing in {n_chunks} chunks of {chunk_duration/60:.1f} minutes each")
    
    # Process data in chunks
    all_psd_arrays = []
    all_freqs = None
    total_epochs_processed = 0
    
    for chunk_idx in range(n_chunks):
        print(f"Processing chunk {chunk_idx + 1}/{n_chunks}...")
        
        # Calculate time range for this chunk
        start_time = chunk_idx * chunk_duration
        end_time = min((chunk_idx + 1) * chunk_duration, total_duration)
        
        # Load only this chunk of data
        raw_chunk = raw.copy().crop(tmin=start_time, tmax=end_time)
        raw_chunk.load_data()
        
        # Get data for the selected channel
        data = raw_chunk.get_data(picks=channel_name)
        signal_chunk = data[0]
        
        # Process this chunk
        psd_array, freqs = process_eeg_chunk(signal_chunk, sfreq, epoch_duration, fmin, fmax)
        
        if psd_array is not None:
            all_psd_arrays.append(psd_array)
            if all_freqs is None:
                all_freqs = freqs
            total_epochs_processed += psd_array.shape[1]
        
        # Clear memory
        del raw_chunk, data, signal_chunk
        gc.collect()
    
    if not all_psd_arrays:
        raise ValueError("No valid data could be processed")
    
    # Combine all PSD arrays
    print(f"Combining data from {len(all_psd_arrays)} chunks...")
    combined_psd = np.concatenate(all_psd_arrays, axis=1)
    psd_db = 10 * np.log10(combined_psd + 1e-12)
    
    print(f"Final spectrogram shape: {psd_db.shape} (frequencies x epochs)")
    print(f"Total epochs processed: {total_epochs_processed}")
    
    # === Plot spectrogram ===
    plt.figure(figsize=(15, 6))
    plt.imshow(psd_db, aspect='auto', origin='lower',
               extent=[0, total_epochs_processed * epoch_duration, all_freqs[0], all_freqs[-1]],
               cmap='viridis')
    plt.colorbar(label='Power (dB)')
    plt.xlabel('Time (s)')
    plt.ylabel('Frequency (Hz)')
    plt.title(f'Spectrogram of EEG Channel: {channel_name}\n'
              f'Duration: {total_epochs_processed * epoch_duration / 3600:.1f} hours')
    plt.tight_layout()
    
    # === Generate filename with patient ID ===
    patient_id = extract_patient_id(edf_path)
    session_num = extract_session_num(edf_path)
    filename = f"sub-I0003{patient_id}_ses-{session_num}_{channel_name}_spectrogram.png"
    
    # === Save plot ===
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, filename)
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"✅ Spectrogram saved to: {save_path}")
    print(f"📊 Processed {total_epochs_processed} epochs ({total_epochs_processed * epoch_duration / 3600:.1f} hours of data)")

except Exception as e:
    print(f"❌ Error processing EDF file: {e}")
    import traceback
    traceback.print_exc()
