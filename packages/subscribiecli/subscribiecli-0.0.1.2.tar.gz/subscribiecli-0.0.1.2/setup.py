import setuptools

setuptools.setup(
    name='subscribiecli',
    version="0.0.1.2",
    author="Karma Computing",
    author_email="subscribie@karmacomputing.co.uk",
    desciption="cli utility for Subscribie",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=(
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
    ),
    install_requires=[
        'Click',
        'gitpython',
        'datetime',
        'subscribie',
    ],
    entry_points='''
        [console_scripts]
        subscribie=subscribie_cli:cli
    ''',
)
