Spark Management Consolidated
=============================

A small module that will load as a singleton class object to manage Spark
related things.

Installation
------------

Directly via ``pip`` on the command line, in a `virtualenv`:

.. code:: shell

   pip install https://github.com/matz-e/sparkmanager/tarball/master

or for the current user:

.. code:: shell

   pip install --user https://github.com/matz-e/sparkmanager/tarball/master

Usage
-----

The module itself acts as a mediator to Spark:

.. code:: python

   import sparkmanager as sm

   # Create a new application
   sm.create("My fancy name",
             [("spark.executor.cores", 4), ("spark.executor.memory", "8g")])

   data = sm.spark.range(5)
   # Will show up in the UI with the name "broadcasting some data"
   with sm.jobgroup("broadcasting some data"):
       data = sm.broadcast(data.collect())

The Spark session can be accessed via ``sm.spark``, the Spark context via
``sm.sc``. Both attributes are instantiated once the ``create`` method is
called, with the option to call unambiguous methods from both directly via
the :py:class:`SparkManager` object:

.. code:: python

   # The following two calls are equivalent
   c = sm.parallelize(range(5))
   d = sm.sc.parallelize(range(5))
   assert c.collect() == d.collect()

Cluster support scripts
-----------------------

.. note::

   Scripts to run on the cluster are still somewhat experimental and should
   be used with caution!

Environment setup
~~~~~~~~~~~~~~~~~

To create a self-contained Spark environment, the script provided in
``examples/env.sh`` can be used. It is currently tuned to the requirements of
the `bbpviz` cluster.  A usage example:

.. code:: shell

   SPARK_ROOT=/path/to/my/spark/installation SM_WORKDIR=/path/to/a/work/directory examples/env.sh

The working directory will contain:

* A Python virtual environment
* A basic Spark configuration pointing to directories within the working
  directory
* An environment script to establish the setup

To use the resulting working environment:

.. code:: shell

   . /path/to/a/work/directory/env.sh

Spark deployment on allocations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Within a cluster allocation, the script ``sm_cluster`` can be used to start
a Spark cluster.  The script will be automatically installed by `pip`.  To
use it, pass either a working directory containing an environment or
specify them separately:

.. code:: shell

   sm_cluster startup $WORKDIR
   sm_cluster startup $WORKDIR /path/to/some/env.sh

Similar, to stop a cluster (not necessary with slurm):

.. code:: shell

   sm_cluster shutdown $WORKDIR
   sm_cluster shutdown $WORKDIR /path/to/some/env.sh

Spark applications then can connect to a master found via:

.. code:: shell

   cat $WORKDIR/spark_master

TL;DR on BlueBrain 5
~~~~~~~~~~~~~~~~~~~~

Setup a Spark environment in your current shell, and point `WORKDIR` to a
shared directory. `SPARK_HOME` needs to be in your environment and point to
your Spark installation.  By default, only a file with the Spark master and
the cluster launch script will be copied to `WORKDIR`. Then submit a
cluster with:

.. code:: shell

   sbatch -A proj16 -t 24:00:00 -N4 --exclusive -C nvme $(which sm_cluster) startup $WORKDIR
