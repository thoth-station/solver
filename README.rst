Thoth Solver
------------

Python dependency solver used in `Thoth project
<https://thoth-station.ninja>`__.

As Python is a dynamic programming language, Thoth runs several types of
solvers that differ in software environment (operating system, native packages
present, system symbols and their versions and Python interpreter version). An
example can be a solver which is running raw RHEL 8.0 with Python 3.6, another
example can be a solver with Fedora 33 with Python 3.9 installed with different
version of glibc and some of the ABI symbols of native libraries provided by
operating system (see also Python manylinux standards and devtools for more
info).

See the listing built solvers used in Thoth:

* `quay.io/thoth-station/solver-rhel-8-py38 <https://quay.io/repository/thoth-station/solver-rhel-8-py38>`__

* `quay.io/thoth-station/solver-rhel-8-py36 <https://quay.io/repository/thoth-station/solver-rhel-8-py36>`__

* `quay.io/thoth-station/solver-fedora-32-py38 <https://quay.io/repository/thoth-station/solver-fedora-32-py38>`__

* `quay.io/thoth-station/solver-fedora-32-py37 <https://quay.io/repository/thoth-station/solver-fedora-32-py37>`__

* `quay.io/thoth-station/solver-fedora-31-py38 <https://quay.io/repository/thoth-station/solver-fedora-31-py38>`__

* `quay.io/thoth-station/solver-fedora-31-py37 <https://quay.io/repository/thoth-station/solver-fedora-31-py37>`__

* `quay.io/thoth-station/solver-fedora-31-py36 <https://quay.io/repository/thoth-station/solver-fedora-31-py36>`__

* `quay.io/thoth-station/solver-fedora-30-py37 <https://quay.io/repository/thoth-station/solver-fedora-30-py37>`__

* `quay.io/thoth-station/solver-fedora-30-py36 <https://quay.io/repository/thoth-station/solver-fedora-30-py36>`__

* `quay.io/thoth-station/solver-fedora-29-py37 <https://quay.io/repository/thoth-station/solver-fedora-29-py37>`__ (no longer used)

* `quay.io/thoth-station/solver-fedora-29-py36 <https://quay.io/repository/thoth-station/solver-fedora-29-py36>`__ (no longer used)

* `quay.io/thoth-station/solver-fedora-28-py36 <https://quay.io/repository/thoth-station/solver-fedora-28-py36>`__ (no longer used)

For a `detailed explanation see this blog post
<https://dev.to/fridex/how-to-beat-python-s-pip-solving-python-dependencies-2d6e>`__.

This solver is run in different environments (different operating systems with
various native packages provided) to obtain dependency information about Python
packages.  An important information is also the fact whether the given Python
package is installable into the environment (e.g. dependencies on native
packages being present in the environment). An example could be UBI 8 specific
solver running Python 3.8 or UBI 8 running Python 3.6 with gcc tooling for
building native extensions.

Project Scope
=============

The aim of this project is to answer a simple question - what packages will be
installed (resolved by pip or any Python compliant dependency resolver) for the
provided stack?

Imagine you have an application that has one dependency:

.. code-block:: console

  $ cat requirements.txt
  tensorflow

Tool provided by this project will tell you what dependencies will be
considered during resolution (the whole dependency graph):

.. code-block:: console

  thoth-solver -vvv pypi -r requirements.txt

The output of this solver is a dependency analysis for the given software stack
- in the example above, package ``tensorflow`` in any release with analysis of
its all dependencies (direct and indirect ones) with additional information
from Python ecosystem needed for a Python resolver to perform the actual
``tensorflow`` resolution.

The tool also allows specifying custom Python package indexes which conform to
`PEP-503 <https://www.python.org/dev/peps/pep-0503/>`__ - see the ``--index``
option for analyzing your custom Python packages provided by your repositories.

It is also possible to restrict version using standard Python version range
specifiers and/or limit the output just to direct dependencies.

Produced output
===============

This tool (unless ``--no-transitive`` is specified) recursively analyzes all
the dependencies of the desired package inside a specific environment.
Dependencies to be analyzed can be defined in similar to ``requirements.txt``
file or as a string in a form of:

.. code-block:: console

  <package-name><version-cmp><version-identifier>

Where ``<package-name>`` is the analyzed package name (as present on PyPI for
example), part ``<version-cmp><version-identifier>`` is optional and creates
version specifier for the given package (if not specified, all versions are
considered).

An example output shown bellow can be reproduced by running the tool with the
following arguments (with an example of produced log):

