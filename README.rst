=======
soluble
=======

.. image:: https://img.shields.io/badge/made%20with-pop-teal
   :alt: Made with pop, a Python implementation of Plugin Oriented Programming
   :target: https://pop.readthedocs.io/

.. image:: https://img.shields.io/badge/made%20with-python-yellow
   :alt: Made with Python
   :target: https://www.python.org/

Soluble is a tool for setting up, managing, and tearing down ephemeral Salt minions on remote systems u
sing a streamlined Python-based approach. It simplifies the deployment of temporary nodes that can
execute Salt commands and clean up afterward, making it ideal for transient infrastructure needs.

About
=====

Soluble is designed aims to streamline the deployment of ephemeral nodes with Salt leveraging `salt-ssh`
for setting up and tearing down temporary Salt minions, allowing users to execute Salt commands on these
minions before safely removing them. The entire process is managed by a Python script, ensuring ease of use,
flexibility, and integration with existing Python-based infrastructure.

What is POP?
------------

This project is built with `pop <https://pop.readthedocs.io/>`__, a Python-based implementation of *Plugin Oriented Programming (POP)*. POP seeks to bring together concepts and wisdom from the history of computing in new ways to solve modern computing problems.

For more information:

* `Intro to Plugin Oriented Programming (POP) <https://pop-book.readthedocs.io/en/latest/>`__
* `pop-awesome <https://gitlab.com/vmware/pop/pop-awesome>`__
* `pop-create <https://gitlab.com/vmware/pop/pop-create/>`__

Getting Started
===============

Prerequisites
-------------

* Python 3.10+
* git *(if installing from source, or contributing to the project)*
* SaltStack installed on the master node
* `salt` and `salt-key` commands available

Installation
------------

.. note::

   If wanting to contribute to the project, and setup your local development
   environment, see the ``CONTRIBUTING.rst`` document in the source repository
   for this project.

If wanting to use ``soluble``, you can do so by either installing from PyPI or from source.

Install from PyPI
+++++++++++++++++

If package is available via PyPI, include the directions.

.. code-block:: bash

   pip install soluble

Install from source
+++++++++++++++++++

.. code-block:: bash

   # clone repo
   git clone git@<your-project-path>/soluble.git
   cd soluble

   # Setup venv
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -e .

Usage
=====

Soluble is designed to simplify the process of setting up ephemeral Salt minions, running commands,
and then cleaning up those minions. Here’s a basic usage example:

.. code-block:: bash

   # Example usage of soluble.py
   soluble -R /path/to/roster 'test.ping'

In this example:
- The `-R` flag specifies the path to the roster file for `salt-ssh`.
- The first positional argument (`test.ping`) is the Salt command to be executed on the ephemeral minions.

Examples
--------

Here are a few more examples of how you can use Soluble:

.. code-block:: bash

   # Install a package on ephemeral nodes
   soluble minion '*' 'pkg.install vim'

   # Apply a state file
   soluble '*' 'state.apply my_state'

   # Ping minions
   soluble minion '*' 'test.ping'

Roadmap
=======

Reference the `open issues <https://issues.example.com>`__ for a list of proposed features (and known issues).

The project roadmap includes:
- Expanding support for additional Salt modules and functions.
- Enhancing error handling and logging for more robust operation.
- Integration with other infrastructure management tools.

Acknowledgements
================

* `Img Shields <https://shields.io>`__ for making repository badges easy.
