from pytest import raises
from bidso import file_Core
from .paths import BIDS_PATH, elec_ct


def test_create_file_Core():
    core = file_Core(subject='a', session='b')
    assert core.subject == 'a'
    assert core.run is None

    with raises(AttributeError):
        core = file_Core(weird='a')


def test_get_filename():
    core = file_Core(
        subject='bert',
        session='day02',
        task='block',
        run='00',
        acquisition='ct',
        modality='ieeg')
    expected = 'sub-bert_ses-day02_task-block_run-00_acq-ct_ieeg'
    assert core.get_filename() == expected
    assert core.get_filename(BIDS_PATH).name == expected
    assert str(core.get_filename(BIDS_PATH).relative_to(BIDS_PATH).parent) == 'sub-bert/ses-day02/ieeg'

    assert core.get_filename(BIDS_PATH).parent.name == 'ieeg'
    assert core.get_filename(BIDS_PATH, 'xxx').parent.name == 'xxx'


def test_get_filename_modality():
    core = file_Core(
        subject='bert',
        session='day02',
        task='block',
        run='00',
        acquisition='ct',
        modality='ieeg')

    assert core.get_filename(BIDS_PATH).parent.name == 'ieeg'
    assert core.get_filename(BIDS_PATH, 'xxx').parent.name == 'xxx'


def test_elec_filename():
    assert elec_ct.get_filename() == 'sub-bert_ses-day02_acq-ct_electrodes.tsv'
