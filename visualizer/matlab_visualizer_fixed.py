import scipy.io
import numpy as np

# Load MATLAB .mat file using scipy.io (handles older MATLAB formats)
try:
    mat_data = scipy.io.loadmat("results_NR_YAC_1.mat")
    print("Available variables in the .mat file:")
    print(list(mat_data.keys()))
    
    # Filter out MATLAB metadata keys (usually start with '__')
    data_keys = [key for key in mat_data.keys() if not key.startswith('__')]
    print(f"\nData variables: {data_keys}")
    
    # Access EEG data if it exists
    if 'EEG' in mat_data:
        eeg = mat_data['EEG']
        print(f"\nEEG data shape: {eeg.shape}")
        print(f"EEG data type: {eeg.dtype}")
        print(f"EEG sample values: {eeg.flat[:5]}")  # First 5 values
        
    # Show info about all data variables
    for key in data_keys:
        data = mat_data[key]
        print(f"\n{key}:")
        print(f"  Shape: {data.shape}")
        print(f"  Type: {data.dtype}")
        if data.size < 10:  # Only show values for small arrays
            print(f"  Values: {data}")
        else:
            print(f"  Sample values: {data.flat[:5]}")
            
except FileNotFoundError:
    print("File 'results_NR_YAC_1.mat' not found in current directory")
    print("Available .mat files:")
    import os
    mat_files = [f for f in os.listdir('.') if f.endswith('.mat')]
    if mat_files:
        for f in mat_files:
            print(f"  - {f}")
    else:
        print("  No .mat files found")
except Exception as e:
    print(f"Error reading .mat file: {e}")
    print("This might be a newer MATLAB format. Try using h5py for MATLAB v7.3+ files.")
