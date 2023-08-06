from setuptools import setup
from CABS import __version__

setup(
    name='cabs',
    version=__version__,
    packages=['CABS'],
    url='https://bitbucket.org/lcbio/cabsdock',
    license='MIT',
    author='Laboratory of Computational Biology',
    author_email='mkurc@cnbc.uw.edu.pl',
    install_requires=['numpy', 'matplotlib>=2.0', 'requests'],
    description='CABS in python',
    entry_points={
        'console_scripts': [
            'CABSdock = CABS.__main__:run_dock',
            'CABSflex = CABS.__main__:run_flex'
        ]
    },
    package_data={'CABS': ['data/*.dat']}
)
