from setuptools import find_packages
from setuptools import setup


def get_lines(filename):
    with open(filename, "r") as f:
        return [line.strip() for line in f.readlines()]


install_requires = get_lines("requirements.txt")
dev_requires = get_lines("requirements-dev.txt")

setup(
    name="fcredis",
    version='0.0.1',
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
    install_requires=install_requires,
    extras_require={"test": dev_requires}
)
