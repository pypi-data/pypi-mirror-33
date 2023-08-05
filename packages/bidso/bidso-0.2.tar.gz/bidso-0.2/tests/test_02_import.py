from bidso import (Task,
                   iEEG,
                   )
from bidso.utils import bids_mkdir
from bidso.directories import (dir_Root,
                               dir_Session,
                               )

from .paths import BIDS_PATH, task_fmri, task_ieeg


def test_directories_xxx():
    dir_Root(BIDS_PATH)

    dir_Session(bids_mkdir(BIDS_PATH, task_fmri))


def test_objects_xxx():
    Task(task_fmri.get_filename(BIDS_PATH))
    ieeg = iEEG(task_ieeg.get_filename(BIDS_PATH))
    ieeg.read_electrodes()
    assert len(ieeg.electrodes.electrodes.tsv) == 28
