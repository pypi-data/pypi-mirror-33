from bidso import Task

from sanajeh import simulate_all

from .paths import BIDS_PATH, task_fmri


def test_read_fmri():
    simulate_all(BIDS_PATH)
    Task(task_fmri.get_filename(BIDS_PATH))