.. code-block:: console

  $ thoth-solver python --requirements 'tensorflow==2.0.0' --index https://pypi.org/simple --no-transitive
  2019-10-01 14:01:02,756 [31432] INFO     root:128: Logging to a Sentry instance is turned off
  2019-10-01 14:01:02,756 [31432] INFO     root:150: Logging to rsyslog endpoint is turned off
  2019-10-01 14:01:06,838 [31432] INFO     thoth.solver.python.python_solver:113: Parsing dependency 'tensorflow==2.0.0'
  2019-10-01 14:01:07,003 [31432] INFO     thoth.solver.python.python:356: Using index 'https://pypi.org/simple' to discover package 'tensorflow' in version '2.0.0'
  2019-10-01 14:01:40,568 [31432] INFO     thoth.solver.python.python:405: Resolving dependency versions for 'absl-py' with range '>=0.7.0' from 'https://pypi.org/simple'
  2019-10-01 14:01:40,568 [31432] INFO     thoth.solver.python.python_solver:113: Parsing dependency 'absl-py>=0.7.0'
  2019-10-01 14:01:40,689 [31432] INFO     thoth.solver.python.python:405: Resolving dependency versions for 'astor' with range '>=0.6.0' from 'https://pypi.org/simple'
  2019-10-01 14:01:40,689 [31432] INFO     thoth.solver.python.python_solver:113: Parsing dependency 'astor>=0.6.0'
  2019-10-01 14:01:40,841 [31432] INFO     thoth.solver.python.python:405: Resolving dependency versions for 'gast' with range '==0.2.2' from 'https://pypi.org/simple'
  2019-10-01 14:01:40,841 [31432] INFO     thoth.solver.python.python_solver:113: Parsing dependency 'gast==0.2.2'
  2019-10-01 14:01:40,984 [31432] INFO     thoth.solver.python.python:405: Resolving dependency versions for 'google-pasta' with range '>=0.1.6' from 'https://pypi.org/simple'
  2019-10-01 14:01:40,985 [31432] INFO     thoth.solver.python.python_solver:113: Parsing dependency 'google-pasta>=0.1.6'
  2019-10-01 14:01:41,104 [31432] INFO     thoth.solver.python.python:405: Resolving dependency versions for 'keras-applications' with range '>=1.0.8' from 'https://pypi.org/simple'
  2019-10-01 14:01:41,104 [31432] INFO     thoth.solver.python.python_solver:113: Parsing dependency 'keras-applications>=1.0.8'
  2019-10-01 14:01:41,273 [31432] INFO     thoth.solver.python.python:405: Resolving dependency versions for 'keras-preprocessing' with range '>=1.0.5' from 'https://pypi.org/simple'
  2019-10-01 14:01:41,274 [31432] INFO     thoth.solver.python.python_solver:113: Parsing dependency 'keras-preprocessing>=1.0.5'
  2019-10-01 14:01:41,443 [31432] INFO     thoth.solver.python.python:405: Resolving dependency versions for 'numpy' with range '<2.0,>=1.16.0' from 'https://pypi.org/simple'
  2019-10-01 14:01:41,443 [31432] INFO     thoth.solver.python.python_solver:113: Parsing dependency 'numpy<2.0,>=1.16.0'
  2019-10-01 14:01:41,723 [31432] INFO     thoth.solver.python.python:405: Resolving dependency versions for 'opt-einsum' with range '>=2.3.2' from 'https://pypi.org/simple'
  2019-10-01 14:01:41,723 [31432] INFO     thoth.solver.python.python_solver:113: Parsing dependency 'opt-einsum>=2.3.2'
  2019-10-01 14:01:41,828 [31432] INFO     thoth.solver.python.python:405: Resolving dependency versions for 'six' with range '>=1.10.0' from 'https://pypi.org/simple'
  2019-10-01 14:01:41,828 [31432] INFO     thoth.solver.python.python_solver:113: Parsing dependency 'six>=1.10.0'
  2019-10-01 14:01:41,942 [31432] INFO     thoth.solver.python.python:405: Resolving dependency versions for 'protobuf' with range '>=3.6.1' from 'https://pypi.org/simple'
  2019-10-01 14:01:41,943 [31432] INFO     thoth.solver.python.python_solver:113: Parsing dependency 'protobuf>=3.6.1'
  2019-10-01 14:01:42,095 [31432] INFO     thoth.solver.python.python:405: Resolving dependency versions for 'tensorboard' with range '<2.1.0,>=2.0.0' from 'https://pypi.org/simple'
  2019-10-01 14:01:42,095 [31432] INFO     thoth.solver.python.python_solver:113: Parsing dependency 'tensorboard<2.1.0,>=2.0.0'
  2019-10-01 14:01:42,286 [31432] INFO     thoth.solver.python.python:405: Resolving dependency versions for 'tensorflow-estimator' with range '<2.1.0,>=2.0.0' from 'https://pypi.org/simple'
  2019-10-01 14:01:42,287 [31432] INFO     thoth.solver.python.python_solver:113: Parsing dependency 'tensorflow-estimator<2.1.0,>=2.0.0'
  2019-10-01 14:01:42,411 [31432] INFO     thoth.solver.python.python:405: Resolving dependency versions for 'termcolor' with range '>=1.1.0' from 'https://pypi.org/simple'
  2019-10-01 14:01:42,411 [31432] INFO     thoth.solver.python.python_solver:113: Parsing dependency 'termcolor>=1.1.0'
  2019-10-01 14:01:42,580 [31432] INFO     thoth.solver.python.python:405: Resolving dependency versions for 'wrapt' with range '>=1.11.1' from 'https://pypi.org/simple'
  2019-10-01 14:01:42,581 [31432] INFO     thoth.solver.python.python_solver:113: Parsing dependency 'wrapt>=1.11.1'
  2019-10-01 14:01:42,693 [31432] INFO     thoth.solver.python.python:405: Resolving dependency versions for 'grpcio' with range '>=1.8.6' from 'https://pypi.org/simple'
  2019-10-01 14:01:42,693 [31432] INFO     thoth.solver.python.python_solver:113: Parsing dependency 'grpcio>=1.8.6'
  2019-10-01 14:01:43,007 [31432] INFO     thoth.solver.python.python:405: Resolving dependency versions for 'wheel' with range '>=0.26' from 'https://pypi.org/simple'
  2019-10-01 14:01:43,008 [31432] INFO     thoth.solver.python.python_solver:113: Parsing dependency 'wheel>=0.26'
  2019-10-01 14:01:43,116 [31432] INFO     thoth.solver.python.python:405: Resolving dependency versions for 'backports-weakref' with range '>=1.0rc1' from 'https://pypi.org/simple'
  2019-10-01 14:01:43,117 [31432] INFO     thoth.solver.python.python_solver:113: Parsing dependency 'backports-weakref>=1.0rc1'
  2019-10-01 14:01:43,262 [31432] INFO     thoth.solver.python.python:405: Resolving dependency versions for 'enum34' with range '>=1.1.6' from 'https://pypi.org/simple'
  2019-10-01 14:01:43,262 [31432] INFO     thoth.solver.python.python_solver:113: Parsing dependency 'enum34>=1.1.6'

