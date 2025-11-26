import numpy as np
import h5py

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
