from pytest import raises, warns
from bidso.find import find_in_bids, find_root, _generate_pattern

from .paths import BIDS_PATH, task_ieeg

filename = task_ieeg.get_filename(BIDS_PATH)


def test_find_root():
    assert find_root(filename).name == 'bids'
    assert find_root(filename, target='subject').name == 'sub-bert'
    assert find_root(filename, target='session').name == 'ses-day02'


def test_find_in_bids_01():

    found = find_in_bids(filename, subject='bert', session='day01', run='1',
                         extension='.nii.gz', upwards=True)
    assert found.name == 'sub-bert_ses-day01_task-block_run-1_bold.nii.gz'

    with warns(UserWarning):
        find_in_bids(filename, subject='bert', useless='xxx', task='block',
                     modality='channels', upwards=True)


def test_find_in_bids_02():

    with raises(FileNotFoundError):
        find_in_bids(filename, upwards=True, subject='xxx')


def test_find_in_bids_03():

    with raises(FileNotFoundError):
        find_in_bids(filename, upwards=True, subject='bert')


def test_find_in_bids_04():
    assert sum(1 for x in find_in_bids(BIDS_PATH, generator=True, subject='bert')) == 12


def test_find_in_bids_05():
    with raises(FileNotFoundError):
        find_in_bids(BIDS_PATH, subject='xxx')

    with raises(StopIteration):
        next(find_in_bids(BIDS_PATH, subject='xxx', generator=True))


def test_find_in_bids_06():
    with raises(ValueError):
        find_in_bids(BIDS_PATH, upwards=True, generator=True)


def test_generate_pattern():
    assert _generate_pattern(True, dict(subject='test')) == 'sub-test_*.*'
    assert _generate_pattern(False, dict(subject='test')) == 'sub-test.*'

    assert _generate_pattern(True, dict(subject='test', session='sess')) == 'sub-test_ses-sess_*.*'
    assert _generate_pattern(True, dict(subject='test', modality='mod')) == 'sub-test_*_mod.*'
    assert _generate_pattern(True, dict(session='sess', extension='.nii.gz')) == '*_ses-sess_*.nii.gz'
    assert _generate_pattern(True, dict(modality='mod', extension='.nii.gz')) == '*_mod.nii.gz'


def test_wildcard_subject():
    with raises(ValueError):
        _generate_pattern(False, dict())
