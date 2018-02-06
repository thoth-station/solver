thoth-solver
============

Dependency solver for the Thoth project.


Project scope
-------------

The aim of this project is to answer a simple question - what packages will be installed (resolved by pip) for the provided stack?

Imagine you have an application that has one dependency:

.. code-block:: console

  $ cat requirements.txt
  tensorflow


This project will tell you how dependencies could be resolved:

.. code-block:: console

  $ thoth-solver -vvv pypi -r requirements.txt --exclude-packages setuptools --tree-only
  [
    {
      "dependencies": [],
      "package": {
        "key": "wheel",
        "package_name": "wheel"
      }
    },
    {
      "dependencies": [],
      "package": {
        "key": "werkzeug",
        "package_name": "Werkzeug"
      }
    },
    {
      "dependencies": [
        {
          "key": "wheel",
          "package_name": "wheel",
          "required_version": ">=0.26",
          "resolved_versions": [
            "0.26.0",
            "0.27.0",
            "0.28.0",
            "0.29.0",
            "0.30.0a0",
            "0.30.0"
          ]
        },
        {
          "key": "six",
          "package_name": "six",
          "required_version": ">=1.10.0",
          "resolved_versions": [
            "1.10.0",
            "1.11.0"
          ]
        },
        {
          "key": "protobuf",
          "package_name": "protobuf",
          "required_version": ">=3.4.0",
          "resolved_versions": [
            "3.4.0",
            "3.5.0.post1",
            "3.5.1"
          ]
        },
        {
          "key": "absl-py",
          "package_name": "absl-py",
          "required_version": ">=0.1.6",
          "resolved_versions": [
            "0.1.6",
            "0.1.7",
            "0.1.8",
            "0.1.9",
            "0.1.10"
          ]
        },
        {
          "key": "numpy",
          "package_name": "numpy",
          "required_version": ">=1.12.1",
          "resolved_versions": [
            "1.12.1",
            "1.13.0rc2",
            "1.13.0rc1",
            "1.13.0",
            "1.13.1",
            "1.13.3",
            "1.14.0rc1",
            "1.14.0"
          ]
        },
        {
          "key": "tensorflow-tensorboard",
          "package_name": "tensorflow-tensorboard",
          "required_version": "<1.6.0,>=1.5.0",
          "resolved_versions": [
            "1.5.0"
          ]
        }
      ],
      "package": {
        "key": "tensorflow",
        "package_name": "tensorflow"
      }
    },
    {
      "dependencies": [
        {
          "key": "wheel",
          "package_name": "wheel",
          "required_version": ">=0.26",
          "resolved_versions": [
            "0.26.0",
            "0.27.0",
            "0.28.0",
            "0.29.0",
            "0.30.0a0",
            "0.30.0"
          ]
        },
        {
          "key": "numpy",
          "package_name": "numpy",
          "required_version": ">=1.12.0",
          "resolved_versions": [
            "1.12.0",
            "1.12.1",
            "1.13.0rc2",
            "1.13.0rc1",
            "1.13.0",
            "1.13.1",
            "1.13.3",
            "1.14.0rc1",
            "1.14.0"
          ]
        },
        {
          "key": "markdown",
          "package_name": "markdown",
          "required_version": ">=2.6.8",
          "resolved_versions": [
            "2.6.8",
            "2.6.9",
            "2.6.10",
            "2.6.11"
          ]
        },
        {
          "key": "futures",
          "package_name": "futures",
          "required_version": ">=3.1.1",
          "resolved_versions": [
            "3.1.1",
            "3.2.0"
          ]
        },
        {
          "key": "six",
          "package_name": "six",
          "required_version": ">=1.10.0",
          "resolved_versions": [
            "1.10.0",
            "1.11.0"
          ]
        },
        {
          "key": "wheel",
          "package_name": "wheel",
          "required_version": null,
          "resolved_versions": [
            "0.1",
            "0.2",
            "0.3",
            "0.4",
            "0.4.1",
            "0.4.2",
            "0.5",
            "0.6",
            "0.7",
            "0.8",
            "0.9",
            "0.9.1",
            "0.9.2",
            "0.9.3",
            "0.9.4",
            "0.9.5",
            "0.9.6",
            "0.9.7",
            "0.10.0",
            "0.10.1",
            "0.10.2",
            "0.10.3",
            "0.11.0",
            "0.12.0",
            "0.13.0",
            "0.14.0",
            "0.15.0",
            "0.16.0",
            "0.17.0",
            "0.18.0",
            "0.19.0",
            "0.21.0",
            "0.22.0",
            "0.23.0",
            "0.24.0",
            "0.25.0",
            "0.26.0",
            "0.27.0",
            "0.28.0",
            "0.29.0",
            "0.30.0a0",
            "0.30.0"
          ]
        },
        {
          "key": "bleach",
          "package_name": "bleach",
          "required_version": "==1.5.0",
          "resolved_versions": [
            "1.5.0"
          ]
        },
        {
          "key": "werkzeug",
          "package_name": "werkzeug",
          "required_version": ">=0.11.10",
          "resolved_versions": [
            "0.11.10",
            "0.11.11",
            "0.11.12",
            "0.11.13",
            "0.11.14",
            "0.11.15",
            "0.12",
            "0.12.1",
            "0.12.2",
            "0.13",
            "0.14",
            "0.14.1"
          ]
        },
        {
          "key": "protobuf",
          "package_name": "protobuf",
          "required_version": ">=3.4.0",
          "resolved_versions": [
            "3.4.0",
            "3.5.0.post1",
            "3.5.1"
          ]
        },
        {
          "key": "html5lib",
          "package_name": "html5lib",
          "required_version": "==0.9999999",
          "resolved_versions": [
            "0.9999999"
          ]
        }
      ],
      "package": {
        "key": "tensorflow-tensorboard",
        "package_name": "tensorflow-tensorboard"
      }
    },
    {
      "dependencies": [],
      "package": {
        "key": "six",
        "package_name": "six"
      }
    },
    {
      "dependencies": [
        {
          "key": "six",
          "package_name": "six",
          "required_version": ">=1.9",
          "resolved_versions": [
            "1.9.0",
            "1.10.0",
            "1.11.0"
          ]
        }
      ],
      "package": {
        "key": "protobuf",
        "package_name": "protobuf"
      }
    },
    {
      "dependencies": [],
      "package": {
        "key": "pip",
        "package_name": "pip"
      }
    },
    {
      "dependencies": [],
      "package": {
        "key": "numpy",
        "package_name": "numpy"
      }
    },
    {
      "dependencies": [],
      "package": {
        "key": "markdown",
        "package_name": "Markdown"
      }
    },
    {
      "dependencies": [
        {
          "key": "six",
          "package_name": "six",
          "required_version": null,
          "resolved_versions": [
            "0.9.0",
            "0.9.1",
            "0.9.2",
            "1.0b1",
            "1.0.0",
            "1.1.0",
            "1.2.0",
            "1.3.0",
            "1.4.0",
            "1.4.1",
            "1.5.0",
            "1.5.1",
            "1.5.2",
            "1.6.0",
            "1.6.1",
            "1.7.0",
            "1.7.1",
            "1.7.2",
            "1.7.3",
            "1.8.0",
            "1.9.0",
            "1.10.0",
            "1.11.0"
          ]
        }
      ],
      "package": {
        "key": "html5lib",
        "package_name": "html5lib"
      }
    },
    {
      "dependencies": [],
      "package": {
        "key": "futures",
        "package_name": "futures"
      }
    },
    {
      "dependencies": [
        {
          "key": "six",
          "package_name": "six",
          "required_version": null,
          "resolved_versions": [
            "0.9.0",
            "0.9.1",
            "0.9.2",
            "1.0b1",
            "1.0.0",
            "1.1.0",
            "1.2.0",
            "1.3.0",
            "1.4.0",
            "1.4.1",
            "1.5.0",
            "1.5.1",
            "1.5.2",
            "1.6.0",
            "1.6.1",
            "1.7.0",
            "1.7.1",
            "1.7.2",
            "1.7.3",
            "1.8.0",
            "1.9.0",
            "1.10.0",
            "1.11.0"
          ]
        },
        {
          "key": "html5lib",
          "package_name": "html5lib",
          "required_version": ">=0.999,!=0.99999,!=0.9999,<0.99999999",
          "resolved_versions": [
            "0.999",
            "0.999999",
            "0.9999999"
          ]
        }
      ],
      "package": {
        "key": "bleach",
        "package_name": "bleach"
      }
    },
    {
      "dependencies": [
        {
          "key": "six",
          "package_name": "six",
          "required_version": null,
          "resolved_versions": [
            "0.9.0",
            "0.9.1",
            "0.9.2",
            "1.0b1",
            "1.0.0",
            "1.1.0",
            "1.2.0",
            "1.3.0",
            "1.4.0",
            "1.4.1",
            "1.5.0",
            "1.5.1",
            "1.5.2",
            "1.6.0",
            "1.6.1",
            "1.7.0",
            "1.7.1",
            "1.7.2",
            "1.7.3",
            "1.8.0",
            "1.9.0",
            "1.10.0",
            "1.11.0"
          ]
        }
      ],
      "package": {
        "key": "absl-py",
        "package_name": "absl-py"
      }
    }
  ]

Another question that can be answered by ``thoth-solver`` - how can different stacks looks like (explicit full definition of a stack)? Consider the following ``requirements.txt`` file:

.. code-block:: console

  $ cat requriements.txt
  setuptools>=38.5.0

What all possible stack definitions satisfy given requirement?

.. code-block:: console

  $ ./thoth-solver -vv pypi -r requirements.txt
  [
    "wheel==0.6\n"setuptools==34.4.0\n"pip==1.0\n"
    ...
  ]

Note that this can resolve in huge number of stacks and the application can be easily killed due to OOM.

Current limitations
-------------------

Note that pip does not allow to directly query what are package dependencies without explicitly installing packages. That's why ``thoth-solver`` explicitly installs required stack for the given package and tries to resolve them. This also means, that there is a possibility that not all dependencies will be stated in the output.


Installation
------------

.. code-block:: console

  $ git clone git@github.com:fridex/thoth-solver.git
  $ cd thoth-solver && export PYTHONPATH='.'
  $ ./thoth-solver --help
