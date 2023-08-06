from setuptools import find_packages
from setuptools import setup


setup(
    name="fcredis",
    version='0.0.2a',
    description='Redis API for users and allocation',
    long_description="",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    url='https://github.com/forever-am/fcredis',
    author='Alice Wang',
    author_email="alice.wang@forever-am.com",
    keywords='database, redis',
    license="GPLv3",
    packages=find_packages(),
    include_package_data=False,
    zip_safe=False,
    install_requires=[
        "redis==2.10.6",
        "rncryptor==3.2.0",
    ],
    extras_require={"test": [
        "pytest==3.6.1",
        "pytest-cov==2.5.1",
        "fakeredis==0.11.0",
    ]}
)
