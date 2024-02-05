.. _productdescription:

****************************************
Level-1B SAR IFREMER Product Description
****************************************

This page stands as a Product Description document for Sentinel-1 L1B IFREMER product.

It describes the format, the files and the content of Level-1B SAR product.

Product philosophy
##################


The Level-1B Sentinel-1 IFREMER product is designed to be a SAR expert product. The rationales behind the dimensions and coordinates that are showing the tiling of the SAR image in slice / sub-swath / burst / tiles are:

    The willing to stay close to image geometry to be able to easily swap from image domain to geo-referenced spectral domain

    The willing to stay close to ESA Sentinel-1 SLC product format.

The limited number of variables (only geometry, radar and radar-derived variables) is also a strategy to limit the volume of the products and keep simple the first L1 -> L1B processing which is also the most greedy processing in terms of processing-time and memory-usage.

L1B Level-1B Sentinel-1 IFREMER product has been designed to ease the work on the inversion from cross-spectrum coming from intra-burst and inter-burst (overlapping) part of the SLC products.

The current version of the product is still prototype, and future evolution are expected depending on feedbacks from partners. The configurations of the tiles, periodograms, looks is tuneable and furthers tests will help to choose the proper set of parameters for wind and wave applications.

Product structure
#################

Each product is stored in a .SAFE directory. The SAFE convention is inherited from Sentinel-1 mission. Except that the SLC (single look complex) acronym has been replaced by XSP (for cross-spectrum which is the most important variable in this dataset).

.. image:: ./figures/L1_naming_conventions.png
   :width: 650px
   :height: 500px
   :scale: 110 %
   :alt: safe-naming
   :align: center



Each .SAFE directory contains 3 or 6 netCDF files, one per polarization (could be single polarization HH/VV or dual polarization HH/HV - VV/VH) plus one per sub-swath, following the storage of official ESA SLC products. All the polarizations are processed from Level-1 to Level-1B even though VV is the classical candidate polarization for wave inversion.


The netCDF files naming convention is adapted from ESA Sentinel-1:


.. image:: ./figures/Sentinel-1-SAR-User-Guide-Product-Formatting-Figure-2.jpg
   :width: 800px
   :height: 400px
   :scale: 90 %
   :alt: file-naming
   :align: center


Example of L1B filename:

s1a-iw1-slc-hv-20220309t083923-20220309t083948-042242-0508e1-004_L1B_xspec_IFR_1.4k.nc

Extra part gives the processing level, IFR stands for IFREMER and "1.4k" is the ID of the processing.

Typical size for a IW SLC processed at 17.7 km² tile width is about 75 Mo per L1B .nc file .

Product variables
#################


Exhaustive content
------------------

Each netCDF files is split into 2 groups:

     - **intraburst**: region (i.e. SAR time span) of SLC bursts in which Ocean/Land surface have been seen only one time.

     - **interburst**: region (i.e. SAR time span) of SLC bursts for which the Ocean/Land surface have been observed twice thanks to antenna steering in azimuth.

Each of the group contains the same set of variables with minor exceptions*.

The variables of **intraburst** group:

.. raw:: html

 <details>
 <summary><a>exhaustive list of the variables available in Level-1B SAR IFREMER</a></summary>

