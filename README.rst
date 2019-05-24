Thoth Solver
------------

Dependency solver used in `Thoth project <https://thoth-station.ninja>`_.

Project Scope
=============

The aim of this project is to answer a simple question - what packages will be
installed (resolved by pip) for the provided stack?

Imagine you have an application that has one dependency:

.. code-block:: console

  $ cat requirements.txt
  tensorflow


This project will tell you how dependencies could be resolved:

.. code-block:: console

  thoth-solver -vvv pypi -r requirements.txt 

The output can be found at `here <https://github.com/thoth-station/misc/blob/master/examples/runtime-environment/resolved.json>`_.

You can optionally also specify a list of indexes which should be checked for each package.

Installation and Deployment
===========================

.. code-block:: console

  git clone git@github.com:thoth-station/solver.git thoth-solver
  cd thoth-solver
  PYTHONPATH='.' ./thoth-solver-cli --help


This project is also released on
`PyPI <https://pypi.org/project/thoth-solver>`_, so the latest release can be
installed via pip or `Pipenv <https://pipenv.readthedocs.io>`_:

.. code-block:: console

  pipenv install thoth-solver


Solver is run in Thoth to gather information about package dependencies. You
can find deployment templates in the `openshift/` directory present in the
root of `solver's Git repository <https://github.com/thoth-station/solver>`_. The
actual deployment is done using Ansible playbooks available in the
`Thoth's core repository <https://github.com/thoth-station/core>`_.
