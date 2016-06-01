from setuptools import setup

install_requires = [
    'couchdb>=1.0.1',
    'dateparser>=0.3.4',
    'pbkdf2',
    'requests',
    'requests_cache',
    'pytz',
    'iso8601',
    'pyminizip',
    'arrow',
]


setup(
    name='reports',
    version='0.0.1',
    packages=[
        'reports',
    ],
    entry_points={
        'console_scripts': [
            'bids = reports.utilities.bids:run',
            'tenders = reports.utilities.tenders:run',
            'refunds = reports.utilities.refunds:run',
            'invoices = reports.utilities.invoices:run',
            'init = reports.db_init:run',
        ]
    },
    install_requires=install_requires
)
