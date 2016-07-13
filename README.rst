Documentation
=============

Reports is a collection of utilities for generating OpenProcurement
billing reports.

Building
--------

Use following commands to build :

``python bootstrap.py``

``bin/buildout -N``

Usage
------

Threre are four utilities for renerating report : **bids**,
**invioces**, **refund**, **tenders**. **init** script used to
initialize database. **zip** creates encrypted zip archives.

General options for all utilities:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    Optional arguments:
      -h, --help            show help message and exit

``bids`` and ``invoices`` usage
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    Usage:

      -c CONFIG, --config CONFIG
                            Path to config file. Required
      -b BROKER, --broker BROKER
                            Broker name. Required
      -p PERIOD [PERIOD ...], --period PERIOD [PERIOD ...]
                            Specifies period for billing report. By default report
                            will be generated from all database
      -t TIMEZONE, --timezone TIMEZONE
                            Timezone. Default "Europe/Kiev"

``tenders`` and ``refunds`` usage
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    Usage:
    Optional arguments:
      --kind Kind           Kind filtering functionality. Usage: --kind <include,
                            exclude, one>=<kinds>
      --status status       Tenders statuses filtering functionality. Usage:
                            --status <include, exclude, one>=<statuses>
      -i IGNORE, --ignore IGNORE
                            File with ids that should be skipped

    Report:
      Report parameters

      -c CONFIG, --config CONFIG
                            Path to config file. Required
      -b BROKER, --broker BROKER
                            Broker name. Required
      -p PERIOD [PERIOD ...], --period PERIOD [PERIOD ...]
                            Specifies period for billing report. By default report
                            will be generated from all database
      -t TIMEZONE, --timezone TIMEZONE
                            Timezone. Default "Europe/Kiev"

Examples:

Run script to generate report to broker test with period that starts at
2016-01-01 and ands at 2016-02-01:

::

    bin/bids -b test -p 2016-01-01 2016-02-01:

Run script with changed default timezone.

::

    bin/bids -b test -p 2016-01-01 2016-02-01 -t Europe/Amsterdam

Run script with but scip ids specified in the ignore.txt file.

::

    bin/tenders -b test -p 2015-01-01 2015-02-01 -i ignore.txt

To filter kinds use ``include``, ``exclude`` or ``one``.

::

    bin/tenders -b test --kind include=other[exclude=general][one=general]

Report documents will be placed to ``var/reports/`` directory.
