import os
import numpy as np
import pandas as pd
import mne

def check_eeg_units():
    """Check the actual units of EEG data by examining standard deviation"""
    
    # Check if bdsp-bids directory exists
    if not os.path.exists('./bdsp-bids'):
        print("bdsp-bids directory not found. Please run the main script first to download data.")
        return
    
    print("Checking EEG units across available subjects...")
    print("=" * 60)
    
    for root, dirs, files in os.walk('./bdsp-bids'):
        if 'eeg' in root and any(f.endswith('.edf') for f in files):
            # Extract subject ID from path
            path_parts = root.split('/')
            if 'sub-' in root:
                sub_idx = [i for i, part in enumerate(path_parts) if part.startswith('sub-')][0]
                sid = path_parts[sub_idx].replace('sub-', '')
                ses_idx = [i for i, part in enumerate(path_parts) if part.startswith('ses-')][0]
                ses = path_parts[ses_idx].replace('ses-', '')
                
                # Find EDF file
                edf_file = None
                for f in files:
                    if f.endswith('.edf'):
                        edf_file = os.path.join(root, f)
                        break
                
                if edf_file:
                    try:
                        print(f"\nSubject: {sid}, Session: {ses}")
                        print(f"EDF: {os.path.basename(edf_file)}")
                        
                        # Load raw data
                        raw = mne.io.read_raw_edf(edf_file, preload=False, verbose=False)
                        
                        # Check available channels
                        print(f"Available channels: {raw.ch_names}")
                        
                        # Check C3-M2 if available, otherwise C3
                        if 'C3-M2' in raw.ch_names:
                            raw.pick_channels(['C3-M2'])
                            channel_name = 'C3-M2'
                        elif 'C3' in raw.ch_names:
                            raw.pick_channels(['C3'])
                            channel_name = 'C3'
                        else:
                            print("  No C3-M2 or C3 channel found")
                            continue
                        
                        # Load data and compute statistics
                        raw.load_data()
                        data = raw.get_data()[0]
                        
                        std_val = np.std(data)
                        mean_val = np.mean(data)
                        min_val = np.min(data)
                        max_val = np.max(data)
                        
                        print(f"  Channel: {channel_name}")
                        print(f"  Std: {std_val:.4f}")
                        print(f"  Mean: {mean_val:.4f}")
                        print(f"  Range: [{min_val:.4f}, {max_val:.4f}]")
                        
                        # Interpret units
                        if std_val > 100:
                            print(f"  → Data appears to be in VOLTS (V)")
                            print(f"  → Convert to μV by multiplying by 1e6")
                        elif 0.1 < std_val <= 100:
                            print(f"  → Data appears to be in MILLIVOLTS (mV)")
                            print(f"  → Convert to μV by multiplying by 1e3")
                        else:
                            print(f"  → Data appears to be in MICROVOLTS (μV) - correct units!")
                        
                    except Exception as e:
                        print(f"  Error processing {edf_file}: {e}")
                    
                    # Only process first few subjects to avoid long runtime
                    if sid in ['I0003175075972', 'I0003175076780', 'I0003175173838']:
                        break

if __name__ == '__main__':
    check_eeg_units() 