=====
Usage
=====

To use sarwaveifrproc in a project::

    import sarwaveifrproc




Exemple Usage
-------------
Example usage 


SAFE naming convention
~~~~~~~~~~~~~~~~~~~~~~
be sure your configuration is in your python path, exemple: 

.. code-block::
   export PYTHONPATH=$PYTHONPATH:<path/to/sarwaveifrproc>


Sequential processing
~~~~~~~~~~~~~~~~~~~~~~
.. code-block::
L2-wave-processor input_path=<path/to/listing.txt>  save_directory=<path/to/savedir>


Local parallel run
~~~~~~~~~~~~~~~~~~~~~~
Example with 100 parallel jobs see hydra / joblib documentation for more information
.. code-block::
L2-wave-processor -m hydra/launcher=joblib +parallel=chunk hydra.launcher.n_jobs=100 'input_path.i=range(100)'   input_path.path=<...>  save_directory=<...>

Configuration
~~~~~~~~~~~~~~~~~~~~~~
.. code-block::
» L2-wave-processor --help
_implementations is powered by Hydra.

== Configuration groups ==
Compose your configuration from those groups (group=option)

parallel: chunk


== Config ==
Override anything in the config (foo.bar=value)

_target_: sarwaveifrproc.main.main
input_path: ???
save_directory: ???
product_id: E11
models:
  multi:
    path: models/multi.onnx
    outputs:
    - pred_hs
    - pred_phs0
    - pred_t0m1
    - conf_hs
    - conf_phs0
    - conf_t0m1
  multi_interburst:
    path: models/multi_interburst.onnx
    outputs:
    - pred_hs
    - pred_phs0
    - pred_t0m1
    - conf_hs
    - conf_phs0
    - conf_t0m1
predicted_variables:
  intraburst:
    hs_most_likely:
      model: multi
      output: pred_hs
      attrs:
        long_name: Most likely significant wave height
        units: m
    hs_conf:
      model: multi
      output: conf_hs
      attrs:
        long_name: Significant wave height confidence
        units: ''
    phs0_most_likely:
      model: multi
      output: pred_phs0
      attrs:
        long_name: Most likely wind sea significant wave height
        units: m
    phs0_conf:
      model: multi
      output: conf_phs0
      attrs:
        long_name: Wind sea significant wave height confidence
        units: ''
    t0m1_most_likely:
      model: multi
      output: pred_t0m1
      attrs:
        long_name: Most likely mean wave period
        units: s
    t0m1_conf:
      model: multi
      output: conf_t0m1
      attrs:
        long_name: Mean wave period confidence
        units: ''
  interburst:
    hs_most_likely:
      model: multi_interburst
      output: pred_hs
      attrs:
        long_name: Most likely significant wave height
        units: m
    hs_conf:
      model: multi_interburst
      output: conf_hs
      attrs:
        long_name: Significant wave height confidence
        units: ''
    phs0_most_likely:
      model: multi_interburst
      output: pred_phs0
      attrs:
        long_name: Most likely wind sea significant wave height
        units: m
    phs0_conf:
      model: multi_interburst
      output: conf_phs0
      attrs:
        long_name: Wind sea significant wave height confidence
        units: ''
    t0m1_most_likely:
      model: multi_interburst
      output: pred_t0m1
      attrs:
        long_name: Most likely mean wave period
        units: s
    t0m1_conf:
      model: multi_interburst
      output: conf_t0m1
      attrs:
        long_name: Mean wave period confidence
        units: ''
supported_input_product_versions:
- B08
- A15
- A16
- A17
overwrite: true
verbose: false
dry_run: false


Powered by Hydra (https://hydra.cc)
Use --hydra-help to view Hydra specific help
