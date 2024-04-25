import pytest
import os
from sarwaveifrproc.utils import get_output_filename,get_output_safe

inputs_l1slc = [
    "/tmp/2022/127/S1A_IW_XSP__1SDV_20220507T162437_20220507T162504_043107_0525DE_B14E_A02.SAFE/l1b-s1a-iw1-xsp-vv-20220507t162439-20220507t162504-043107-0525de-004-a02.nc",
    "/tmp/2022/127/S1A_IW_XSP__1SDV_20220507T162437_20220507T162504_043107_0525DE_B14E_A02.SAFE/l1b-s1a-iw1-xsp-vv-20220507t162439-20220507t162504-043107-0525de-004_a02.nc",
    "/tmp/2022/127/S1A_IW_XSP__1SDV_20220507T162437_20220507T162504_043107_0525DE_B14E_B02.SAFE/l1c-s1a-iw1-xsp-vv-20220507t162439-20220507t162504-043107-0525de-004_b02.nc",
    "/tmp/2022/127/S1A_IW_XSP__1SDV_20220507T162437_20220507T162504_043107_0525DE_B14E.SAFE/l1c-s1a-iw1-xsp-vv-20220507t162439-20220507t162504-043107-0525de-004_b02.nc"
]
expected_l2wav = [
    '/tmp/2022/127/S1A_IW_WAV__2SDV_20220507T162437_20220507T162504_043107_0525DE_B14E_E03.SAFE/l2-s1a-iw1-wav-dv-20220507t162439-20220507t162504-043107-0525de-e03.nc'
]


@pytest.mark.parametrize(
    ["l1b_fullpath", "expected_l2wav"],
    (
        pytest.param(inputs_l1slc[0], expected_l2wav[0]),
        pytest.param(inputs_l1slc[1], expected_l2wav[0]),
        pytest.param(inputs_l1slc[2], expected_l2wav[0]),
        pytest.param(inputs_l1slc[3], expected_l2wav[0]),
    ),
)
def test_outputfile_path(l1b_fullpath, expected_l2wav):
    version = "E03"
    outputdir = "/tmp/"
    output_safe = get_output_safe(l1x_safe=os.path.dirname(l1b_fullpath),root_savepath=outputdir,tail=version)
    l2_full_path = get_output_filename(l1b_fullpath, output_safe, tail=version)

    print(l2_full_path)
    assert l2_full_path == expected_l2wav
