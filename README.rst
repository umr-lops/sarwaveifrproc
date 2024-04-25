==============
sarwaveifrproc
==============


.. image:: https://img.shields.io/pypi/v/sarwaveifrproc.svg
        :target: https://pypi.python.org/pypi/sarwaveifrproc

.. image:: https://img.shields.io/travis/agrouaze/sarwaveifrproc.svg
        :target: https://travis-ci.com/agrouaze/sarwaveifrproc

.. image:: https://readthedocs.org/projects/sarwaveifrproc/badge/?version=latest
        :target: https://sarwaveifrproc.readthedocs.io/en/latest/?version=latest
        :alt: Documentation Status


.. image:: https://pyup.io/repos/github/agrouaze/sarwaveifrproc/shield.svg
     :target: https://pyup.io/repos/github/agrouaze/sarwaveifrproc/
     :alt: Updates



SAR Sentinel-1 ESA mission sea state Ifremer processor


* Free software: MIT license
* Documentation: https://sarwaveifrproc.readthedocs.io.


Features
--------

 * predicts sea state geophysical quantities from Level-1B or Level-1C Ifremer SARWAVE Sentinel-1 (WV,IW,EW) products using empirical function learnt on numerical hindcasts (WAVEWATCH III):
  - significant wave height (`Hs`)
  - mean wave period (`t0m1`)
  - significant wave height of the wind-sea (`pshs0`)
 * save results in a netCDF file per sub-swath.

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
