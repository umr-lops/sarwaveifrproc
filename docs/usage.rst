=====
Usage
=====

To use sarwaveifrproc in a project::

    import sarwaveifrproc


.. code-block::
PYTHONPATH=. L2-wave-processor 'hydra/help=[default,doc]' --help

        Generate a L2 WAVE product from a L1B or L1C SAFE.

        input_path: l1b or l1c safe path or listing path (.txt file).
        save_directory: where to save output data
        product_id: 3 digits ID representing the processing options. Ex: E00.
        models: onnx models and output
        predicted_variables:  model outputs and associated variables name to add to the L2 product
        overwrite: overwrite the existing outputs
        verbose: debug log level if True

        == Configuration groups ==
        Compose your configuration from those groups (group=option)

        parallel: chunk


        == Config ==
        Override anything in the config (foo.bar=value)

        _target_: sarwaveifrproc.main_new.main
        input_path: ???
        save_directory: ???
        product_id: E09
        models:
          hs_mod:
            path: models/hs.onnx
            outputs:
            - pred
            - conf
          t0m1_mod:
            path: models/t0m1.onnx
            outputs:
            - pred
            - conf
          phs0_mod:
            path: models/phs0.onnx
            outputs:
            - pred
            - conf
        predicted_variables:
          intraburst:
            hs_most_likely:
              model: hs_mod
              output: pred
              attrs:
                long_name: Most likely significant wave height
                units: m
            hs_conf:
              model: hs_mod
              output: conf
              attrs:
                long_name: Significant wave height confidence
                units: ''
            phs0_most_likely:
              model: phs0_mod
              output: pred
              attrs:
                long_name: Most likely wind sea significant wave height
                units: m
            phs0_conf:
              model: phs0_mod
              output: conf
              attrs:
                long_name: Wind sea significant wave height confidence
                units: ''
            t0m1_most_likely:
              model: t0m1_mod
              output: pred
              attrs:
                long_name: Most likely mean wave period
                units: s
            t0m1_conf:
              model: t0m1_mod
              output: conf
              attrs:
                long_name: Mean wave period confidence
                units: ''
          interburst: ${.intraburst}
        overwrite: true
        verbose: false


        Powered by Hydra (https://hydra.cc)
        Use --hydra-help to view Hydra specific help
                                    list of sea states variables to predict.