An the output can be pretty verbose, the following section describes some most
interesting parts of the output using JSONPath:

* ``.metadata`` - metadata assigned to the solver run - these metadata are especially useful within project Thoth, where analyzer is run in a cluster, the purpose of metadata is to capture information which could be beneficial when debugging issues which arise in the cluster due to different container environment (e.g. Python version)
* ``.result`` - the actual result as produced by this tool
* ``.result.unparsed`` - a list of requirements that failed to be parsed (wrong dependency specification not conforming to Python standards)
* ``.result.unresolved`` - a list of requirements that failed to be resolved - the reason behind failure can be for example non-existing package or its version on the given Python package index, or for example incompatibility of package distribution with the solver's software environment (Python version, environment markers, ...), or bogus distribution (e.g. forgotten ``requirements.txt`` in the distribution required by ``setup.py`` on package build).
* ``.result.tree`` - the actual serialized dependency tree (broken dependency graph as cyclic dependencies are possible in Python ecosystem)
* ``.result.tree[*].package_name`` - name of the analyzed package
* ``.result.tree[*].package_version`` - version of the analyzed package
* ``.result.tree[*].sha256`` - sha256 digests of artifacts present on the given Python package index
* ``.result.tree[*].importlib_metadata`` - metadata associated with the given package, these metadata are obtained using `importlib-metadata <https://pypi.org/project/importlib-metadata/>`__, fallback to standard `importlib.metadata <https://docs.python.org/3.9/library/importlib.metadata.html>`__ on Python3.9+

  * ``.result.tree[*].importlib_metadata.metadata`` - package metadata - see `packaging docs for more info <https://packaging.python.org/specifications/core-metadata/>`__
  * ``.result.tree[*].importlib_metadata.requires`` - raw strings which declare the given Python package requirements as obtained by ``importlib_metadata.requires``
  * ``.result.tree[*].importlib_metadata.version`` - version as obtained by ``importlib_metadata.requires``
  * ``.result.tree[*].importlib_metadata.files`` - file information about the given package (additionally parsed to provide digest, file size and path) as obtained by ``importlib_metadata.files``
  * ``.result.tree[*].importlib_metadata.entry_points`` - entry points as obtained by ``importlib_metadata.entry_points`` (additionally parsed to provide entry point name, group and value)

  .. code-block:: json

    {
      "entry_points": [
        {
          "group": "console_scripts",
          "name": "saved_model_cli",
          "value": "tensorflow.python.tools.saved_model_cli:main"
        },
        {
          "group": "console_scripts",
          "name": "tensorboard",
          "value": "tensorboard.main:run_main"
        },
        {
          "group": "console_scripts",
          "name": "tf_upgrade_v2",
          "value": "tensorflow.tools.compatibility.tf_upgrade_v2_main:main"
        },
        {
          "group": "console_scripts",
          "name": "tflite_convert",
          "value": "tensorflow.lite.python.tflite_convert:main"
        },
        {
          "group": "console_scripts",
          "name": "toco",
          "value": "tensorflow.lite.python.tflite_convert:main"
        },
        {
          "group": "console_scripts",
          "name": "toco_from_protos",
          "value": "tensorflow.lite.toco.python.toco_from_protos:main"
        }
      ],
      "files": [
        {
          "hash": {
            "mode": "sha256",
            "value": "47DEQpj8HBSa-_TImW-5JCeuQeRkm5NMpJWZG3hSuFU"
          },
          "path": "tensorflow_core/tools/pip_package/__init__.py",
          "size": 0
        }
      ],
      "metadata": {
        "Author": "Google Inc.",
        "Author-email": "packages@tensorflow.org",
        "Classifier": [
          "Development Status :: 5 - Production/Stable",
          "Intended Audience :: Developers",
          "Intended Audience :: Education",
          "Intended Audience :: Science/Research",
          "License :: OSI Approved :: Apache Software License",
          "Programming Language :: Python :: 2",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3.4",
          "Programming Language :: Python :: 3.5",
          "Programming Language :: Python :: 3.6",
          "Programming Language :: Python :: 3.7",
          "Topic :: Scientific/Engineering",
          "Topic :: Scientific/Engineering :: Mathematics",
          "Topic :: Scientific/Engineering :: Artificial Intelligence",
          "Topic :: Software Development",
          "Topic :: Software Development :: Libraries",
          "Topic :: Software Development :: Libraries :: Python Modules"
        ],
        "Download-URL": "https://github.com/tensorflow/tensorflow/tags",
        "Home-page": "https://www.tensorflow.org/",
        "Keywords": "tensorflow tensor machine learning",
        "License": "Apache 2.0",
        "Metadata-Version": "2.1",
        "Name": "tensorflow",
        "Platform": [
          "UNKNOWN"
        ],
        "Requires-Dist": [
          "absl-py (>=0.7.0)",
          "astor (>=0.6.0)",
          "gast (==0.2.2)",
          "google-pasta (>=0.1.6)",
          "keras-applications (>=1.0.8)",
          "keras-preprocessing (>=1.0.5)",
          "numpy (<2.0,>=1.16.0)",
          "opt-einsum (>=2.3.2)",
          "six (>=1.10.0)",
          "protobuf (>=3.6.1)",
          "tensorboard (<2.1.0,>=2.0.0)",
          "tensorflow-estimator (<2.1.0,>=2.0.0)",
          "termcolor (>=1.1.0)",
          "wrapt (>=1.11.1)",
          "grpcio (>=1.8.6)",
          "wheel (>=0.26)",
          "backports.weakref (>=1.0rc1) ; python_version < \"3.4\"",
          "enum34 (>=1.1.6) ; python_version < \"3.4\""
        ],
        "Summary": "TensorFlow is an open source machine learning framework for everyone.",
        "Version": "2.0.0"
      },
      "requires": [
        "absl-py (>=0.7.0)",
        "astor (>=0.6.0)",
        "gast (==0.2.2)",
        "google-pasta (>=0.1.6)",
        "keras-applications (>=1.0.8)",
        "keras-preprocessing (>=1.0.5)",
        "numpy (<2.0,>=1.16.0)",
        "opt-einsum (>=2.3.2)",
        "six (>=1.10.0)",
        "protobuf (>=3.6.1)",
        "tensorboard (<2.1.0,>=2.0.0)",
        "tensorflow-estimator (<2.1.0,>=2.0.0)",
        "termcolor (>=1.1.0)",
        "wrapt (>=1.11.1)",
        "grpcio (>=1.8.6)",
        "wheel (>=0.26)",
        "backports.weakref (>=1.0rc1) ; python_version < \"3.4\"",
        "enum34 (>=1.1.6) ; python_version < \"3.4\""
      ],
      "version": "2.0.0"
    }

  The example above shows data associated with ``tensorflow==2.0.0``. The ``files``
  section is intentionally snipped, the file digest is signed as described in
  `PEP-427 <https://www.python.org/dev/peps/pep-0427/#id16>`__.

