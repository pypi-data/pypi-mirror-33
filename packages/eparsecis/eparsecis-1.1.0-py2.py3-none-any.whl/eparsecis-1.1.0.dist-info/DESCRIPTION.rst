===============================
EParseCIS
===============================

.. code-block:: text

    ▓█████  ██▓███   ▄▄▄       ██▀███   ▄████▄   ██▓  ██████
    ▓█   ▀ ▓██░  ██▒▒████▄    ▓██ ▒ ██▒▒██▀ ▀█  ▓██▒▒██    ▒
    ▒███   ▓██░ ██▓▒▒██  ▀█▄  ▓██ ░▄█ ▒▒▓█    ▄ ▒██▒░ ▓██▄
    ▒▓█  ▄ ▒██▄█▓▒ ▒░██▄▄▄▄██ ▒██▀▀█▄  ▒▓▓▄ ▄██▒░██░  ▒   ██▒
    ░▒████▒▒██▒ ░  ░ ▓█   ▓██▒░██▓ ▒██▒▒ ▓███▀ ░░██░▒██████▒▒
    ░░ ▒░ ░▒▓▒░ ░  ░ ▒▒   ▓▒█░░ ▒▓ ░▒▓░░ ░▒ ▒  ░░▓  ▒ ▒▓▒ ▒ ░
     ░ ░  ░░▒ ░       ▒   ▒▒ ░  ░▒ ░ ▒░  ░  ▒    ▒ ░░ ░▒  ░ ░
       ░   ░░         ░   ▒     ░░   ░ ░         ▒ ░░  ░  ░
       ░  ░               ░  ░   ░     ░ ░       ░        ░
                                       ░

A Pythonic Approach to Parsing EPCIS Data
-----------------------------------------

The EParseCIS python package utilizes the lxml python package along with
the EPCPyYes EPCIS python package to enable the quick and easy parsing of
EPCIS data from it's native format into python EPCPyYes class instances that
can be quickly manipulated, inspected and serialized to other formats with
minimal effort.

.. image:: https://gitlab.com/serial-lab/EParseCIS/badges/master/pipeline.svg
        :target: https://gitlab.com/serial-lab/EParseCIS/commits/master

.. image:: https://gitlab.com/serial-lab/EParseCIS/badges/master/coverage.svg
        :target: https://gitlab.com/serial-lab/EParseCIS/pipelines

.. image:: https://badge.fury.io/py/quartet_epcis.svg
    :target: https://badge.fury.io/py/quartet_epcis

Note: Line-by-line code-coverage files can be found in the build artifacts.

Python lxml Parser for EPCIS Events


* Free software: GNU General Public License v3
* Documentation: https://serial-lab.gitlab.io/EParseCIS


Features
--------

* Fast-forward lxml parsing of EPCIS xml-formatted data
* Easy handling of EPCIS events as EPCPyYes python class instances as events are parsed.
* Simplifies the building of EPCIS-enabled applications.





