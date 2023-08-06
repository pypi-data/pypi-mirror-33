==========
 Experipy
==========

.. image:: https://travis-ci.org/Elemnir/experipy.svg?branch=master
    :target: https://travis-ci.org/Elemnir/experipy

A framework for writing and running Computational Science experiments.

``experipy`` provides a composable grammar for automating experiment script generation and a tool which can then execute those scripts. Supports PBS script based queueing.

------------------
 A Simple Example
------------------

::

    from experipy.exp       import Experiment
    from experipy.grammar   import Executable

    exp = Experiment(Executable("echo", ["Hello World"]), 
                     expname="test", 
                     destdir="results")
    exp.run()

This will run the program ``echo`` with the argument ``Hello World`` in a directory in ``/tmp``, writing the output and error, along with timing information, to the directory ``results``. Directories will be created as needed. A complete example showing how to write an experiment for a Python script can be found in ``test/runtest.py``.

--------------
 Installation
--------------

``experipy`` can be installed from PyPI, and has no other dependencies.

::
    
    ?> pip install experipy
    
---------------
 Documentation
---------------

Full documentation for experipy can be found at https://experipy.readthedocs.io. 

-----------------------
 Features In The Works
-----------------------

- Expand ``experipy.system`` to include more standard command line tools

- Beef up PBS script options
