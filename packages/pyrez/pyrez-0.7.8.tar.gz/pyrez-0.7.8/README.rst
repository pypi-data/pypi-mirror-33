=================
# PyRez
=================

`PyRez` is Python-based wrapper for `Hi-Rez <http://www.hirezstudios.com/>`_ API that supports `Smite <https://www.smitegame.com/>`_ and `Paladins <https://www.paladins.com/>`_.

Requirements
===========
- `Python <http://python.org>`_ 3.5 (or higher)
    * The following libraries are required: `requests` and `requests-aeaweb`
- `Access <https://fs12.formsite.com/HiRez/form48/secure_index.html>`_ to Hi-Rez Studios' API

Detailed documentation is in the `"docs"` directory.

Installation
===========
The easiest way to install `Py-rez` is using `pip`, Python's package manager:

::
    pip install -U pyrez


The required dependencies will be installed automatically. After that, you can use the library using `import pyrez`.

Example
===========

.. code-block:: python
    from pyrez.api import PaladinsAPI

    client = PaladinsAPI ("YOUR_DEV_ID", "YOUR_AUTH_KEY")
    godsRanks = client.getGodRanks ("FeyRazzle")

    if godsRanks is not None:
        for godRank in godsRanks:
            print (godRank.getWinratio ())
This example will print the winrate with every gods of player `FeyRazzle`.

Resources
=========

* `Documentation <http://django-reportmail.readthedocs.org/>`_
* `Github <https://github.com/hirokiky/django-reportmail/>`_
* `PyPI <http://pypi.python.org/pypi/django-reportmail>`_
