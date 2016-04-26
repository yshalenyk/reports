
import sys
from setuptools import setup

install_requires = [
    'couchdbkit>=0.6.5',
    'dateparser>=0.3.4',
    'appdirs>=1.4.0',
]


setup(
    name='reports',
    version='0.0.1',
    packages=[
        'reports',
    ],
    entry_points={
        'console_scripts': [
            'bids = reports.bids:run',
            'tenders = reports.tenders:run',
            'refunds = reports.refunds:run',
            'invoices = reports.invoices:run',
        ]
    },
    install_requires=install_requires
)
