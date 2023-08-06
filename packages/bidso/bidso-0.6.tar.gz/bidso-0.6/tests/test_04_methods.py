from bidso.files import file_Tsv
from bidso import Electrodes
from .paths import elec_ct, BIDS_PATH


def test_file_Tsv_get():

    tsv = file_Tsv(elec_ct.get_filename(BIDS_PATH))

    assert tsv.get(lambda x: x['name'] == 'grid01')[0]['name'] == 'grid01'
    assert tsv.get(None, lambda x: x['name'])[0] == 'grid01'


def test_Electrodes_get_xyz():
    elec = Electrodes(elec_ct.get_filename(BIDS_PATH))

    assert len(elec.get_xyz()) == 28
    assert len(elec.get_xyz(['grid01', ])) == 1
