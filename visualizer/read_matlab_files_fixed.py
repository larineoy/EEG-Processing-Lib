import os
import numpy as np
import scipy.io
import data_loading_helpers as dh

def analyze_matlab_file(file_path):
    """Analyze a MATLAB .mat file and extract available data"""
    print(f"Analyzing: {file_path}")
    print("=" * 50)
    
    try:
        # Load the MATLAB file
        mat_data = scipy.io.loadmat(file_path)
        
        # Show all available variables
        print("Available variables:")
        for key in mat_data.keys():
            if not key.startswith('__'):
                print(f"  - {key}")
        
        # Analyze each variable
        for key, data in mat_data.items():
            if not key.startswith('__'):
                print(f"\n{key}:")
                print(f"  Type: {type(data)}")
                print(f"  Shape: {data.shape if hasattr(data, 'shape') else 'N/A'}")
                
                # If it's a structured array, show its fields
                if hasattr(data, 'dtype') and data.dtype.names:
                    print(f"  Fields: {data.dtype.names}")
                    for field in data.dtype.names:
                        field_data = data[field]
                        print(f"    {field}: {field_data}")
                
                # If it's a regular array, show sample values
                elif hasattr(data, 'flat') and data.size > 0:
                    if data.size <= 10:
                        print(f"  Values: {data}")
                    else:
                        print(f"  Sample values: {data.flat[:5]}")
        
        return mat_data
        
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
    mat_data = analyze_matlab_file(file_path)
    
    if mat_data is None:
        return
    
    # Try to extract meaningful data
    print("\n" + "=" * 50)
    print("EXTRACTING MEANINGFUL DATA:")
    print("=" * 50)
    
    # Extract parameters
    if 'par' in mat_data:
        par = mat_data['par']
        print(f"\nParameters extracted: {par.dtype.names}")
        
        # Try to get subject ID
        if 'subjectID' in par.dtype.names:
            subject_id = par['subjectID'][0, 0]
            print(f"Subject ID: {subject_id}")
    
    # Extract answers
    if 'answers' in mat_data:
        answers = mat_data['answers']
        print(f"\nAnswers shape: {answers.shape}")
        print(f"Answers: {answers}")
    
    # Extract break data
    if 'nBreaks_all' in mat_data:
        breaks = mat_data['nBreaks_all']
        print(f"\nBreak data shape: {breaks.shape}")
        print(f"Break data: {breaks}")

if __name__ == "__main__":
    main()
