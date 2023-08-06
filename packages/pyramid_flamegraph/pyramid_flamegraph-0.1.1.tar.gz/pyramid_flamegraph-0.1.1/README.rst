pyramid_flamegraph
==================

This package provides a Pyramid tween to generate a `flamegraph`_ image for every request.

developed on the basis of `pyramid_pycallgraph implemented by Andreas Kaiser`_
and `djdt-flamegraph implemented by Bo Lopker`_ .

.. _`flamegraph`: https://github.com/brendangregg/FlameGraph
.. _`djdt-flamegraph implemented by Bo Lopker`: https://github.com/23andMe/djdt-flamegraph
.. _`pyramid_pycallgraph implemented by Andreas Kaiser`: https://github.com/disko/pyramid_pycallgraph


Installation
------------

.. code-block:: bash

    $ pip install --upgrade git+https://gitlab.com/hhatto/pyramid_flamegraph


Usage
-----

.. code-block:: text

    pyramid.includes =
        pyramid_flamegraph


Configuration
-------------

.. code-block:: text

    flamegraph.interval = 0.005     # default: 0.001
    flamegraph.color = aqua         # default: hot

