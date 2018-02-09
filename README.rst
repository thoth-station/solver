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

  $ thoth-solver -vvv pypi -r requirements.txt 

The output can be found at `here <https://pastebin.com/bKLbcXe1>`_.

Installation
------------

.. code-block:: console

  $ git clone git@github.com:fridex/thoth-solver.git
  $ cd thoth-solver && export PYTHONPATH='.'
  $ ./thoth-solver --help
