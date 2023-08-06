from pathlib import Path
from bidso import file_Core


TEST_PATH = Path(__file__).resolve().parent
DATA_PATH = TEST_PATH / 'data'
BIDS_PATH = DATA_PATH / 'bids'
BIDS_PATH.mkdir(parents=True, exist_ok=True)
DERIVATIVES_PATH = DATA_PATH / 'derivatives'
FREESURFER_PATH = DERIVATIVES_PATH / 'freesurfer'

subject = 'bert'
task_ieeg = file_Core(
    subject=subject,
    session='day02',
    modality='ieeg',
    task='block',
    run='1',
    acquisition='clinical',
    extension='.eeg',
    )
task_fmri = file_Core(
    subject=subject,
    session='day01',
    modality='bold',
    task='block',
    run='1',
    extension='.nii.gz',
    )
task_anat = file_Core(
    subject=subject,
    session='day01',
    modality='T1w',
    extension='.nii.gz',
    )
elec_ct = file_Core(
    subject=subject,
    session='day02',
    modality='electrodes',
    acquisition='ct',
    extension='.tsv',
    )


T1_PATH = FREESURFER_PATH / 'sub-bert/mri/T1.mgz'
