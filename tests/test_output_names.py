import pytest
from xsarslc.tools import get_output_l1b_filepath

inputs_l1slc = [
    "/tmp/data/sentinel1/S1A_IW_SLC__1SDV_20220507T162437_20220507T162504_043107_0525DE_B14E.SAFE/measurement/s1a-iw1-slc-vv-20220507t162439-20220507t162504-043107-0525de-004.tiff",
]
expected_l1b = [
    '/tmp/2022/127/S1A_IW_XSP__1SDV_20220507T162437_20220507T162504_043107_0525DE_B14E_A02.SAFE/l1b-s1a-iw1-xsp-vv-20220507t162439-20220507t162504-043107-0525de-004_a02.nc'
]


@pytest.mark.parametrize(
    ["l1slc_fullpath", "expected_l1b"],
    (
        pytest.param(inputs_l1slc[0], expected_l1b[0]),
        #pytest.param(inputs_l1slc[1], expected_l1b[0]),
    ),
)
def test_outputfile_path(l1slc_fullpath, expected_l1b):
    version = "A02"
    outputdir = "/tmp/"
    l1b_full_path = get_output_l1b_filepath(
        l1slc_fullpath, version=version, outputdir=outputdir
    )

    print(l1b_full_path)
    assert l1b_full_path == expected_l1b
