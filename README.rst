Documentation
=============

Reports is a collection of utilities for generating OpenProcurement billing reports.

Building 
----------------------

Use following commands to build ::

 python bootstrap.py
 bin/buildout -N

Usage
----------------------

First of all initialize database:

     (bin/init)

Threre are four utilities for renerating report : bids, invioces, refund, tenders.

To use them run:


     (bin/<utility> -o <owner> -p <period> [optional])

where <utility> is one of [bids, invioces, refund, tenders],
<owner> - owner name (like in database) for whom report will be generated,
<period> - specifies period of billing report. If not placed, utility will generate report from all documents in database. If placed only one date, utility will generate report from this date.

Report documents will be placed to var/reports/ directory.