* ``.result.tree[*].dependencies`` - a list of dependencies which can be resolved given requirements specification of the analyzed package
* ``.result.tree[*].dependencies[*].extras`` - name of extras signalizing the given package should be installed with extras as specified in `PEP-508 in extras section <https://www.python.org/dev/peps/pep-0508/#extras>`__
* ``.result.tree[*].dependencies[*].extra`` - name of extra which should be required to take into account this dependency as specified `PEP-508 in extras section <https://www.python.org/dev/peps/pep-0508/#extras>`__
* ``.result.tree[*].dependencies[*].marker`` - a full specification of the environment marker as described in `PEP-508 in environment markers section <https://www.python.org/dev/peps/pep-0508/#environment-markers>`__
* ``.result.tree[*].dependencies[*].marker_evaluation_error`` - a string capturing error information when marker evaluation failed in the run software environment, otherwise ``null``
* ``.result.tree[*].dependencies[*].marker_evaluated`` - marker defined by the package, but additionally adjusted for evaluation for the current environment (see notes bellow).
* ``.result.tree[*].dependencies[*].marker_evaluation_result`` - a boolean representing if the given marker evaluation was evaluated as ``true`` (the given environment accepts marker) or ``false`` (marker not accepted), a special value of `null` signalizes marker evaluation error (see ``marker_evaluation_error`` for more info)
* ``.result.tree[*].dependencies[*].normalized_package_name`` - a string representing normalized package name as described in `PEP-503 in normalized names section <https://www.python.org/dev/peps/pep-0503/#normalized-names>`__
* ``.result.tree[*].dependencies[*].specifier`` - a version range specifier which was declared by package which depends on the given dependency conforming to `PEP-440 <https://www.python.org/dev/peps/pep-0440/>`__
* ``.result.tree[*].dependencies[*].resolved_versions`` - a list of versions which were resolved given the version range specifier and specified Python package indexes (passed ``--index`` option can specify multiple indexes which causes package discovery on each of them)

