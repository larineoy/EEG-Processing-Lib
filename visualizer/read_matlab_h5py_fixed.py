import os
import numpy as np
import h5py

def explore_h5py_structure(group, level=0):
    """Recursively explore HDF5 structure"""
    indent = "  " * level
    
    for key in group.keys():
        item = group[key]
        print(f"{indent}{key}: {type(item).__name__}")
        
        if isinstance(item, h5py.Group):
            print(f"{indent}  (Group with {len(item.keys())} items)")
            if level < 2:  # Limit depth to avoid too much output
                explore_h5py_structure(item, level + 1)
        elif isinstance(item, h5py.Dataset):
            print(f"{indent}  Shape: {item.shape}, Dtype: {item.dtype}")
            if item.size > 0 and item.size < 20:  # Show small datasets
                try:
                    data = item[()]
                    print(f"{indent}  Values: {data}")
                except:
                    print(f"{indent}  (Could not read data)")
            elif item.size > 0:
                try:
                    data = item[()]
                    if hasattr(data, 'flat'):
                        print(f"{indent}  Sample: {data.flat[:5]}")
                    else:
                        print(f"{indent}  Sample: {data.ravel()[:5]}")
                except:
                    print(f"{indent}  (Could not read data)")
        elif isinstance(item, h5py.Reference):
            print(f"{indent}  (Reference)")

def load_matlab_string(f, ref):
    """Load a MATLAB string from HDF5 reference"""
    if isinstance(ref, h5py.Reference):
        return f[ref][()].tobytes().decode('utf-8')
    else:
        return str(ref)

def extract_word_level_data(f, word_ref):
    """Extract word-level data from MATLAB structure"""
    word_data = []
    
    if isinstance(word_ref, h5py.Reference):
        word_group = f[word_ref]
        
        # Try to extract common word-level features
        features = ['FFD', 'ALPHA_EEG', 'word', 'duration', 'frequency']
        
        for i in range(len(word_group)):
            word_info = {}
            for feature in features:
                if feature in word_group:
                    try:
                        if isinstance(word_group[feature][i], h5py.Reference):
                            word_info[feature] = f[word_group[feature][i]][()]
                        else:
                            word_info[feature] = word_group[feature][i]
                    except:
                        word_info[feature] = None
            word_data.append(word_info)
    
    return word_data

def analyze_matlab_h5py(file_path):
    """Analyze a MATLAB v7.3 .mat file using h5py"""
    print(f"Analyzing: {file_path}")
    print("=" * 50)
    
    try:
        with h5py.File(file_path, 'r') as f:
            print("File structure:")
            explore_h5py_structure(f)
            
            print("\n" + "=" * 50)
            print("EXTRACTING DATA:")
            print("=" * 50)
            
            # Look for common MATLAB variables
            for key in f.keys():
                if not key.startswith('#'):  # Skip MATLAB metadata
                    print(f"\n{key}:")
                    item = f[key]
                    
                    if isinstance(item, h5py.Group):
                        print(f"  Group with {len(item.keys())} items:")
                        for subkey in list(item.keys())[:10]:  # Limit to first 10 items
                            subitem = item[subkey]
                            if isinstance(subitem, h5py.Dataset):
                                print(f"    {subkey}: {subitem.shape} {subitem.dtype}")
                                if subitem.size > 0 and subitem.size < 10:
                                    try:
                                        data = subitem[()]
                                        print(f"      Values: {data}")
                                    except:
                                        print(f"      (Could not read data)")
                            else:
                                print(f"    {subkey}: {type(subitem).__name__}")
                    
                    elif isinstance(item, h5py.Dataset):
                        print(f"  Dataset: {item.shape} {item.dtype}")
                        if item.size > 0 and item.size < 20:
                            try:
                                data = item[()]
                                print(f"    Values: {data}")
                            except:
                                print(f"    (Could not read data)")
                        elif item.size > 0:
                            try:
                                data = item[()]
                                if hasattr(data, 'flat'):
                                    print(f"    Sample: {data.flat[:5]}")
                                else:
                                    print(f"    Sample: {data.ravel()[:5]}")
                            except:
                                print(f"    (Could not read data)")
            
            return f
            
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

def main():
    # Check if the file exists
    file_path = "resultsYAC_NR.mat"
    
    if not os.path.exists(file_path):
        print(f"File {file_path} not found!")
        print("Available .mat files:")
        for f in os.listdir('.'):
            if f.endswith('.mat'):
                print(f"  - {f}")
        return
    
    # Analyze the file
    analyze_matlab_h5py(file_path)

if __name__ == "__main__":
    main()
