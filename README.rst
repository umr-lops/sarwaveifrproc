==============
sarwaveifrproc
==============


.. image:: https://img.shields.io/pypi/v/sarwaveifrproc.svg
        :target: https://pypi.python.org/pypi/sarwaveifrproc


.. image:: https://readthedocs.org/projects/sarwaveifrproc/badge/?version=latest
        :target: https://sarwaveifrproc.readthedocs.io/en/latest/?version=latest
        :alt: Documentation Status


.. image:: https://badge.fury.io/py/sarwaveifrproc.svg
     :target: https://badge.fury.io/py/sarwaveifrproc
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

This Sentinel-1 Level-2 sea state processor is developed/maintained by `Ifremer - LOPS laboratory`_. This work is co-funded by ESA through the SARWAVE project (https://www.sarwave.org/).
The processor development benefits from support and contributions from Sentinel-1 Mission Performance Cluster team (https://sar-mpc.eu/about/activities-and-team/).

.. _Ifremer - LOPS laboratory: https://www.umr-lops.fr/