An example of a dependency entry (an entry from one of ``.result.tree[*].dependencies``:

.. code-block:: json

  {
    "extras": [],
    "extra": [],
    "marker": "python_version < \"3.4\"",
    "marker_evaluated": "python_version < \"3.4\"",
    "marker_evaluation_error": null,
    "marker_evaluation_result": false,
    "normalized_package_name": "backports-weakref",
    "package_name": "backports.weakref",
    "parsed_markers": [
      {
        "op": "<",
        "value": "3.4",
        "variable": "python_version"
      }
    ],
    "resolved_versions": [
      {
        "index": "https://pypi.org/simple",
        "versions": [
          "1.0rc1",
          "1.0.post1"
        ]
      }
    ],
    "specifier": ">=1.0rc1"
  }

To evaluate environment markers inside solver environment, there was a need to
adjust marker so that it can be evaluated in the solver environment - see
`PEP-508 in environment markers section
<https://www.python.org/dev/peps/pep-0508/#environment-markers>`__
specification, specifically the following section:

.. code-block::

  The "extra" variable is special. It is used by wheels to signal which
  specifications apply to a given extra in the wheel METADATA file, but since
  the METADATA file is based on a draft version of PEP-426, there is no current
  specification for this. Regardless, outside of a context where this special
  handling is taking place, the "extra" variable should result in an error like
  all other unknown variables.

Installation and Deployment
===========================

This project is also released on `PyPI
<https://pypi.org/project/thoth-solver>`__, so the latest release can be
installed via pip or `Pipenv <https://pipenv.readthedocs.io>`__:

.. code-block:: console

  pipenv install thoth-solver

Solver is run in `project Thoth <https://thoth-station.ninja>`__ to gather
information about package dependencies. Check `thoth-station/thoth-application
<https://github.com/thoth-station/thoth-application>`__ repository for
deployment and installation instructions.

Running solver locally
======================

To run solver locally, first clone the repo and install the project:

.. code-block:: console

  git clone git@github.com:thoth-station/solver.git thoth-solver
  cd thoth-solver
  pipenv install --dev
  PYTHONPATH='.' ./thoth-solver-cli --help

Now you can run the solver:

.. code-block:: console

  pipenv run python3 ./thoth-solver --verbose python -r 'selinon==1.0.0' -i https://pypi.org/simple --no-transitive