.. code-block::

  group: intraburst {
  dimensions:
        tile_line = 10 ;
        tile_sample = 4 ;
        bt_thresh = 5 ;
        freq_sample = 403 ;
        freq_line = 50 ;
        \0tau = 3 ;
        \1tau = 2 ;
        \2tau = 1 ;
        c_sample = 2 ;
        c_line = 2 ;
        k_gp = 4 ;
        phi_hf = 5 ;
        lambda_range_max_macs = 10 ;


.. code-block:: python

 variables:
        float incidence(tile_line, tile_sample) ;
                incidence:_FillValue = NaNf ;
                incidence:long_name = "incidence at tile middle" ;
                incidence:units = "degree" ;
                incidence:coordinates = "latitude line longitude pol sample" ;
        float ground_heading(tile_line, tile_sample) ;
                ground_heading:_FillValue = NaNf ;
                ground_heading:long_name = "ground heading" ;
                ground_heading:units = "degree" ;
                ground_heading:convention = "from North clockwise" ;
                ground_heading:coordinates = "latitude line longitude pol sample" ;
        string pol ;
        short burst(tile_line) ;
                burst:coordinates = "line pol" ;
        int64 sensing_time(tile_line, tile_sample) ;
                sensing_time:long_name = "tile sensing time" ;
                sensing_time:coordinates = "latitude line longitude pol sample" ;
                sensing_time:units = "microseconds since 2021-04-18 21:22:25.142172" ;
                sensing_time:calendar = "proleptic_gregorian" ;
        float sigma0(tile_line, tile_sample) ;
                sigma0:_FillValue = NaNf ;
                sigma0:long_name = "RAW calibrated sigma0" ;
                sigma0:units = "linear" ;
                sigma0:coordinates = "latitude line longitude pol sample" ;
        float nesz(tile_line, tile_sample) ;
                nesz:_FillValue = NaNf ;
                nesz:long_name = "RAW noise-equivalent sigma zero" ;
                nesz:units = "linear" ;
                nesz:coordinates = "latitude line longitude pol sample" ;
        short bt_thresh(bt_thresh) ;
                bt_thresh:long_name = "lower edge of bright target to background amplitude ratio" ;
        short bright_targets_histogram(tile_line, tile_sample, bt_thresh) ;
                bright_targets_histogram:long_name = "bright targets histogram" ;
                bright_targets_histogram:coordinates = "latitude line longitude pol sample" ;
        float sigma0_filt(tile_line, tile_sample) ;
                sigma0_filt:_FillValue = NaNf ;
                sigma0_filt:long_name = "calibrated sigma0 with BT correction" ;
                sigma0_filt:units = "linear" ;
                sigma0_filt:coordinates = "latitude line longitude pol sample" ;
        float normalized_variance_filt(tile_line, tile_sample) ;
                normalized_variance_filt:_FillValue = NaNf ;
                normalized_variance_filt:long_name = "normalized variance with BT correction" ;
                normalized_variance_filt:units = "" ;
                normalized_variance_filt:coordinates = "latitude line longitude pol sample" ;
        float doppler_centroid(tile_line, tile_sample) ;
                doppler_centroid:_FillValue = NaNf ;
                doppler_centroid:units = "rad/m" ;
                doppler_centroid:averaged_periodograms = 81LL ;
                doppler_centroid:periodo_width_sample = 3540LL ;
                doppler_centroid:periodo_overlap_sample = 1770LL ;
                doppler_centroid:periodo_overlap_line = 1770LL ;
                doppler_centroid:coordinates = "latitude line longitude pol sample" ;
        float k_rg(tile_line, tile_sample, freq_sample) ;
                k_rg:_FillValue = NaNf ;
                k_rg:long_name = "wavenumber in range direction" ;
                k_rg:units = "rad/m" ;
        float k_az(freq_line) ;
                k_az:_FillValue = NaNf ;
                k_az:long_name = "wavenumber in azimuth direction" ;
                k_az:units = "rad/m" ;
                k_az:spacing = 0.00179264256685252 ;
        float var_xspectra_0tau(tile_line, tile_sample, freq_line, freq_sample, \0tau) ;
                var_xspectra_0tau:_FillValue = NaNf ;
                var_xspectra_0tau:averaged_periodograms = 81LL ;
                var_xspectra_0tau:periodo_width_sample = 3540LL ;
                var_xspectra_0tau:periodo_width_line = 3540LL ;
                var_xspectra_0tau:periodo_overlap_sample = 1770LL ;
                var_xspectra_0tau:periodo_overlap_line = 1770LL ;
                var_xspectra_0tau:coordinates = "k_az k_rg latitude line longitude pol sample" ;
        float var_xspectra_1tau(tile_line, tile_sample, freq_line, freq_sample, \1tau) ;
                var_xspectra_1tau:_FillValue = NaNf ;
                var_xspectra_1tau:averaged_periodograms = 81LL ;
                var_xspectra_1tau:periodo_width_sample = 3540LL ;
                var_xspectra_1tau:periodo_width_line = 3540LL ;
                var_xspectra_1tau:periodo_overlap_sample = 1770LL ;
                var_xspectra_1tau:periodo_overlap_line = 1770LL ;
                var_xspectra_1tau:coordinates = "k_az k_rg latitude line longitude pol sample" ;
        float var_xspectra_2tau(tile_line, tile_sample, freq_line, freq_sample, \2tau) ;
                var_xspectra_2tau:_FillValue = NaNf ;
                var_xspectra_2tau:averaged_periodograms = 81LL ;
                var_xspectra_2tau:periodo_width_sample = 3540LL ;
                var_xspectra_2tau:periodo_width_line = 3540LL ;
                var_xspectra_2tau:periodo_overlap_sample = 1770LL ;
                var_xspectra_2tau:periodo_overlap_line = 1770LL ;
                var_xspectra_2tau:coordinates = "k_az k_rg latitude line longitude pol sample" ;
        float tau(tile_line, tile_sample) ;
                tau:_FillValue = NaNf ;
                tau:long_name = "delay between two successive looks" ;
                tau:units = "s" ;
                tau:coordinates = "latitude line longitude pol sample" ;
        float azimuth_cutoff(tile_line, tile_sample) ;
                azimuth_cutoff:_FillValue = NaNf ;
                azimuth_cutoff:long_name = "Azimuthal cut-off (2tau)" ;
                azimuth_cutoff:units = "m" ;
                azimuth_cutoff:coordinates = "latitude line longitude pol sample" ;
        float azimuth_cutoff_error(tile_line, tile_sample) ;
                azimuth_cutoff_error:_FillValue = NaNf ;
                azimuth_cutoff_error:long_name = "normalized azimuthal cut-off error std (2tau)" ;
                azimuth_cutoff_error:coordinates = "latitude line longitude pol sample" ;
        short line(tile_line) ;
        short sample(tile_line, tile_sample) ;
        float corner_longitude(tile_line, tile_sample, c_sample, c_line) ;
                corner_longitude:_FillValue = NaNf ;
                corner_longitude:history = "longitude:\n  annotation/s1a.xml:\n  - /product/geolocationGrid/geolocationGridPointList/geolocationGridPoint/line\n  - /product/geolocationGrid/geolocationGridPointList/geolocationGridPoint/pixel\n  - /product/geolocationGrid/geolocationGridPointList/geolocationGridPoint/longitude\n" ;
                corner_longitude:definition = "Geodetic longitude of grid point [degrees]." ;
                corner_longitude:coordinates = "latitude line longitude pol sample" ;
        float corner_latitude(tile_line, tile_sample, c_sample, c_line) ;
                corner_latitude:_FillValue = NaNf ;
                corner_latitude:history = "latitude:\n  annotation/s1a.xml:\n  - /product/geolocationGrid/geolocationGridPointList/geolocationGridPoint/line\n  - /product/geolocationGrid/geolocationGridPointList/geolocationGridPoint/pixel\n  - /product/geolocationGrid/geolocationGridPointList/geolocationGridPoint/latitude\n" ;
                corner_latitude:definition = "Geodetic latitude of grid point [degrees]." ;
                corner_latitude:coordinates = "latitude line longitude pol sample" ;
        short corner_line(tile_line, c_line) ;
                corner_line:long_name = "line number in original digital number matrix" ;
                corner_line:coordinates = "line pol" ;
        short corner_sample(tile_line, tile_sample, c_sample) ;
                corner_sample:long_name = "sample number in original digital number matrix" ;
                corner_sample:coordinates = "latitude line longitude pol sample" ;
        float longitude(tile_line, tile_sample) ;
                longitude:_FillValue = NaNf ;
                longitude:history = "longitude:\n  annotation/s1a.xml:\n  - /product/geolocationGrid/geolocationGridPointList/geolocationGridPoint/line\n  - /product/geolocationGrid/geolocationGridPointList/geolocationGridPoint/pixel\n  - /product/geolocationGrid/geolocationGridPointList/geolocationGridPoint/longitude\n" ;
                longitude:definition = "Geodetic longitude of grid point [degrees]." ;
        float latitude(tile_line, tile_sample) ;
                latitude:_FillValue = NaNf ;
                latitude:history = "latitude:\n  annotation/s1a.xml:\n  - /product/geolocationGrid/geolocationGridPointList/geolocationGridPoint/line\n  - /product/geolocationGrid/geolocationGridPointList/geolocationGridPoint/pixel\n  - /product/geolocationGrid/geolocationGridPointList/geolocationGridPoint/latitude\n" ;
                latitude:definition = "Geodetic latitude of grid point [degrees]." ;
        byte land_flag(tile_line, tile_sample) ;
                land_flag:long_name = "land flag" ;
                land_flag:convention = "True if land is present" ;
                land_flag:coordinates = "latitude line longitude pol sample" ;
                land_flag:dtype = "bool" ;
        float burst_corner_longitude(tile_line, c_sample, c_line) ;
                burst_corner_longitude:_FillValue = NaNf ;
                burst_corner_longitude:long_name = "corner longitude of burst valid portion" ;
                burst_corner_longitude:coordinates = "line pol" ;
        float burst_corner_latitude(tile_line, c_sample, c_line) ;
                burst_corner_latitude:_FillValue = NaNf ;
                burst_corner_latitude:long_name = "corner latitude of burst valid portion" ;
                burst_corner_latitude:coordinates = "line pol" ;
        short k_gp(k_gp) ;
                k_gp:long_name = "Gegenbauer polynoms dimension" ;
        short phi_hf(phi_hf) ;
                phi_hf:long_name = "Harmonic functions dimension (odd number)" ;
        float cwave_params(tile_line, tile_sample, k_gp, phi_hf, \2tau) ;
                cwave_params:_FillValue = NaNf ;
                cwave_params:long_name = "CWAVE parameters" ;
                cwave_params:coordinates = "latitude line longitude pol sample" ;
        float lambda_range_max_macs(lambda_range_max_macs) ;
                lambda_range_max_macs:_FillValue = NaNf ;
                lambda_range_max_macs:long_name = "maximum wavelength bound for MACS estimation " ;
        float xspectra_0tau_Re(tile_line, tile_sample, freq_line, freq_sample, \0tau) ;
                xspectra_0tau_Re:_FillValue = NaNf ;
                xspectra_0tau_Re:averaged_periodograms = 81LL ;
                xspectra_0tau_Re:periodo_width_sample = 3540LL ;
                xspectra_0tau_Re:periodo_width_line = 3540LL ;
                xspectra_0tau_Re:periodo_overlap_sample = 1770LL ;
                xspectra_0tau_Re:periodo_overlap_line = 1770LL ;
                xspectra_0tau_Re:coordinates = "k_az k_rg latitude line longitude pol sample" ;
        float xspectra_0tau_Im(tile_line, tile_sample, freq_line, freq_sample, \0tau) ;
                xspectra_0tau_Im:_FillValue = NaNf ;
                xspectra_0tau_Im:averaged_periodograms = 81LL ;
                xspectra_0tau_Im:periodo_width_sample = 3540LL ;
                xspectra_0tau_Im:periodo_width_line = 3540LL ;
                xspectra_0tau_Im:periodo_overlap_sample = 1770LL ;
                xspectra_0tau_Im:periodo_overlap_line = 1770LL ;
                xspectra_0tau_Im:coordinates = "k_az k_rg latitude line longitude pol sample" ;
        float xspectra_1tau_Re(tile_line, tile_sample, freq_line, freq_sample, \1tau) ;
                xspectra_1tau_Re:_FillValue = NaNf ;
                xspectra_1tau_Re:averaged_periodograms = 81LL ;
                xspectra_1tau_Re:periodo_width_sample = 3540LL ;
                xspectra_1tau_Re:periodo_width_line = 3540LL ;
                xspectra_1tau_Re:periodo_overlap_sample = 1770LL ;
                xspectra_1tau_Re:periodo_overlap_line = 1770LL ;
                xspectra_1tau_Re:coordinates = "k_az k_rg latitude line longitude pol sample" ;
        float xspectra_1tau_Im(tile_line, tile_sample, freq_line, freq_sample, \1tau) ;
                xspectra_1tau_Im:_FillValue = NaNf ;
                xspectra_1tau_Im:averaged_periodograms = 81LL ;
                xspectra_1tau_Im:periodo_width_sample = 3540LL ;
                xspectra_1tau_Im:periodo_width_line = 3540LL ;
                xspectra_1tau_Im:periodo_overlap_sample = 1770LL ;
                xspectra_1tau_Im:periodo_overlap_line = 1770LL ;
                xspectra_1tau_Im:coordinates = "k_az k_rg latitude line longitude pol sample" ;
        float xspectra_2tau_Re(tile_line, tile_sample, freq_line, freq_sample, \2tau) ;
                xspectra_2tau_Re:_FillValue = NaNf ;
                xspectra_2tau_Re:averaged_periodograms = 81LL ;
                xspectra_2tau_Re:periodo_width_sample = 3540LL ;
                xspectra_2tau_Re:periodo_width_line = 3540LL ;
                xspectra_2tau_Re:periodo_overlap_sample = 1770LL ;
                xspectra_2tau_Re:periodo_overlap_line = 1770LL ;
                xspectra_2tau_Re:coordinates = "k_az k_rg latitude line longitude pol sample" ;
        float xspectra_2tau_Im(tile_line, tile_sample, freq_line, freq_sample, \2tau) ;
                xspectra_2tau_Im:_FillValue = NaNf ;
                xspectra_2tau_Im:averaged_periodograms = 81LL ;
                xspectra_2tau_Im:periodo_width_sample = 3540LL ;
                xspectra_2tau_Im:periodo_width_line = 3540LL ;
                xspectra_2tau_Im:periodo_overlap_sample = 1770LL ;
                xspectra_2tau_Im:periodo_overlap_line = 1770LL ;
                xspectra_2tau_Im:coordinates = "k_az k_rg latitude line longitude pol sample" ;
        float macs_Re(tile_line, tile_sample, lambda_range_max_macs, \2tau) ;
                macs_Re:_FillValue = NaNf ;
                macs_Re:kaz_min = -0.010471975511966 ;
                macs_Re:kaz_max = 0.010471975511966 ;
                macs_Re:krg_max = 0.418879020478639 ;
                macs_Re:long_name = "Mean rAnge Cross-Spectrum" ;
                macs_Re:coordinates = "latitude line longitude pol sample" ;
        float macs_Im(tile_line, tile_sample, lambda_range_max_macs, \2tau) ;
                macs_Im:_FillValue = NaNf ;
                macs_Im:kaz_min = -0.010471975511966 ;
                macs_Im:kaz_max = 0.010471975511966 ;
                macs_Im:krg_max = 0.418879020478639 ;
                macs_Im:long_name = "Mean rAnge Cross-Spectrum" ;
                macs_Im:coordinates = "latitude line longitude pol sample" ;


.. raw:: html
 </details>

.. toctree::
   :maxdepth: 1
   :hidden:
   :caption: extra explanations

   examples/L1B_Sentinel1_variables_explanation

Explanation on specific variables
---------------------------------

This section gives illustrated details on some of the variables:

    * :doc:`examples/L1B_Sentinel1_variables_explanation`


Product attributes
##################

global attributes of the sub-swath file:

.. code-block::

 // global attributes:
                :version_xsar = "1.0.2" ;
                :version_xsarslc = "2024.1.31" ;
                :processor = "./lib/python3.9/site-packages/xsarslc/scripts/L1B_xspectra_IW_SLC_IFR.py" ;
                :generation_date = "2024-Jan-31" ;


global attributes of the intra-burst group:

.. code-block::

 // group attributes:
 :name = "SENTINEL1_DS:/data/esa/sentinel-1a/L1/IW/S1A_IW_SLC__1S/2018/065/S1A_IW_SLC__1SDV_20180306T230337_20180306T230405_020901_023DBA_73A0.SAFE:IW1" ;
                :short_name = "SENTINEL1_DS:S1A_IW_SLC__1SDV_20180306T230337_20180306T230405_020901_023DBA_73A0.SAFE:IW1" ;
                :product = "SLC" ;
                :safe = "S1A_IW_SLC__1SDV_20180306T230337_20180306T230405_020901_023DBA_73A0.SAFE" ;
                :swath = "IW" ;
                :multidataset = "False" ;
                :ipf = 2.84 ;
                :platform = "SENTINEL-1A" ;
                :pols = "VV VH" ;
                :start_date = "2018-03-06 23:03:38.051625" ;
                :stop_date = "2018-03-06 23:04:03.182857" ;
                :footprint = "POLYGON ((-76.08430839864033 26.63756326996933, -75.18793064940225 26.79052036139598, -75.50267764839376 28.28730160398311, -76.41199086776611 28.13488378485153, -76.08430839864033 26.63756326996933))" ;
                :coverage = "169km * 90km (line * sample )" ;
                :orbit_pass = "Ascending" ;
                :platform_heading = -12.5313253576975 ;
                :comment = "denoised digital number, read at full resolution" ;
                :history = "digital_number: measurement/s1a-iw1-slc-v*-20180306t230338-20180306t230403-020901-023dba-00*.tiff\n" ;
                :radar_frequency = 5405000454.33435 ;
                :azimuth_time_interval = 0.0020555563 ;
                :tile_width_sample = 17700LL ;
                :tile_width_line = 17700LL ;
                :tile_overlap_sample = 0LL ;
                :tile_overlap_line = 0LL ;


global attributes of the inter-burst group:

.. code-block::

 // group attributes:
                :name = "SENTINEL1_DS:/data/esa/sentinel-1a/L1/IW/S1A_IW_SLC__1S/2021/108/S1A_IW_SLC__1SDV_20210418T212223_20210418T212253_037510_046C42_6560.SAFE:IW1" ;
                :short_name = "SENTINEL1_DS:S1A_IW_SLC__1SDV_20210418T212223_20210418T212253_037510_046C42_6560.SAFE:IW1" ;
                :product = "SLC" ;
                :safe = "S1A_IW_SLC__1SDV_20210418T212223_20210418T212253_037510_046C42_6560.SAFE" ;
                :swath = "IW" ;
                :multidataset = "False" ;
                :ipf = 3.31 ;
                :platform = "SENTINEL-1A" ;
                :pols = "VV VH" ;
                :start_date = "2021-04-18 21:22:23.644969" ;
                :stop_date = "2021-04-18 21:22:51.563535" ;
                :footprint = "POLYGON ((128.3637024723631 14.57604630647329, 127.5496545856357 14.73346785356862, 127.2081937934356 13.04621122868775, 128.0161923665588 12.88763160287155, 128.3637024723631 14.57604630647329))" ;
                :coverage = "191km * 89km (line * sample )" ;
                :orbit_pass = "Descending" ;
                :platform_heading = -167.922014873722 ;
                :azimuth_steering_rate = 1.590368784 ;
                :mean_incidence = 34.0561728242343 ;
                :azimuth_time_interval = 0.0020555563 ;
                :tile_width_sample = 17700LL ;
                :tile_width_line = 17700LL ;
                :tile_overlap_sample = 0LL ;
                :tile_overlap_line = 0LL ;


Product access
##############

Currently the L1B SAR Sentinel-1 product is disseminated from this URL:

https://cerweb.ifremer.fr/datarmor/sarwave/diffusion/sar/iw/slc/l1b/experimental_product_collection/


Acknowledgment
##############

The Sentinel-1 Level-1B SAR IFREMER Product has been co-funded by ESA through the SARWAVE project (https://www.sarwave.org/).
The processor development benefits from support and contribution from/to Sentinel-1 Mission Performance Cluster (https://sar-mpc.eu/about/activities-and-team/).
