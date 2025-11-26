import os
import numpy as np
import pandas as pd
import subprocess
import shutil
from tqdm import tqdm
from scipy.signal import welch
import mne

def load_sleep_stages_from_csv(csv_path):
    df = pd.read_csv(csv_path)
    stage_map = {
        'WAKE': 5,
        'W': 5,
        'REM': 4,
        'N1': 3,
        'N2': 3,
        'N3': 3,
        'N4': 3,
        'UNSCORED': -1  # Ignored later if needed
    }
    sleep_stages = df['sleep_stage'].map(stage_map).values
    return sleep_stages

def compute_spectrogram(raw, sfreq, epoch_length=30, n_fft=512):
    data = raw.get_data(picks='eeg')
    n_channels, n_samples = data.shape
    samples_per_epoch = int(sfreq * epoch_length)
    n_epochs = n_samples // samples_per_epoch

    if n_epochs <= 0 or n_channels == 0:
        return np.empty((0, 0, 0)), np.array([])

    spec = []
    freqs = None

    for i in range(n_epochs):
        epoch_data = data[:, i * samples_per_epoch:(i + 1) * samples_per_epoch]
        psds = []
        # Choose Welch params based on sfreq and epoch length; ensure ints and valid sizes
        nperseg = int(min(sfreq * 2, epoch_data.shape[1]))
        # Ensure at least 2 to avoid scipy errors, and clamp to n_fft
        nperseg = max(min(nperseg, int(n_fft)), 2)
        noverlap = int(min(sfreq, nperseg // 2))
        for ch_data in epoch_data:
            f, p = welch(ch_data, fs=float(sfreq), nperseg=nperseg, noverlap=noverlap, nfft=int(n_fft))
            psds.append(p)
        psds = np.stack(psds, axis=0)
        spec.append(psds)
        if freqs is None:
            freqs = f

    spec = np.stack(spec, axis=0)
    return spec, freqs

def get_band_power(spec, freq, sleep_stages, channel_names):
    if freq is None or len(freq) < 2:
        return {}
    dfreq = freq[1] - freq[0]

    stages = {'NREM': 3, 'REM': 4, 'W': 5}
    bands = {
        'slow': (0, 1),
        'delta': (1, 4),
        'theta': (4, 8),
        'alpha': (8, 12),
        'sigma': (12, 15),
        'beta': (15, 30)
    }

    feat = {}
    for band_name, (f_low, f_high) in bands.items():
        freq_ids = (freq >= f_low) & (freq < f_high)
        for stage_name, stage_id in stages.items():
            stage_ids = (sleep_stages == stage_id)
            if not np.any(stage_ids):
                continue
            for ch_id, ch in enumerate(channel_names):
                if ch_id >= spec.shape[1]:
                    break
                this_spec = spec[stage_ids, ch_id][:, freq_ids]
                band_power = (this_spec * dfreq).sum(axis=-1)
                bp = np.nanmean(band_power)
                key = f'BP_{band_name}_{stage_name}_{ch}'
                feat[key] = bp
    return feat

def main():
    metadata_path = '/Users/larineouyang/psg-metadata/dataset_BCH_sleep.xlsx'
    meta = pd.read_excel(metadata_path).copy()
    meta['SID'] = meta.apply(
        lambda row: f"I{str(row['SiteID'])[1:]}{int(row['BDSPPatientID'])}", axis=1
    )

    all_feats = []

    for _, row in tqdm(meta.iterrows(), total=len(meta)):
        site = row['SiteID']
        sid = row['SID']
        local_dir = f'./bdsp-bids/{site}/sub-{sid}/'
        os.makedirs(local_dir, exist_ok=True)

        # Check if data already exists locally
        local_eeg = []
        local_annot = None
        for root, _, files in os.walk(local_dir):
            for file in files:
                if file.endswith('.edf'):
                    local_eeg.append(os.path.join(root, file))
                elif file.endswith('sleepannotations.csv'):
                    local_annot = os.path.join(root, file)

        downloaded = False
        if not local_eeg or local_annot is None:
            aws_cmd = (
                f"aws s3 cp "
                f"s3://arn:aws:s3:us-east-1:184438910517:accesspoint/bdsp-psg-access-point/"
                f"PSG/bids/{site}/sub-{sid}/ "
                f"{local_dir} --recursive --region us-east-1"
            )
            subprocess.run(aws_cmd, shell=True)
            print(f"{sid}: Downloaded data from AWS to {local_dir}")
            downloaded = True

        try:
            eeg_files = []
            annot_csv = None
            for root, _, files in os.walk(local_dir):
                for file in files:
                    if file.endswith('.edf'):
                        eeg_files.append(os.path.join(root, file))
                    elif file.endswith('sleepannotations.csv'):
                        annot_csv = os.path.join(root, file)

            if not eeg_files or annot_csv is None:
                print(f"Missing files for {sid}")
                if downloaded:
                    shutil.rmtree(local_dir, ignore_errors=True)
                continue

            raw = mne.io.read_raw_edf(eeg_files[0], preload=True, verbose=False)
            raw.pick_types(eeg=True)

            # IMPORTANT: Multiply signal by 10^6 BEFORE filtering as instructed by manager/leader
            # This converts from μV to a different scale (likely pV or similar)
            raw._data = raw._data * 1e6
            print(f"{sid}: Applied 10^6 scaling before filtering (μV → pV scale)")

            # Keep only standard scalp EEG channels to avoid montage errors
            desired_names = ['F3', 'F4', 'C3', 'C4', 'O1', 'O2']
            picks = [ch for ch in desired_names if ch in raw.ch_names]
            if len(picks) == 0:
                print(f"No desired EEG channels found for {sid}")
                if downloaded:
                    shutil.rmtree(local_dir, ignore_errors=True)
                continue
            raw.pick_channels(picks, ordered=True)

            # Set montage but ignore missing channels (non-EEG were already dropped)
            raw.set_montage('standard_1020', on_missing='ignore', verbose=False)

            spec, freqs = compute_spectrogram(raw, raw.info['sfreq'])
            if spec.size == 0:
                print(f"No epochs or EEG channels for {sid}")
                if downloaded:
                    shutil.rmtree(local_dir, ignore_errors=True)
                continue

            sleep_stages = load_sleep_stages_from_csv(annot_csv)
            # Align lengths between spec epochs and annotations
            min_len = min(spec.shape[0], len(sleep_stages))
            if min_len == 0:
                print(f"No overlapping epochs and annotations for {sid}")
                if downloaded:
                    shutil.rmtree(local_dir, ignore_errors=True)
                continue
            spec = spec[:min_len]
            sleep_stages = sleep_stages[:min_len]

            feat = get_band_power(spec, freqs, sleep_stages, channel_names=raw.ch_names)
            feat['SID'] = sid
            all_feats.append(feat)

        except Exception as e:
            print(f"Error processing {sid}: {e}")
        finally:
            if downloaded:
                print(f"{sid}: Deleting temporary folder {local_dir}")
                shutil.rmtree(local_dir, ignore_errors=True)

    df = pd.DataFrame(all_feats)
    df.to_csv('bandpower_features_scaled_all.csv', index=False)
    print("Saved bandpower_features_scaled.csv (with 10^6 scaling applied)")

if __name__ == '__main__':
    main() 