.. include:: ../../README.rst

Crossroad
=========

* `Documentation for thamos <../thamos>`_
* `Documentation for thoth-adviser <../adviser>`_
* `Documentation for thoth-analyzer <../analyzer>`_
* `Documentation for thoth-common <../common>`_
* `Documentation for thoth-lab <../lab>`_
* `Documentation for thoth-package-analyzer <../package-analyzer>`_
* `Documentation for thoth-package-extract <../package-extract>`_
* `Documentation for thoth-python <../python>`_
* `Documentation for thoth-storages <../storages>`_
* `Documentation for kebechet <../kebechet>`_
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. toctree::
   :maxdepth: 3

   thoth.solver

This documentation corresponds to implementation in version |version|,
documentation was generated on |today|.


Creating New Solvers
####################

A. Firstly identify the upstream image that you wish to develop a new solver from. Create an overlay for that new solver in [`thoth-station/s2i-thoth`](https://github.com/thoth-station/s2i-thoth). Each solver overlay should have 4 files.
 1. A `Dockerfile` to build the image from. This should be based off of the other examples available in the (s2i-thoth-repo)[https://github.com/thoth-station/s2i-thoth].
 2. A `requirements.in` stating the required dependencies.
 3. A `requirements.txt` which can be generated from pip compile using the following command once the `requirements.in` file is present: `pip-compile --generate-hashes requirements.in`.
 4. An `s2i_assemble.patch` file. This will be used to patch the upstream image's s2i_assemble file with the dependencies required by thoth-station.
   - Documentation on custructing this patch file is already availabe [here](https://github.com/thoth-station/s2i-thoth/blob/master/README.rst#s2i-assemble-patches).
B. Secondly head over to the [solver-repo][https://github.com/thoth-station/solver], and create an overlay for your new solver. This entails:
 1. Creating the overlay directory in the solver-repo root, with a `Pipfile` and `Pipfile.lock`
 2. Create a new overlay in the `.thoth.yaml` file [see example](https://github.com/thoth-station/solver/blob/master/.thoth.yaml#L15-L22)
 3. Create a new overlay in the `.aicoe-ci.yaml` file [see example](https://github.com/thoth-station/solver/blob/master/.aicoe-ci.yaml#L50-L63)
C. Third, create a deployment for the new solver image in `thoth-station/thoth-application`.
 1. Add your solver image to the [base imagestream file](https://github.com/thoth-station/thoth-application/blob/master/solver/base/imagestreams.yaml)
 2. Add your solver image to the imagestream file for the overlay you want to deploy it to. An example [here](https://github.com/thoth-station/thoth-application/blob/master/solver/overlays/test/imagestreamtag.yaml#L42-L55) shows the `f35-py310` overlay being deployed to the `test` overlay.
D. Finally, create a PR in thoth-station/perscriptions to gerenate the prescriptions for the new solver overlay. The code used to generate these perscriptions is available on [this issue thread](https://github.com/thoth-station/adviser/issues/1961).
